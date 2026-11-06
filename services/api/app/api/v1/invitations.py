from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User
from app.schemas.invitation import (
    InvitationCreateRequest,
    InvitationAcceptRequest,
    InvitationResponse,
)
from app.schemas.organization import OrganizationMemberResponse
from app.schemas.common import ApiResponse
from app.services.organization_service import OrganizationService
from app.repositories.invitation_repository import InvitationRepository

router = APIRouter(tags=["Invitations"])

@router.post("/organizations/{org_id}/invitations", response_model=ApiResponse[InvitationResponse], status_code=status.HTTP_201_CREATED)
async def create_invitation(
    org_id: str,
    req: InvitationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    inv = await service.send_invitation(
        org_id=org_id,
        actor_id=current_user.id,
        invited_email=req.invited_email,
        target_role=req.role,
    )
    resp = InvitationResponse(
        id=inv.id,
        organization_id=inv.organization_id,
        invited_email=inv.invited_email,
        role=inv.role,
        invited_by_name=current_user.full_name,
        expires_at=inv.expires_at,
        created_at=inv.created_at,
        is_expired=False,
    )
    return ApiResponse.ok_response(data=resp, message="Invitation sent successfully.")

@router.get("/organizations/{org_id}/invitations", response_model=ApiResponse[List[InvitationResponse]])
async def list_invitations(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    # Check that caller has access to the org
    await service.get_organization(org_id, current_user.id)

    inv_repo = InvitationRepository(db)
    invitations = await inv_repo.list_org_invitations(org_id)
    now = datetime.now(timezone.utc)
    resp = []
    for inv in invitations:
        exp = inv.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        resp.append(
            InvitationResponse(
                id=inv.id,
                organization_id=inv.organization_id,
                invited_email=inv.invited_email,
                role=inv.role,
                expires_at=inv.expires_at,
                created_at=inv.created_at,
                is_expired=now > exp,
            )
        )
    return ApiResponse.ok_response(data=resp)

@router.post("/invitations/accept", response_model=ApiResponse[OrganizationMemberResponse])
async def accept_invitation(
    req: InvitationAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    member = await service.accept_invitation(raw_token=req.token, user_id=current_user.id)
    resp = OrganizationMemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=member.role,
        status=member.status,
        joined_at=member.joined_at,
    )
    return ApiResponse.ok_response(data=resp, message="You have successfully joined the organization.")

@router.post("/invitations/{invitation_id}/resend", response_model=ApiResponse[bool])
async def resend_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inv_repo = InvitationRepository(db)
    inv = await inv_repo.get(invitation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

    service = OrganizationService(db)
    # Revoke old and send fresh invitation
    await inv_repo.revoke_invitation(inv.id, inv.organization_id)
    await service.send_invitation(
        org_id=inv.organization_id,
        actor_id=current_user.id,
        invited_email=inv.invited_email,
        target_role=inv.role,
    )
    return ApiResponse.ok_response(data=True, message="Fresh invitation sent.")

@router.delete("/invitations/{invitation_id}", response_model=ApiResponse[bool])
async def revoke_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inv_repo = InvitationRepository(db)
    inv = await inv_repo.get(invitation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

    service = OrganizationService(db)
    # Verify actor is owner or admin in this organization
    _, role = await service.get_organization(inv.organization_id, current_user.id)
    if role not in ["owner", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied to revoke invitations.")

    revoked = await inv_repo.revoke_invitation(invitation_id, inv.organization_id)
    return ApiResponse.ok_response(data=revoked, message="Invitation revoked successfully.")

