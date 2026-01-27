from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from ninja import Schema
import re


class RegisterIn(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=150, description="Unique username"
    )
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    password_confirm: str = Field(..., description="Confirm your password")
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)

    @field_validator("password")
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

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
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
