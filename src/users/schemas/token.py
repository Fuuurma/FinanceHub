# users/schemas.py
from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from typing import Optional, List
from datetime import datetime
import re


class TokenObtainPairOut(BaseModel):
    refresh: str
    access: str


class TokenRefreshOut(BaseModel):
    access: str


class RegisterIn(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=150, description="Unique username"
    )
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)

    @validator("password")
    def strong_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class RegisterOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    message: str = "User successfully registered. Please log in."

    class Config:
        schema_extra = {
            "example": {
                "id": "a1b2c3d4-...",
                "username": "sergi",
                "email": "sergi@example.com",
                "first_name": "Sergi",
                "last_name": "Finance",
                "message": "User successfully registered. Please log in.",
            }
        }


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: str = Field(..., description="Computed full name")
    is_active: bool
    is_staff: bool
    date_joined: datetime
    roles: List[str] = Field(default_factory=list, description="List of role names")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "sergi",
                "email": "sergi@example.com",
                "full_name": "Sergi Finance",
                "is_active": True,
                "is_staff": False,
                "date_joined": "2025-12-25T10:00:00Z",
                "roles": ["Investor"],
            }
        }


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)

    class Config:
        schema_extra = {"example": {"first_name": "Sergi", "last_name": "Updated"}}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("New passwords do not match")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_strength(cls, v):
        # Reuse same strong password logic
        errors = []
        if not re.search(r"[A-Z]", v):
            errors.append("uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("lowercase letter")
        if not re.search(r"[0-9]", v):
            errors.append("digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]", v):
            errors.append("special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v
