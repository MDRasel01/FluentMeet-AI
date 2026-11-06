from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class InvitationCreateRequest(BaseModel):
    invited_email: EmailStr
    role: str = Field("member", description="admin, manager, or member")

class InvitationAcceptRequest(BaseModel):
    token: str = Field(..., min_length=10)

class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    organization_name: Optional[str] = None
    invited_email: str
    role: str
    invited_by_name: Optional[str] = None
    expires_at: datetime
    created_at: datetime
    is_expired: bool = False
