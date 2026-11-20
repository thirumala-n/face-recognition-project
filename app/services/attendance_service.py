import csv
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from app.config import settings
from app.core.logging_config import logger
from app.models.student import Student
from app.models.attendance import Attendance
from app.schemas.attendance import (
    AttendanceResponse,
    RecognitionAttendanceResponse,
    DailyAttendanceSummary
)
from app.database.repositories import StudentRepository, AttendanceRepository
from app.services.face_service import face_service

class AttendanceService:
    """
    Coordinates Attendance business logic between FaceService and Database Repositories.
    Enforces daily deduplication and maintains CSV backups.
    """

    @staticmethod
    def _append_to_csv_backup(student_id: str, student_name: str, att_date: date, att_time, status: str):
        """Appends attendance record to daily CSV backup file to preserve legacy functionality."""
        try:
            date_str = att_date.strftime("%Y-%m-%d")
            time_str = att_time.strftime("%H:%M:%S")
            csv_path = settings.ATTENDANCE_CSV_DIR / f"Attendance_{date_str}.csv"

            file_exists = csv_path.exists()
            with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Id", "Name", "Date", "Time", "Status"])
                writer.writerow([student_id, student_name, date_str, time_str, status])
            logger.info(f"Appended backup record to CSV: {csv_path.name}")
        except Exception as e:
            logger.warning(f"Could not append to CSV backup: {e}")

    @classmethod
    def recognize_and_mark_attendance(
        cls,
        db: Session,
        image_bytes: bytes,
        threshold: Optional[float] = None
    ) -> RecognitionAttendanceResponse:
        """
        Processes an uploaded face snapshot, runs recognition, and records attendance.
        Prevents duplicate daily attendance.
        """
        active_threshold = threshold if threshold is not None else settings.CONFIDENCE_THRESHOLD

        # Step 1: Detect and recognize face
        recognized, student_id, distance, message = face_service.process_and_recognize(
            image_bytes=image_bytes,
            threshold=active_threshold
        )

        if not recognized or student_id is None:
            return RecognitionAttendanceResponse(
                recognized=False,
                student_id=None,
                student_name=None,
                confidence_distance=distance,
                threshold=active_threshold,
                attendance_marked=False,
                status=None,
                message=message
            )

        # Step 2: Validate student in database
        student = StudentRepository.get_by_student_id(db, student_id)
        if not student:
            return RecognitionAttendanceResponse(
                recognized=True,
                student_id=student_id,
                student_name=None,
                confidence_distance=distance,
                threshold=active_threshold,
                attendance_marked=False,
                status=None,
                message=f"Student ID '{student_id}' recognized by model but not found in student database."
            )

        # Step 3: Check for duplicate attendance today
        today = date.today()
        existing_record = AttendanceRepository.get_by_student_and_date(db, student_id, today)

        if existing_record:
            return RecognitionAttendanceResponse(
                recognized=True,
                student_id=student_id,
                student_name=student.name,
                confidence_distance=distance,
                threshold=active_threshold,
                attendance_marked=False,
                status=existing_record.status,
                message=f"Attendance already marked for today at {existing_record.attendance_time}."
            )

        # Step 4: Mark new attendance record
        now = datetime.now()
        new_attendance = Attendance(
            student_id=student_id,
            attendance_date=today,
            attendance_time=now.time(),
            status="Present"
        )
        saved_record = AttendanceRepository.create(db, new_attendance)

        # Step 5: Preserve legacy CSV backup
        cls._append_to_csv_backup(
            student_id=student.student_id,
            student_name=student.name,
            att_date=today,
            att_time=now.time(),
            status="Present"
        )

        logger.info(f"Attendance recorded for {student.student_id} ({student.name}) at {now.time()}")

        return RecognitionAttendanceResponse(
            recognized=True,
            student_id=student.student_id,
            student_name=student.name,
            confidence_distance=distance,
            threshold=active_threshold,
            attendance_marked=True,
            status="Present",
            message=f"Attendance marked successfully for {student.name}."
        )

    @staticmethod
    def get_attendance_summary_for_date(db: Session, target_date: date) -> DailyAttendanceSummary:
        """
        Compiles attendance status for all registered students for a specific date.
        """
        all_students = StudentRepository.get_all(db)
        attendance_records = AttendanceRepository.get_by_date(db, target_date)

        # Build mapping of student_id -> Attendance
        marked_map = {rec.student_id: rec for rec in attendance_records}

        response_records: List[AttendanceResponse] = []
        present_count = 0
        absent_count = 0

        for student in all_students:
            rec = marked_map.get(student.student_id)
            if rec:
                present_count += 1
                response_records.append(
                    AttendanceResponse(
                        id=rec.id,
                        student_id=student.student_id,
                        student_name=student.name,
                        attendance_date=rec.attendance_date,
                        attendance_time=rec.attendance_time,
                        status=rec.status
                    )
                )
            else:
                absent_count += 1
                response_records.append(
                    AttendanceResponse(
                        id=0,
                        student_id=student.student_id,
                        student_name=student.name,
                        attendance_date=target_date,
                        attendance_time=datetime.min.time(),
                        status="Absent"
                    )
                )

        return DailyAttendanceSummary(
            date=target_date,
            total_students=len(all_students),
            total_present=present_count,
            total_absent=absent_count,
            records=response_records
        )

    @staticmethod
    def get_student_history(db: Session, student_id: str) -> List[AttendanceResponse]:
        """Fetches all past attendance records for a single student."""
        student = StudentRepository.get_by_student_id(db, student_id)
        student_name = student.name if student else None

        records = AttendanceRepository.get_by_student_id(db, student_id)
        return [
            AttendanceResponse(
                id=rec.id,
                student_id=rec.student_id,
                student_name=student_name,
                attendance_date=rec.attendance_date,
                attendance_time=rec.attendance_time,
                status=rec.status
            )
            for rec in records
        ]

attendance_service = AttendanceService()
