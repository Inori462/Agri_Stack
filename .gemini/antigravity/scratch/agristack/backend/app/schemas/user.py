from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    phone_number: str
    full_name: str
    primary_role: str
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    preferred_language: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
