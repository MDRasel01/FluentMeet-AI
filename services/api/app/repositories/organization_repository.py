from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from app.models.base import Organization, OrganizationMember, OrganizationSettings, User
from app.repositories.base import BaseRepository

class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: AsyncSession):
        super().__init__(Organization, db)

    async def create_organization_with_owner(
        self,
        name: str,
        slug: str,
        creator_id: str,
        org_type: str = "team",
        timezone_str: str = "UTC",
        default_language: str = "English"
    ) -> Organization:
        now = datetime.now(timezone.utc)
        org = Organization(
            name=name,
            slug=slug,
            org_type=org_type,
            timezone=timezone_str,
            default_language=default_language,
            created_at=now,
            updated_at=now,
        )
        self.db.add(org)
        await self.db.flush()

        # Add Organization Settings
        settings = OrganizationSettings(
            organization_id=org.id,
            allow_manager_invites=True,
            require_2fa=False,
            enforce_recording_consent=True,
            created_at=now,
            updated_at=now,
        )
        self.db.add(settings)

        # Creator automatically becomes the Owner
        member = OrganizationMember(
            organization_id=org.id,
            user_id=creator_id,
            role="owner",
            status="active",
            joined_at=now,
            created_at=now,
            updated_at=now,
        )
        self.db.add(member)

        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        stmt = select(Organization).filter(Organization.slug == slug.lower().strip())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_with_settings(self, org_id: str) -> Optional[Organization]:
        stmt = (
            select(Organization)
            .options(selectinload(Organization.settings))
            .filter(Organization.id == org_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_organizations(self, user_id: str) -> List[Tuple[Organization, str]]:
        """Returns list of (Organization, user_role) tuples for a given user."""
        stmt = (
            select(Organization, OrganizationMember.role)
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .filter(
                OrganizationMember.user_id == user_id,
                OrganizationMember.status == "active"
            )
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def get_member(self, org_id: str, user_id: str) -> Optional[OrganizationMember]:
        stmt = select(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_members(self, org_id: str) -> List[Tuple[OrganizationMember, User]]:
        stmt = (
            select(OrganizationMember, User)
            .join(User, OrganizationMember.user_id == User.id)
            .filter(OrganizationMember.organization_id == org_id)
            .order_by(OrganizationMember.joined_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def update_member_role(self, org_id: str, user_id: str, new_role: str) -> Optional[OrganizationMember]:
        member = await self.get_member(org_id, user_id)
        if member:
            member.role = new_role
            member.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(member)
        return member

    async def remove_member(self, org_id: str, user_id: str) -> bool:
        member = await self.get_member(org_id, user_id)
        if member:
            await self.db.delete(member)
            await self.db.commit()
            return True
        return False

    async def transfer_ownership(
        self,
        org_id: str,
        current_owner_id: str,
        new_owner_id: str
    ) -> bool:
        cur_member = await self.get_member(org_id, current_owner_id)
        new_member = await self.get_member(org_id, new_owner_id)
        if not cur_member or not new_member:
            return False
        if cur_member.role != "owner":
            return False

        now = datetime.now(timezone.utc)
        cur_member.role = "admin"
        cur_member.updated_at = now
        new_member.role = "owner"
        new_member.updated_at = now

        await self.db.commit()
        return True

