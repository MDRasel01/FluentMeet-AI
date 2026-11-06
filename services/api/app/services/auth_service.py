import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.core.jwt import (
    create_access_token,
    generate_opaque_token,
    hash_token,
)
from app.models.base import (
    User,
    UserProfile,
    AuthSession,
    RefreshToken,
    EmailVerificationToken,
    PasswordResetToken,
    AuditLog,
    OrganizationMember,
)
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.services.email_service import email_service
from app.schemas.auth import (
    UserRegisterRequest,
    TokenResponse,
    UserProfileResponse,
)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)

    async def log_audit(
        self,
        action: str,
        actor_id: str,
        target_entity: Optional[str] = None,
        organization_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None
    ):
        audit = AuditLog(
            action=action,
            actor_id=actor_id,
            target_entity=target_entity,
            organization_id=organization_id,
            details=details,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(audit)
        await self.db.commit()

    async def register(
        self,
        payload: UserRegisterRequest,
        ip_address: Optional[str] = None
    ) -> UserProfileResponse:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists."
            )

        now = datetime.now(timezone.utc)
        user = User(
            email=payload.email.lower().strip(),
            hashed_password=get_password_hash(payload.password),
            full_name=payload.full_name.strip(),
            native_language=payload.native_language or "English",
            role="individual",
            status="pending_verification",
            is_active=True,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )
        created_user = await self.user_repo.create_user_with_profile(user)

        # Generate email verification token (valid for 30 minutes)
        raw_token = generate_opaque_token(32)
        token_hash = hash_token(raw_token)
        verif_token = EmailVerificationToken(
            user_id=created_user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=30),
            created_at=now,
        )
        self.db.add(verif_token)
        await self.db.commit()

        # Dispatch verification email
        await email_service.send_verification_email(
            to_email=created_user.email,
            full_name=created_user.full_name,
            raw_token=raw_token,
        )

        await self.log_audit(
            action="auth.registered",
            actor_id=created_user.id,
            target_entity=created_user.email,
            ip_address=ip_address,
        )

        return UserProfileResponse.model_validate(created_user)

    async def verify_email(self, raw_token: str, ip_address: Optional[str] = None) -> bool:
        t_hash = hash_token(raw_token)
        stmt = select(EmailVerificationToken).filter(
            EmailVerificationToken.token_hash == t_hash,
            EmailVerificationToken.used_at.is_(None)
        )
        result = await self.db.execute(stmt)
        token_record = result.scalars().first()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token."
            )

        now = datetime.now(timezone.utc)
        exp = token_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)

        if now > exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please request a new one."
            )

        token_record.used_at = now
        user = await self.user_repo.get(token_record.user_id)
        if user:
            user.is_verified = True
            user.status = "active"
            user.email_verified_at = now
            user.updated_at = now

        await self.db.commit()
        if user:
            await self.log_audit(
                action="auth.email_verified",
                actor_id=user.id,
                target_entity=user.email,
                ip_address=ip_address,
            )
        return True

    async def resend_verification(self, email: str) -> bool:
        user = await self.user_repo.get_by_email(email)
        # Prevent email enumeration: return success even if user not found or already verified
        if not user or user.is_verified:
            return True

        now = datetime.now(timezone.utc)
        raw_token = generate_opaque_token(32)
        token_hash = hash_token(raw_token)
        verif_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=30),
            created_at=now,
        )
        self.db.add(verif_token)
        await self.db.commit()

        await email_service.send_verification_email(
            to_email=user.email,
            full_name=user.full_name,
            raw_token=raw_token,
        )
        return True

    async def login(
        self,
        email: str,
        password: str,
        device_type: str = "desktop",
        session_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            # Generic error to prevent account enumeration
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if user.status == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is suspended. Please contact support."
            )
        if user.status == "deactivated":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Please contact support to reactivate."
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive."
            )

        now = datetime.now(timezone.utc)
        session_expiry = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Create active server-backed session
        session = await self.session_repo.create_session(
            user_id=user.id,
            expires_at=session_expiry,
            session_name=session_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Create rotating Refresh Token with family_id
        raw_refresh_token = generate_opaque_token(48)
        refresh_hash = hash_token(raw_refresh_token)
        family_id = str(uuid.uuid4())
        await self.session_repo.create_refresh_token(
            session_id=session.id,
            token_hash=refresh_hash,
            expires_at=session_expiry,
            family_id=family_id,
        )

        # Issue short-lived JWT Access Token
        access_token = create_access_token(
            user_id=user.id,
            session_id=session.id,
            email=user.email,
            platform_role=user.role,
        )

        await self.log_audit(
            action="auth.login",
            actor_id=user.id,
            target_entity=session.id,
            ip_address=ip_address,
            details={"device_type": device_type},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileResponse.model_validate(user),
        )

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        r_hash = hash_token(raw_refresh_token)
        token_record = await self.session_repo.get_refresh_token_by_hash(r_hash)

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token."
            )

        # --- TOKEN REUSE DETECTION ---
        if token_record.used_at is not None or token_record.revoked_at is not None:
            # Compromised token reuse detected! Immediately revoke the whole token family
            await self.session_repo.revoke_token_family(token_record.family_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Security violation: Refresh token reuse detected. All sessions in this chain have been revoked."
            )

        now = datetime.now(timezone.utc)
        exp = token_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)

        if now > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please login again."
            )

        # Verify parent session is still active
        session = await self.session_repo.get_active_session(token_record.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired or was revoked."
            )

        # Mark previous token as used
        token_record.used_at = now

        # Generate new rotated refresh token in the same family
        new_raw_refresh = generate_opaque_token(48)
        new_refresh_hash = hash_token(new_raw_refresh)
        new_token_record = await self.session_repo.create_refresh_token(
            session_id=session.id,
            token_hash=new_refresh_hash,
            expires_at=session.expires_at,
            family_id=token_record.family_id,
        )
        token_record.replaced_by_token_id = new_token_record.id
        await self.db.commit()

        # Touch session activity
        await self.session_repo.touch_session(session.id)

        user = await self.user_repo.get(session.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive."
            )

        access_token = create_access_token(
            user_id=user.id,
            session_id=session.id,
            email=user.email,
            platform_role=user.role,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_raw_refresh,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileResponse.model_validate(user),
        )

    async def logout(self, session_id: str, user_id: str) -> bool:
        success = await self.session_repo.revoke_session(session_id, user_id=user_id)
        if success:
            await self.log_audit(
                action="auth.logout",
                actor_id=user_id,
                target_entity=session_id,
            )
        return success

    async def logout_all(self, user_id: str) -> int:
        count = await self.session_repo.revoke_all_user_sessions(user_id)
        await self.log_audit(
            action="auth.logout_all",
            actor_id=user_id,
            details={"revoked_sessions_count": count},
        )
        return count

    async def request_password_reset(self, email: str, ip_address: Optional[str] = None) -> bool:
        user = await self.user_repo.get_by_email(email)
        # Always return generic True to avoid email enumeration
        if not user or not user.is_active:
            return True

        now = datetime.now(timezone.utc)
        raw_token = generate_opaque_token(32)
        token_hash = hash_token(raw_token)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=30),
            created_at=now,
        )
        self.db.add(reset_token)
        await self.db.commit()

        await email_service.send_password_reset_email(
            to_email=user.email,
            full_name=user.full_name,
            raw_token=raw_token,
        )

        await self.log_audit(
            action="auth.password_reset_requested",
            actor_id=user.id,
            target_entity=user.email,
            ip_address=ip_address,
        )
        return True

    async def reset_password(
        self,
        raw_token: str,
        new_password: str,
        ip_address: Optional[str] = None
    ) -> bool:
        t_hash = hash_token(raw_token)
        stmt = select(PasswordResetToken).filter(
            PasswordResetToken.token_hash == t_hash,
            PasswordResetToken.used_at.is_(None)
        )
        result = await self.db.execute(stmt)
        token_record = result.scalars().first()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token."
            )

        now = datetime.now(timezone.utc)
        exp = token_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)

        if now > exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token has expired. Please request a new one."
            )

        token_record.used_at = now
        user = await self.user_repo.get(token_record.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = now
        await self.db.commit()

        # Revoke all active sessions after password reset for security
        await self.session_repo.revoke_all_user_sessions(user.id)

        await email_service.send_password_changed_notification(user.email, user.full_name)
        await self.log_audit(
            action="auth.password_reset_completed",
            actor_id=user.id,
            target_entity=user.email,
            ip_address=ip_address,
        )
        return True

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
        current_session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        user = await self.user_repo.get(user_id)
        if not user or not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )

        now = datetime.now(timezone.utc)
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = now
        await self.db.commit()

        # Revoke all other active sessions except the current one (if specified)
        sessions = await self.session_repo.list_user_sessions(user_id)
        for s in sessions:
            if current_session_id and s.id == current_session_id:
                continue
            await self.session_repo.revoke_session(s.id, user_id=user_id)

        await email_service.send_password_changed_notification(user.email, user.full_name)
        await self.log_audit(
            action="auth.password_changed",
            actor_id=user.id,
            target_entity=user.email,
            ip_address=ip_address,
        )
        return True

    async def deactivate_account(
        self,
        user_id: str,
        password: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        user = await self.user_repo.get(user_id)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password."
            )

        # Check if user is the sole owner of any organization
        stmt = (
            select(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user_id,
                OrganizationMember.role == "owner",
                OrganizationMember.status == "active"
            )
        )
        res = await self.db.execute(stmt)
        owned_memberships = res.scalars().all()

        for om in owned_memberships:
            # Check if there are other owners or members in that org
            all_owners_stmt = select(OrganizationMember).filter(
                OrganizationMember.organization_id == om.organization_id,
                OrganizationMember.role == "owner",
                OrganizationMember.status == "active",
                OrganizationMember.user_id != user_id
            )
            owners_res = await self.db.execute(all_owners_stmt)
            other_owners = owners_res.scalars().all()
            if not other_owners:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot deactivate account while you are the sole owner of an organization. Transfer ownership or delete the organization first."
                )

        now = datetime.now(timezone.utc)
        user.status = "deactivated"
        user.is_active = False
        user.updated_at = now

        # Revoke all sessions
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.db.commit()

        await email_service.send_account_deactivated_notification(user.email, user.full_name)
        await self.log_audit(
            action="auth.account_deactivated",
            actor_id=user.id,
            target_entity=user.email,
            ip_address=ip_address,
            details={"reason": reason},
        )
        return True

