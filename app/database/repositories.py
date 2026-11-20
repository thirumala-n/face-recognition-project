from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.user import User

class StudentRepository:
    """
    Data Access Object (DAO) for Student entities.
    Equivalent to Spring Data JPA's StudentRepository interface.
    """

    @staticmethod
    def get_by_student_id(db: Session, student_id: str) -> Optional[Student]:
        statement = select(Student).where(Student.student_id == student_id)
        return db.scalar(statement)

    @staticmethod
    def get_by_id(db: Session, id: int) -> Optional[Student]:
        statement = select(Student).where(Student.id == id)
        return db.scalar(statement)

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 500) -> List[Student]:
        statement = select(Student).offset(skip).limit(limit).order_by(Student.id.asc())
        return list(db.scalars(statement).all())

    @staticmethod
    def create(db: Session, student: Student) -> Student:
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def delete(db: Session, student: Student) -> None:
        db.delete(student)
        db.commit()


class AttendanceRepository:
    """
    Data Access Object (DAO) for Attendance records.
    Equivalent to AttendanceRepository in Spring Boot.
    """

    @staticmethod
    def get_by_student_and_date(db: Session, student_id: str, att_date: date) -> Optional[Attendance]:
        statement = select(Attendance).where(
            Attendance.student_id == student_id,
            Attendance.attendance_date == att_date
        )
        return db.scalar(statement)

    @staticmethod
    def create(db: Session, attendance: Attendance) -> Attendance:
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def get_by_date(db: Session, att_date: date) -> List[Attendance]:
        statement = select(Attendance).where(
            Attendance.attendance_date == att_date
        ).order_by(Attendance.attendance_time.asc())
        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_student_id(db: Session, student_id: str) -> List[Attendance]:
        statement = select(Attendance).where(
            Attendance.student_id == student_id
        ).order_by(Attendance.attendance_date.desc(), Attendance.attendance_time.desc())
        return list(db.scalars(statement).all())


class UserRepository:
    """
    Data Access Object (DAO) for authenticated Users.
    """

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        return db.scalar(statement)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email.strip().lower())
        return db.scalar(statement)

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username.strip().lower())
        return db.scalar(statement)

    @staticmethod
    def get_by_email_or_username(db: Session, identifier: str) -> Optional[User]:
        clean_id = identifier.strip().lower()
        statement = select(User).where(
            or_(User.email == clean_id, User.username == clean_id)
        )
        return db.scalar(statement)

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
