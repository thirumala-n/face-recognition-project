from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Attendance(Base):
    """
    SQLAlchemy ORM Model representing an Attendance Record.
    Enforces a unique constraint on (student_id, attendance_date)
    so duplicate attendance cannot be inserted on the same day.
    """
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_id = Column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    attendance_date = Column(Date, nullable=False, index=True)
    attendance_time = Column(Time, nullable=False)
    status = Column(String(20), nullable=False, default="Present")  # "Present" or "Absent"

    # Relationship back to Student
    student = relationship("Student", back_populates="attendances")

    # Enforce one attendance record per student per calendar date
    __table_args__ = (
        UniqueConstraint("student_id", "attendance_date", name="uq_student_daily_attendance"),
    )

    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, student_id='{self.student_id}', date={self.attendance_date}, status='{self.status}')>"
