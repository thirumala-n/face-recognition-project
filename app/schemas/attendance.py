from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class AttendanceBase(BaseModel):
    student_id: str
    attendance_date: date
    attendance_time: time
    status: str = Field(default="Present", description="Attendance status: Present or Absent")

class AttendanceCreate(BaseModel):
    student_id: str
    attendance_date: Optional[date] = None
    attendance_time: Optional[time] = None
    status: str = "Present"

class AttendanceResponse(BaseModel):
    """Schema for individual attendance record."""
    id: int
    student_id: str
    student_name: Optional[str] = None
    attendance_date: date
    attendance_time: time
    status: str

    model_config = ConfigDict(from_attributes=True)

class RecognitionAttendanceResponse(BaseModel):
    """
    Response schema for POST /api/v1/attendance/recognize.
    Communicates recognition outcome, LBPH distance, and attendance status.
    """
    recognized: bool
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    confidence_distance: Optional[float] = Field(
        None,
        description="LBPH Chi-square distance (lower is closer match, 0 is exact match)"
    )
    threshold: float
    attendance_marked: bool
    status: Optional[str] = None
    message: str

class DailyAttendanceSummary(BaseModel):
    date: date
    total_students: int
    total_present: int
    total_absent: int
    records: list[AttendanceResponse]
