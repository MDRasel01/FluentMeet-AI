from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User
from app.core.permissions import OrgRole, ORG_ROLE_PERMISSIONS
from app.schemas.permission import UserPermissionsResponse, OrgPermissionsResponse
from app.schemas.common import ApiResponse
from app.services.organization_service import OrganizationService

router = APIRouter(tags=["Permissions"])

@router.get("/permissions/me", response_model=ApiResponse[UserPermissionsResponse])
async def get_my_platform_permissions(
    current_user: User = Depends(get_current_user)
):
    resp = UserPermissionsResponse(
        user_id=current_user.id,
        platform_role=current_user.role,
        is_super_admin=current_user.role == "super_admin",
        is_support_admin=current_user.role == "support_admin",
    )
    return ApiResponse.ok_response(data=resp)

@router.get("/organizations/{org_id}/permissions/me", response_model=ApiResponse[OrgPermissionsResponse])
async def get_my_org_permissions(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    _, role_str = await service.get_organization(org_id, current_user.id)

    try:
        org_role = OrgRole(role_str)
        perms = [p.value for p in ORG_ROLE_PERMISSIONS.get(org_role, set())]
    except ValueError:
        perms = []

    resp = OrgPermissionsResponse(
        organization_id=org_id,
        role=role_str,
        permissions=perms,
        can_invite="org:invite_members" in perms,
        can_manage_roles="org:change_roles" in perms,
        can_delete_org="org:delete" in perms,
    )
    return ApiResponse.ok_response(data=resp)
