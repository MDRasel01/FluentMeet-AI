from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User
from app.schemas.organization import (
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
    OrganizationSettingsUpdateRequest,
    OrganizationMemberRoleUpdate,
    OwnershipTransferRequest,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationMemberResponse,
    OrganizationSettingsResponse,
)
from app.schemas.common import ApiResponse
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("", response_model=ApiResponse[OrganizationResponse], status_code=status.HTTP_201_CREATED)
async def create_organization(
    req: OrganizationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    org = await service.create_organization(
        name=req.name,
        creator_id=current_user.id,
        custom_slug=req.slug,
        org_type=req.org_type or "team",
        timezone_str=req.timezone or "UTC",
        default_language=req.default_language or "English",
    )
    resp = OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        org_type=org.org_type,
        timezone=org.timezone,
        default_language=org.default_language,
        seat_limit=org.seat_limit,
        retention_days=org.retention_days,
        my_role="owner",
        created_at=org.created_at,
    )
    return ApiResponse.ok_response(data=resp, message="Organization created successfully.")

@router.get("", response_model=ApiResponse[List[OrganizationResponse]])
async def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    org_list = await service.list_user_organizations(current_user.id)
    resp = [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            org_type=org.org_type,
            timezone=org.timezone,
            default_language=org.default_language,
            seat_limit=org.seat_limit,
            retention_days=org.retention_days,
            my_role=role,
            created_at=org.created_at,
        )
        for org, role in org_list
    ]
    return ApiResponse.ok_response(data=resp)

@router.get("/{org_id}", response_model=ApiResponse[OrganizationDetailResponse])
async def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    org, role = await service.get_organization(org_id, current_user.id)
    members = await service.list_members(org_id, current_user.id)
    settings_resp = None
    if org.settings:
        settings_resp = OrganizationSettingsResponse(
            allow_manager_invites=org.settings.allow_manager_invites,
            require_2fa=org.settings.require_2fa,
            enforce_recording_consent=org.settings.enforce_recording_consent,
        )
    resp = OrganizationDetailResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        org_type=org.org_type,
        timezone=org.timezone,
        default_language=org.default_language,
        seat_limit=org.seat_limit,
        retention_days=org.retention_days,
        my_role=role,
        created_at=org.created_at,
        settings=settings_resp,
        member_count=len(members),
    )
    return ApiResponse.ok_response(data=resp)

@router.patch("/{org_id}", response_model=ApiResponse[OrganizationResponse])
async def update_organization(
    org_id: str,
    req: OrganizationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    org = await service.update_organization_settings(
        org_id=org_id,
        actor_id=current_user.id,
        name=req.name,
        org_type=req.org_type,
        timezone_str=req.timezone,
        default_language=req.default_language,
    )
    _, role = await service.get_organization(org_id, current_user.id)
    resp = OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        org_type=org.org_type,
        timezone=org.timezone,
        default_language=org.default_language,
        seat_limit=org.seat_limit,
        retention_days=org.retention_days,
        my_role=role,
        created_at=org.created_at,
    )
    return ApiResponse.ok_response(data=resp, message="Organization updated successfully.")

@router.delete("/{org_id}", response_model=ApiResponse[bool])
async def delete_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    success = await service.delete_organization(org_id, current_user.id)
    return ApiResponse.ok_response(data=success, message="Organization deleted successfully.")

# Members Management
@router.get("/{org_id}/members", response_model=ApiResponse[List[OrganizationMemberResponse]])
async def list_members(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    members = await service.list_members(org_id, current_user.id)
    resp = [OrganizationMemberResponse(**m) for m in members]
    return ApiResponse.ok_response(data=resp)

@router.patch("/{org_id}/members/{target_user_id}", response_model=ApiResponse[OrganizationMemberResponse])
async def update_member_role(
    org_id: str,
    target_user_id: str,
    req: OrganizationMemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    updated = await service.update_member_role(org_id, current_user.id, target_user_id, req.role)
    members = await service.list_members(org_id, current_user.id)
    target_info = next(m for m in members if m["user_id"] == target_user_id)
    resp = OrganizationMemberResponse(**target_info)
    return ApiResponse.ok_response(data=resp, message="Member role updated successfully.")

@router.delete("/{org_id}/members/{target_user_id}", response_model=ApiResponse[bool])
async def remove_member(
    org_id: str,
    target_user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    success = await service.remove_member(org_id, current_user.id, target_user_id)
    return ApiResponse.ok_response(data=success, message="Member removed from organization.")

@router.post("/{org_id}/transfer-ownership", response_model=ApiResponse[bool])
async def transfer_ownership(
    org_id: str,
    req: OwnershipTransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    success = await service.transfer_ownership(
        org_id=org_id,
        current_owner_id=current_user.id,
        new_owner_user_id=req.new_owner_user_id,
        owner_password=req.password,
    )
    return ApiResponse.ok_response(data=success, message="Organization ownership transferred successfully.")

