from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    native_language: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    job_title: Optional[str] = None
    english_learning_goal: Optional[str] = None
    target_speaking_score: Optional[int] = None

class EmailChangeRequest(BaseModel):
    new_email: EmailStr
    password: str

class AccountDeactivateRequest(BaseModel):
    password: str
    reason: Optional[str] = None

class UserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    native_language: Optional[str]
    role: str
    status: str
    is_active: bool
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    timezone: str
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    job_title: Optional[str] = None
    english_learning_goal: Optional[str] = None
    target_speaking_score: Optional[int] = None
    created_at: datetime

