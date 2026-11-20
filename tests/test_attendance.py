import pytest
import sqlalchemy.exc
from datetime import date, time
from io import BytesIO
from fastapi import status
from app.models.student import Student
from app.models.attendance import Attendance
from app.database.repositories import AttendanceRepository


def test_attendance_database_crud(db_session):
    """Verifies direct MySQL persistence: create + read of an attendance record."""
    student = Student(student_id="STU201", name="Sarah Connor")
    db_session.add(student)
    db_session.commit()

    today = date.today()
    att = Attendance(
        student_id="STU201",
        attendance_date=today,
        attendance_time=time(9, 15, 0),
        status="Present"
    )
    db_session.add(att)
    db_session.commit()

    fetched = AttendanceRepository.get_by_student_and_date(db_session, "STU201", today)
    assert fetched is not None
    assert fetched.student_id == "STU201"
    assert fetched.status == "Present"


def test_duplicate_daily_attendance_db_constraint(db_session):
    """
    Verifies the MySQL UNIQUE constraint (student_id, attendance_date)
    rejects a second attendance row for the same student on the same day.
    """
    student = Student(student_id="STU202", name="John Connor")
    db_session.add(student)
    db_session.commit()

    today = date.today()
    att1 = Attendance(
        student_id="STU202",
        attendance_date=today,
        attendance_time=time(9, 0, 0),
        status="Present"
    )
    db_session.add(att1)
    db_session.commit()

    att2 = Attendance(
        student_id="STU202",
        attendance_date=today,
        attendance_time=time(10, 0, 0),
        status="Present"
    )
    db_session.add(att2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_get_today_attendance_api(client):
    """GET /api/v1/attendance/today returns a valid summary structure."""
    client.post("/api/v1/students", json={"student_id": "STU203", "name": "Kyle Reese"})

    response = client.get("/api/v1/attendance/today")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "date" in data
    assert "total_students" in data
    assert "total_present" in data
    assert "total_absent" in data
    assert "records" in data


def test_get_student_attendance_history_api(client, db_session):
    """GET /api/v1/attendance/student/{id} returns historical records."""
    client.post("/api/v1/students", json={"student_id": "STU204", "name": "Ellen Ripley"})

    att1 = Attendance(
        student_id="STU204",
        attendance_date=date(2026, 1, 10),
        attendance_time=time(8, 30, 0),
        status="Present"
    )
    att2 = Attendance(
        student_id="STU204",
        attendance_date=date(2026, 1, 11),
        attendance_time=time(8, 45, 0),
        status="Present"
    )
    db_session.add_all([att1, att2])
    db_session.commit()

    response = client.get("/api/v1/attendance/student/STU204")
    assert response.status_code == status.HTTP_200_OK
    records = response.json()
    assert len(records) == 2
    dates = [r["attendance_date"] for r in records]
    assert "2026-01-10" in dates
    assert "2026-01-11" in dates


def test_get_attendance_by_specific_date(client):
    """GET /api/v1/attendance/date/{date} works with a valid date string."""
    response = client.get("/api/v1/attendance/date/2026-01-15")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["date"] == "2026-01-15"


def test_recognize_upload_invalid_file_type(client):
    """Uploading a text/plain file returns HTTP 415 Unsupported Media Type."""
    fake_txt = BytesIO(b"This is not an image at all")
    response = client.post(
        "/api/v1/attendance/recognize",
        files={"file": ("test.txt", fake_txt, "text/plain")}
    )
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_recognize_upload_empty_image(client):
    """Uploading an empty file returns HTTP 400 Bad Request."""
    empty = BytesIO(b"")
    response = client.post(
        "/api/v1/attendance/recognize",
        files={"file": ("empty.jpg", empty, "image/jpeg")}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_recognize_upload_blank_image_no_face(client, dummy_blank_image_bytes):
    """
    A plain black image produces recognized=False with an informative message.
    Model may not be loaded in test environment — both paths return recognized=False.
    """
    file_payload = BytesIO(dummy_blank_image_bytes)
    response = client.post(
        "/api/v1/attendance/recognize",
        files={"file": ("noface.jpg", file_payload, "image/jpeg")}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["recognized"] is False
    assert data["attendance_marked"] is False
    # Either "No human face detected" or model-not-loaded message
    assert len(data["message"]) > 0


def test_get_nonexistent_student_attendance_history(client):
    """GET attendance history for unknown student_id returns 404."""
    response = client.get("/api/v1/attendance/student/GHOST_STUDENT_XYZ")
    assert response.status_code == status.HTTP_404_NOT_FOUND
