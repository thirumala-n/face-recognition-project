from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

class StudentBase(BaseModel):
    student_id: str = Field(..., description="Unique alphanumeric identifier (e.g., CS101, 1001)")
    name: str = Field(..., description="Full student name (e.g., John Doe)")

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("student_id cannot be empty or blank")
        # Ensure only alphanumeric, hyphen, underscore
        if not re.match(r"^[A-Za-z0-9_-]+$", cleaned):
            raise ValueError("student_id must contain only letters, numbers, hyphens, or underscores")
        return cleaned

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("name cannot be empty or blank")
        # Allow letters, spaces, dots, hyphens
        if not re.match(r"^[A-Za-z\s.\-]+$", cleaned):
            raise ValueError("name must contain only alphabetical characters, spaces, hyphens, or dots")
        return cleaned

class StudentCreate(StudentBase):
    """Schema for POST /api/v1/students request body."""
    pass

class StudentResponse(StudentBase):
    """Schema for Student responses (DTO)."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StudentDeleteResponse(BaseModel):
    message: str
    student_id: str
    deleted_images_count: int
