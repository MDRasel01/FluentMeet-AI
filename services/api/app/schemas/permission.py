from typing import List, Optional
from pydantic import BaseModel

class UserPermissionsResponse(BaseModel):
    user_id: str
    platform_role: str
    is_super_admin: bool
    is_support_admin: bool

class OrgPermissionsResponse(BaseModel):
    organization_id: str
    role: str
    permissions: List[str]
    can_invite: bool
    can_manage_roles: bool
    can_delete_org: bool

