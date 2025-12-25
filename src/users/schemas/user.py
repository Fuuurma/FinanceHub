from ninja import Schema
from pydantic import Field

from datetime import datetime

from typing import List, Optional


class UserUpdateSchema(Schema):
    """User update schema (partial)"""

    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserOutSchema(Schema):
    """User output schema"""

    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    status: dict
    account_type: dict
    roles: List[dict]
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
