from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import (
    get_current_user,
    get_client_ip,
    get_client_user_agent,
    security
)
from app.models.base import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserProfileResponse,
    EmailVerifyRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    AuthSessionResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService
from app.repositories.session_repository import SessionRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse[UserProfileResponse], status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    profile = await service.register(payload, ip_address=ip)
    return ApiResponse.ok_response(
        data=profile,
        message="Registration successful. Please check your email to verify your account."
    )

@router.post("/verify-email", response_model=ApiResponse[bool])
async def verify_email(
    payload: EmailVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    success = await service.verify_email(payload.token, ip_address=ip)
    return ApiResponse.ok_response(data=success, message="Email verified successfully. You may now log in.")

@router.post("/resend-verification", response_model=ApiResponse[bool])
async def resend_verification(
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    await service.resend_verification(payload.email)
    return ApiResponse.ok_response(
        data=True,
        message="If an unverified account exists for this email, a verification link has been sent."
    )

@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    payload: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    tokens = await service.login(
        email=payload.email,
        password=payload.password,
        device_type=payload.device_type or "desktop",
        session_name=payload.session_name,
        ip_address=ip,
        user_agent=ua,
    )
    return ApiResponse.ok_response(data=tokens, message="Logged in successfully.")

@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_tokens(
    payload: TokenRefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    tokens = await service.refresh_tokens(payload.refresh_token, ip_address=ip)
    return ApiResponse.ok_response(data=tokens, message="Tokens refreshed successfully.")

@router.post("/logout", response_model=ApiResponse[bool])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve current session ID from decoded token state if available, or latest active session
    session_repo = SessionRepository(db)
    sessions = await session_repo.list_user_sessions(current_user.id)
    if sessions:
        service = AuthService(db)
        await service.logout(sessions[0].id, current_user.id)
    return ApiResponse.ok_response(data=True, message="Logged out successfully.")

@router.post("/logout-all", response_model=ApiResponse[int])
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    count = await service.logout_all(current_user.id)
    return ApiResponse.ok_response(data=count, message=f"Revoked {count} active sessions across all devices.")

@router.post("/forgot-password", response_model=ApiResponse[bool])
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    await service.request_password_reset(payload.email, ip_address=ip)
    return ApiResponse.ok_response(
        data=True,
        message="If this email is registered, password reset instructions have been sent."
    )

@router.post("/reset-password", response_model=ApiResponse[bool])
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    success = await service.reset_password(
        raw_token=payload.token,
        new_password=payload.new_password,
        ip_address=ip,
    )
    return ApiResponse.ok_response(data=success, message="Password reset successfully. Please log in with your new password.")

@router.post("/change-password", response_model=ApiResponse[bool])
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    success = await service.change_password(
        user_id=current_user.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
        ip_address=ip,
    )
    return ApiResponse.ok_response(data=success, message="Password updated successfully.")

@router.get("/sessions", response_model=ApiResponse[List[AuthSessionResponse]])
async def list_active_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session_repo = SessionRepository(db)
    sessions = await session_repo.list_user_sessions(current_user.id)
    resp = [
        AuthSessionResponse(
            id=s.id,
            session_name=s.session_name,
            device_type=s.device_type,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            created_at=s.created_at,
            last_used_at=s.last_used_at,
            expires_at=s.expires_at,
            is_current=False,
        )
        for s in sessions
    ]
    return ApiResponse.ok_response(data=resp)

@router.delete("/sessions/{session_id}", response_model=ApiResponse[bool])
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    revoked = await service.logout(session_id, current_user.id)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or already revoked.")
    return ApiResponse.ok_response(data=True, message="Session revoked successfully.")
