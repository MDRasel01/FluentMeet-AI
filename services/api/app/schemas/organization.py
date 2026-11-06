from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    org_type: Optional[str] = "team"
    timezone: Optional[str] = "UTC"
    default_language: Optional[str] = "English"

class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    org_type: Optional[str] = None
    timezone: Optional[str] = None
    default_language: Optional[str] = None

class OrganizationSettingsUpdateRequest(BaseModel):
    allow_manager_invites: Optional[bool] = None
    require_2fa: Optional[bool] = None
    enforce_recording_consent: Optional[bool] = None

class OrganizationSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    allow_manager_invites: bool
    require_2fa: bool
    enforce_recording_consent: bool

class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    email: str
    full_name: str
    role: str
    status: str
    joined_at: datetime

class OrganizationMemberRoleUpdate(BaseModel):
    role: str = Field(..., description="Role to assign: admin, manager, member")

class OwnershipTransferRequest(BaseModel):
    new_owner_user_id: str
    password: str

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    org_type: str
    timezone: str
    default_language: str
    seat_limit: int
    retention_days: int
    my_role: Optional[str] = None
    created_at: datetime

class OrganizationDetailResponse(OrganizationResponse):
    settings: Optional[OrganizationSettingsResponse] = None
    member_count: int = 1

