import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import verify_password
from app.core.jwt import generate_opaque_token, hash_token
from app.core.permissions import (
    OrgRole,
    OrgPermission,
    has_org_permission,
    can_manage_target_role,
)
from app.models.base import (
    Organization,
    OrganizationMember,
    OrganizationSettings,
    OrganizationInvitation,
    User,
    AuditLog,
)
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import email_service

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\-]+', '-', text)
    return text.strip('-')[:100]

class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.inv_repo = InvitationRepository(db)
        self.user_repo = UserRepository(db)

    async def log_audit(
        self,
        action: str,
        actor_id: str,
        organization_id: Optional[str] = None,
        target_entity: Optional[str] = None,
        details: Optional[dict] = None
    ):
        audit = AuditLog(
            action=action,
            actor_id=actor_id,
            organization_id=organization_id,
            target_entity=target_entity,
            details=details,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(audit)
        await self.db.commit()

    async def create_organization(
        self,
        name: str,
        creator_id: str,
        custom_slug: Optional[str] = None,
        org_type: str = "team",
        timezone_str: str = "UTC",
        default_language: str = "English"
    ) -> Organization:
        base_slug = slugify(custom_slug or name)
        slug = base_slug
        existing = await self.org_repo.get_by_slug(slug)
        if existing:
            slug = f"{base_slug}-{str(uuid.uuid4())[:6]}"

        org = await self.org_repo.create_organization_with_owner(
            name=name,
            slug=slug,
            creator_id=creator_id,
            org_type=org_type,
            timezone_str=timezone_str,
            default_language=default_language,
        )

        await self.log_audit(
            action="organization.created",
            actor_id=creator_id,
            organization_id=org.id,
            target_entity=org.name,
        )
        return org

    async def list_user_organizations(self, user_id: str) -> List[Tuple[Organization, str]]:
        return await self.org_repo.get_user_organizations(user_id)

    async def get_organization(self, org_id: str, user_id: str) -> Tuple[Organization, str]:
        member = await self.org_repo.get_member(org_id, user_id)
        if not member or member.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this organization."
            )
        org = await self.org_repo.get_with_settings(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found."
            )
        return org, member.role

    async def update_organization_settings(
        self,
        org_id: str,
        actor_id: str,
        name: Optional[str] = None,
        org_type: Optional[str] = None,
        timezone_str: Optional[str] = None,
        default_language: Optional[str] = None,
        allow_manager_invites: Optional[bool] = None,
        require_2fa: Optional[bool] = None,
        enforce_recording_consent: Optional[bool] = None
    ) -> Organization:
        member = await self.org_repo.get_member(org_id, actor_id)
        if not member or not has_org_permission(member.role, OrgPermission.EDIT_ORGANIZATION_SETTINGS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit organization settings."
            )

        org = await self.org_repo.get_with_settings(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

        now = datetime.now(timezone.utc)
        if name:
            org.name = name
        if org_type:
            org.org_type = org_type
        if timezone_str:
            org.timezone = timezone_str
        if default_language:
            org.default_language = default_language
        org.updated_at = now

        if org.settings:
            if allow_manager_invites is not None:
                org.settings.allow_manager_invites = allow_manager_invites
            if require_2fa is not None:
                org.settings.require_2fa = require_2fa
            if enforce_recording_consent is not None:
                org.settings.enforce_recording_consent = enforce_recording_consent
            org.settings.updated_at = now

        await self.db.commit()
        await self.db.refresh(org)

        await self.log_audit(
            action="organization.settings_updated",
            actor_id=actor_id,
            organization_id=org.id,
        )
        return org

    async def send_invitation(
        self,
        org_id: str,
        actor_id: str,
        invited_email: str,
        target_role: str = "member"
    ) -> OrganizationInvitation:
        member = await self.org_repo.get_member(org_id, actor_id)
        if not member or not has_org_permission(member.role, OrgPermission.INVITE_MEMBERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to invite members."
            )

        org = await self.org_repo.get_with_settings(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

        # If actor is manager, check if organization allows manager invites
        if member.role == "manager" and org.settings and not org.settings.allow_manager_invites:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers are not permitted to invite members in this organization."
            )

        # Role escalation guard: Actor cannot invite someone with equal or higher role than themselves
        if not can_manage_target_role(member.role, target_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot assign role '{target_role}' which is equal to or higher than your own."
            )

        invited_email_clean = invited_email.lower().strip()

        # Check if already a member
        existing_user = await self.user_repo.get_by_email(invited_email_clean)
        if existing_user:
            existing_mem = await self.org_repo.get_member(org_id, existing_user.id)
            if existing_mem and existing_mem.status == "active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This user is already an active member of the organization."
                )

        # Prevent duplicate active invitation
        dup_inv = await self.inv_repo.get_active_by_email_and_org(org_id, invited_email_clean)
        if dup_inv:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active invitation is already pending for this email address."
            )

        actor_user = await self.user_repo.get(actor_id)
        inviter_name = actor_user.full_name if actor_user else "A team member"

        # Generate 7-day single-use opaque token
        raw_token = generate_opaque_token(32)
        token_hash = hash_token(raw_token)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)

        invitation = await self.inv_repo.create_invitation(
            org_id=org_id,
            invited_email=invited_email_clean,
            role=target_role,
            token_hash=token_hash,
            invited_by=actor_id,
            expires_at=expires_at,
        )

        # Send invitation email
        await email_service.send_organization_invitation(
            to_email=invited_email_clean,
            org_name=org.name,
            inviter_name=inviter_name,
            role=target_role,
            raw_token=raw_token,
        )

        await self.log_audit(
            action="organization.invitation_sent",
            actor_id=actor_id,
            organization_id=org.id,
            target_entity=invited_email_clean,
            details={"role": target_role},
        )
        return invitation

    async def accept_invitation(self, raw_token: str, user_id: str) -> OrganizationMember:
        token_hash = hash_token(raw_token)
        inv = await self.inv_repo.get_by_token_hash(token_hash)
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invitation token."
            )

        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # Strict security rule: Authenticated email must match invited email!
        if user.email.lower().strip() != inv.invited_email.lower().strip():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This invitation was sent to '{inv.invited_email}'. You are signed in as '{user.email}'."
            )

        # Check if already a member
        existing_mem = await self.org_repo.get_member(inv.organization_id, user_id)
        now = datetime.now(timezone.utc)
        if existing_mem:
            existing_mem.status = "active"
            existing_mem.role = inv.role
            existing_mem.updated_at = now
            member = existing_mem
        else:
            member = OrganizationMember(
                organization_id=inv.organization_id,
                user_id=user_id,
                role=inv.role,
                status="active",
                joined_at=now,
                created_at=now,
                updated_at=now,
            )
            self.db.add(member)

        await self.inv_repo.mark_accepted(inv.id)
        await self.db.commit()
        await self.db.refresh(member)

        await self.log_audit(
            action="organization.invitation_accepted",
            actor_id=user_id,
            organization_id=inv.organization_id,
            details={"role": inv.role},
        )
        return member

    async def list_members(self, org_id: str, actor_id: str) -> List[Dict[str, Any]]:
        actor_mem = await self.org_repo.get_member(org_id, actor_id)
        if not actor_mem or actor_mem.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this organization's members."
            )

        members = await self.org_repo.list_members(org_id)
        return [
            {
                "id": m.id,
                "user_id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": m.role,
                "status": m.status,
                "joined_at": m.joined_at,
            }
            for m, u in members
        ]

    async def update_member_role(
        self,
        org_id: str,
        actor_id: str,
        target_user_id: str,
        new_role: str
    ) -> OrganizationMember:
        actor_mem = await self.org_repo.get_member(org_id, actor_id)
        if not actor_mem or not has_org_permission(actor_mem.role, OrgPermission.CHANGE_MEMBER_ROLES):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to change member roles."
            )

        target_mem = await self.org_repo.get_member(org_id, target_user_id)
        if not target_mem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in organization.")

        # Protection: Owner role cannot be changed via update_member_role (must use transfer_ownership)
        if target_mem.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change Owner role directly. Please use ownership transfer."
            )

        # Privilege escalation check: Actor cannot grant a role equal or higher than their own
        if not can_manage_target_role(actor_mem.role, new_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot assign role '{new_role}' which is equal to or higher than your own."
            )

        # Actor cannot manage someone whose current role is equal or higher than actor's own
        if not can_manage_target_role(actor_mem.role, target_mem.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot modify the role of someone whose rank is equal to or higher than your own."
            )

        updated = await self.org_repo.update_member_role(org_id, target_user_id, new_role)
        target_user = await self.user_repo.get(target_user_id)
        org = await self.org_repo.get(org_id)
        if target_user and org:
            await email_service.send_role_changed_notification(target_user.email, org.name, new_role)

        await self.log_audit(
            action="organization.member_role_changed",
            actor_id=actor_id,
            organization_id=org_id,
            target_entity=target_user_id,
            details={"old_role": target_mem.role, "new_role": new_role},
        )
        return updated

    async def remove_member(
        self,
        org_id: str,
        actor_id: str,
        target_user_id: str
    ) -> bool:
        actor_mem = await self.org_repo.get_member(org_id, actor_id)
        if not actor_mem or not has_org_permission(actor_mem.role, OrgPermission.REMOVE_MEMBERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to remove members."
            )

        target_mem = await self.org_repo.get_member(org_id, target_user_id)
        if not target_mem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

        if target_mem.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The organization Owner cannot be removed. Transfer ownership first."
            )

        if not can_manage_target_role(actor_mem.role, target_mem.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot remove a member with rank equal to or higher than your own."
            )

        success = await self.org_repo.remove_member(org_id, target_user_id)
        if success:
            await self.log_audit(
                action="organization.member_removed",
                actor_id=actor_id,
                organization_id=org_id,
                target_entity=target_user_id,
            )
        return success

    async def transfer_ownership(
        self,
        org_id: str,
        current_owner_id: str,
        new_owner_user_id: str,
        owner_password: str
    ) -> bool:
        current_owner = await self.user_repo.get(current_owner_id)
        if not current_owner or not verify_password(owner_password, current_owner.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password for ownership transfer confirmation."
            )

        cur_mem = await self.org_repo.get_member(org_id, current_owner_id)
        if not cur_mem or cur_mem.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the current Owner can transfer organization ownership."
            )

        new_mem = await self.org_repo.get_member(org_id, new_owner_user_id)
        if not new_mem or new_mem.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New owner must be an active member of this organization."
            )

        success = await self.org_repo.transfer_ownership(org_id, current_owner_id, new_owner_user_id)
        if success:
            await self.log_audit(
                action="organization.ownership_transferred",
                actor_id=current_owner_id,
                organization_id=org_id,
                target_entity=new_owner_user_id,
            )
        return success

    async def delete_organization(self, org_id: str, actor_id: str) -> bool:
        actor_mem = await self.org_repo.get_member(org_id, actor_id)
        if not actor_mem or actor_mem.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the Owner can delete the organization."
            )

        org = await self.org_repo.get(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

        await self.org_repo.delete(org_id)
        await self.log_audit(
            action="organization.deleted",
            actor_id=actor_id,
            target_entity=org_id,
        )
        return True
