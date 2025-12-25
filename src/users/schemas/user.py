from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)


class RegisterOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    message: str = "User registered successfully"


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
                "username": "tom32",
                "email": "example@example.com",
                "full_name": "Tommy Finance",
                "is_active": True,
                "is_staff": False,
                "date_joined": "2025-12-25T10:00:00Z",
                "roles": ["Investor"],
            }
        }


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    # Add more fields later if needed (e.g., preferences)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    def validate(self):
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match")
