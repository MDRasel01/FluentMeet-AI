import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models.base import AuthSession, RefreshToken
from app.repositories.base import BaseRepository

class SessionRepository(BaseRepository[AuthSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuthSession, db)

    async def create_session(
        self,
        user_id: str,
        expires_at: datetime,
        session_name: Optional[str] = None,
        device_type: str = "desktop",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuthSession:
        now = datetime.now(timezone.utc)
        session = AuthSession(
            user_id=user_id,
            session_name=session_name or f"{device_type.capitalize()} Session",
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            last_used_at=now,
            expires_at=expires_at,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_active_session(self, session_id: str) -> Optional[AuthSession]:
        stmt = select(AuthSession).filter(
            AuthSession.id == session_id,
            AuthSession.revoked_at.is_(None)
        )
        result = await self.db.execute(stmt)
        session = result.scalars().first()
        if session:
            now = datetime.now(timezone.utc)
            exp = session.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if now > exp:
                return None
        return session

    async def list_user_sessions(self, user_id: str) -> List[AuthSession]:
        stmt = (
            select(AuthSession)
            .filter(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .order_by(AuthSession.last_used_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def touch_session(self, session_id: str):
        now = datetime.now(timezone.utc)
        stmt = (
            update(AuthSession)
            .where(AuthSession.id == session_id)
            .values(last_used_at=now)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def revoke_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        stmt = select(AuthSession).filter(AuthSession.id == session_id)
        if user_id:
            stmt = stmt.filter(AuthSession.user_id == user_id)
        result = await self.db.execute(stmt)
        session = result.scalars().first()
        if not session or session.revoked_at is not None:
            return False

        now = datetime.now(timezone.utc)
        session.revoked_at = now

        # Revoke all refresh tokens for this session
        rev_tokens = (
            update(RefreshToken)
            .where(RefreshToken.session_id == session_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.db.execute(rev_tokens)
        await self.db.commit()
        return True

    async def revoke_all_user_sessions(self, user_id: str) -> int:
        now = datetime.now(timezone.utc)
        stmt = (
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        res = await self.db.execute(stmt)

        # Revoke all refresh tokens belonging to the user's sessions
        subq = select(AuthSession.id).where(AuthSession.user_id == user_id)
        rev_tokens = (
            update(RefreshToken)
            .where(RefreshToken.session_id.in_(subq), RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.db.execute(rev_tokens)
        await self.db.commit()
        return res.rowcount

    # Refresh Token Management & Rotation
    async def create_refresh_token(
        self,
        session_id: str,
        token_hash: str,
        expires_at: datetime,
        family_id: Optional[str] = None
    ) -> RefreshToken:
        token = RefreshToken(
            session_id=session_id,
            token_hash=token_hash,
            family_id=family_id or str(uuid.uuid4()),
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def get_refresh_token_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).filter(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def revoke_token_family(self, family_id: str):
        """Used when refresh token reuse is detected to invalidate compromised family."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.db.execute(stmt)

        # Also revoke any associated session
        token_stmt = select(RefreshToken.session_id).where(RefreshToken.family_id == family_id)
        res = await self.db.execute(token_stmt)
        session_ids = [r[0] for r in res.all()]
        if session_ids:
            sess_stmt = (
                update(AuthSession)
                .where(AuthSession.id.in_(session_ids), AuthSession.revoked_at.is_(None))
                .values(revoked_at=now)
            )
            await self.db.execute(sess_stmt)

        await self.db.commit()
