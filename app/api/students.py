import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentDeleteResponse
from app.database.repositories import StudentRepository
from app.services.training_service import training_service
from app.core.logging_config import logger

router = APIRouter()

@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student"
)
def register_student(payload: StudentCreate, db: Session = Depends(get_db)):
    """
    Registers a new student record in MySQL.
    Validates that student_id is unique.
    """
    existing = StudentRepository.get_by_student_id(db, payload.student_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with ID '{payload.student_id}' is already registered."
        )

    new_student = Student(
        student_id=payload.student_id,
        name=payload.name
    )
    saved_student = StudentRepository.create(db, new_student)
    logger.info(f"Student registered: {saved_student.student_id} - {saved_student.name}")
    return saved_student

@router.get(
    "",
    response_model=List[StudentResponse],
    summary="List all registered students"
)
def list_students(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    """Retrieves all registered students with pagination support."""
    return StudentRepository.get_all(db, skip=skip, limit=limit)

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by ID"
)
def get_student(student_id: str, db: Session = Depends(get_db)):
    """Retrieves detailed profile of a single student by student_id."""
    student = StudentRepository.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return student

@router.delete(
    "/{student_id}",
    response_model=StudentDeleteResponse,
    summary="Delete a student"
)
def delete_student(student_id: str, db: Session = Depends(get_db)):
    """
    Deletes a student record from MySQL, cascades deletion to attendance records,
    and removes their face samples from TrainingImage/.
    """
    student = StudentRepository.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )

    # Delete face training images
    deleted_images = training_service.delete_student_images(student_id)

    # Delete from database (cascades to attendance records)
    StudentRepository.delete(db, student)

    logger.info(f"Student {student_id} deleted along with {deleted_images} training images.")
    return StudentDeleteResponse(
        message=f"Student '{student_id}' successfully deleted.",
        student_id=student_id,
        deleted_images_count=deleted_images
    )

@router.post(
    "/{student_id}/images",
    summary="Upload face sample images for a student"
)
async def upload_student_images(
    student_id: str,
    files: List[UploadFile] = File(..., description="Face image files (JPG, PNG)"),
    db: Session = Depends(get_db)
):
    """
    Uploads multiple face sample photos for student enrollment.
    Detects face ROIs and saves them into the TrainingImage/ directory.
    """
    student = StudentRepository.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found. Register the student first."
        )

    image_bytes_list = []
    for file in files:
        content = await file.read()
        if content:
            image_bytes_list.append(content)

    if not image_bytes_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid image files provided."
        )

    # Offload image processing to worker thread to avoid blocking the async event loop
    saved_count = await asyncio.to_thread(
        training_service.save_student_face_samples,
        student_id=student.student_id,
        student_name=student.name,
        image_bytes_list=image_bytes_list
    )

    return {
        "student_id": student.student_id,
        "name": student.name,
        "uploaded_files": len(files),
        "saved_face_samples": saved_count,
        "message": f"Successfully enrolled {saved_count} face samples. Trigger /train to retrain the model."
    }

@router.post(
    "/train/model",
    summary="Trigger LBPH face recognition model retraining"
)
async def train_recognition_model():
    """
    Reads all face samples in TrainingImage/, trains the LBPH Face Recognizer,
    updates Trainner.yml and label_map.csv, and reloads the model in memory.
    Runs asynchronously in a background thread to keep API responsive.
    """
    success, count, students, message = await asyncio.to_thread(training_service.train_model)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

    return {
        "status": "success",
        "message": message,
        "total_images_trained": count,
        "students_trained": students
    }
