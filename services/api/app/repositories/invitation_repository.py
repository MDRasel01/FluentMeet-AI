from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import OrganizationInvitation, Organization
from app.repositories.base import BaseRepository

class InvitationRepository(BaseRepository[OrganizationInvitation]):
    def __init__(self, db: AsyncSession):
        super().__init__(OrganizationInvitation, db)

    async def create_invitation(
        self,
        org_id: str,
        invited_email: str,
        role: str,
        token_hash: str,
        invited_by: str,
        expires_at: datetime
    ) -> OrganizationInvitation:
        invitation = OrganizationInvitation(
            organization_id=org_id,
            invited_email=invited_email.lower().strip(),
            role=role,
            token_hash=token_hash,
            invited_by=invited_by,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def get_by_token_hash(self, token_hash: str) -> Optional[OrganizationInvitation]:
        stmt = select(OrganizationInvitation).filter(
            OrganizationInvitation.token_hash == token_hash,
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.revoked_at.is_(None)
        )
        result = await self.db.execute(stmt)
        inv = result.scalars().first()
        if inv:
            now = datetime.now(timezone.utc)
            exp = inv.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if now > exp:
                return None
        return inv

    async def get_active_by_email_and_org(
        self,
        org_id: str,
        email: str
    ) -> Optional[OrganizationInvitation]:
        stmt = select(OrganizationInvitation).filter(
            OrganizationInvitation.organization_id == org_id,
            OrganizationInvitation.invited_email == email.lower().strip(),
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.revoked_at.is_(None)
        )
        result = await self.db.execute(stmt)
        inv = result.scalars().first()
        if inv:
            now = datetime.now(timezone.utc)
            exp = inv.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if now <= exp:
                return inv
        return None

    async def list_org_invitations(self, org_id: str) -> List[OrganizationInvitation]:
        stmt = (
            select(OrganizationInvitation)
            .filter(
                OrganizationInvitation.organization_id == org_id,
                OrganizationInvitation.accepted_at.is_(None),
                OrganizationInvitation.revoked_at.is_(None)
            )
            .order_by(OrganizationInvitation.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_accepted(self, invitation_id: str):
        inv = await self.get(invitation_id)
        if inv:
            inv.accepted_at = datetime.now(timezone.utc)
            await self.db.commit()

    async def revoke_invitation(self, invitation_id: str, org_id: str) -> bool:
        stmt = select(OrganizationInvitation).filter(
            OrganizationInvitation.id == invitation_id,
            OrganizationInvitation.organization_id == org_id
        )
        result = await self.db.execute(stmt)
        inv = result.scalars().first()
        if inv and inv.revoked_at is None and inv.accepted_at is None:
            inv.revoked_at = datetime.now(timezone.utc)
            await self.db.commit()
            return True
        return False
