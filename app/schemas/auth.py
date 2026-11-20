from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

class UserRegister(BaseModel):
    full_name: str = Field(..., description="Full Name of the user (e.g., John Admin)")
    email: str = Field(..., description="Valid corporate or academic email address")
    username: str = Field(..., description="Unique alphanumeric handle (e.g., admin_john)")
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters")
        if not re.match(r"^[A-Za-z\s.\-]+$", cleaned):
            raise ValueError("Full name must contain only letters, spaces, hyphens, or dots")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
            raise ValueError("Invalid email format")
        return cleaned

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if len(cleaned) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r"^[a-z0-9_-]+$", cleaned):
            raise ValueError("Username must contain only lowercase letters, numbers, hyphens, or underscores")
        return cleaned

class UserLogin(BaseModel):
    email_or_username: str = Field(..., description="Email or Username")
    password: str = Field(..., description="Plaintext password")

    @field_validator("email_or_username")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Email or Username cannot be empty")
        return cleaned

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
