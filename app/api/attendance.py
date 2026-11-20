import asyncio
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.attendance import (
    RecognitionAttendanceResponse,
    DailyAttendanceSummary,
    AttendanceResponse
)
from app.services.attendance_service import attendance_service
from app.database.repositories import StudentRepository
from app.core.logging_config import logger

router = APIRouter()

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp",
    "application/octet-stream"
}

@router.post(
    "/recognize",
    response_model=RecognitionAttendanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload image, recognize face and mark attendance"
)
async def recognize_and_mark_attendance(
    file: UploadFile = File(..., description="Snapshot image containing face (JPEG or PNG)"),
    threshold: Optional[float] = Query(None, description="Optional custom LBPH confidence threshold override"),
    db: Session = Depends(get_db)
):
    """
    Accepts an uploaded image, decodes it with OpenCV, detects face ROI,
    performs LBPH recognition, matches student in MySQL, and commits attendance.
    Prevents duplicate attendance for the current calendar day.
    """
    # Validate MIME type
    if file.content_type and file.content_type.lower() not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{file.content_type}'. Must be JPEG or PNG."
        )

    image_bytes = await file.read()
    if not image_bytes or len(image_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty or too small to be a valid image."
        )

    # Offload synchronous computer vision operations to a thread pool
    # so we do NOT block the FastAPI async event loop
    result: RecognitionAttendanceResponse = await asyncio.to_thread(
        attendance_service.recognize_and_mark_attendance,
        db=db,
        image_bytes=image_bytes,
        threshold=threshold
    )

    logger.info(
        f"Recognition event: recognized={result.recognized}, "
        f"student_id={result.student_id}, marked={result.attendance_marked}, "
        f"distance={result.confidence_distance}"
    )

    return result

@router.get(
    "/today",
    response_model=DailyAttendanceSummary,
    summary="Get today's attendance summary"
)
def get_today_attendance(db: Session = Depends(get_db)):
    """Retrieves full attendance status (Present and Absent) for today."""
    today = date.today()
    return attendance_service.get_attendance_summary_for_date(db, today)

@router.get(
    "/date/{target_date}",
    response_model=DailyAttendanceSummary,
    summary="Get attendance report for a specific date (YYYY-MM-DD)"
)
def get_attendance_by_date(target_date: date, db: Session = Depends(get_db)):
    """Retrieves full attendance status for any specified historical date."""
    return attendance_service.get_attendance_summary_for_date(db, target_date)

@router.get(
    "/student/{student_id}",
    response_model=List[AttendanceResponse],
    summary="Get attendance history for a specific student"
)
def get_student_attendance_history(student_id: str, db: Session = Depends(get_db)):
    """Retrieves all historical attendance logs for a student."""
    student = StudentRepository.get_by_student_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )

    return attendance_service.get_student_history(db, student_id)
