from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.deps import get_current_user, get_client_ip
from app.models.base import User, UserProfile
from app.schemas.user import (
    UserUpdateRequest,
    EmailChangeRequest,
    AccountDeactivateRequest,
    UserDetailResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=ApiResponse[UserDetailResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    profile = current_user.profile
    resp = UserDetailResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        native_language=current_user.native_language,
        role=current_user.role,
        status=current_user.status,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        email_verified_at=current_user.email_verified_at,
        timezone=current_user.timezone,
        avatar_url=profile.avatar_url if profile else None,
        phone_number=profile.phone_number if profile else None,
        bio=profile.bio if profile else None,
        job_title=profile.job_title if profile else None,
        english_learning_goal=profile.english_learning_goal if profile else None,
        target_speaking_score=profile.target_speaking_score if profile else 80,
        created_at=current_user.created_at,
    )
    return ApiResponse.ok_response(data=resp)

@router.patch("/me", response_model=ApiResponse[UserDetailResponse])
async def update_my_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.native_language is not None:
        current_user.native_language = req.native_language
    if req.timezone is not None:
        current_user.timezone = req.timezone
    current_user.updated_at = now

    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id, created_at=now, updated_at=now)
        db.add(profile)

    if req.avatar_url is not None:
        profile.avatar_url = req.avatar_url
    if req.phone_number is not None:
        profile.phone_number = req.phone_number
    if req.bio is not None:
        profile.bio = req.bio
    if req.job_title is not None:
        profile.job_title = req.job_title
    if req.english_learning_goal is not None:
        profile.english_learning_goal = req.english_learning_goal
    if req.target_speaking_score is not None:
        profile.target_speaking_score = req.target_speaking_score
    profile.updated_at = now

    await db.commit()
    await db.refresh(current_user)

    resp = UserDetailResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        native_language=current_user.native_language,
        role=current_user.role,
        status=current_user.status,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        email_verified_at=current_user.email_verified_at,
        timezone=current_user.timezone,
        avatar_url=profile.avatar_url,
        phone_number=profile.phone_number,
        bio=profile.bio,
        job_title=profile.job_title,
        english_learning_goal=profile.english_learning_goal,
        target_speaking_score=profile.target_speaking_score,
        created_at=current_user.created_at,
    )
    return ApiResponse.ok_response(data=resp, message="Profile updated successfully.")

@router.put("/me", response_model=ApiResponse[UserDetailResponse])
async def put_my_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Backward compatibility for PUT /users/me
    return await update_my_profile(req=req, current_user=current_user, db=db)

@router.patch("/me/email", response_model=ApiResponse[bool])
async def request_email_change(
    req: EmailChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.core.security import verify_password
    if not verify_password(req.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password verification failed.")

    user_repo = UserRepository(db)
    existing = await user_repo.get_by_email(req.new_email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email address is already in use.")

    # In production, a verification link is sent to the new email before applying the change.
    current_user.email = req.new_email.lower().strip()
    current_user.is_verified = False
    current_user.email_verified_at = None
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return ApiResponse.ok_response(
        data=True,
        message="Email updated. Please verify your new email address to complete verification."
    )

@router.delete("/me", response_model=ApiResponse[bool])
async def deactivate_my_account(
    req: AccountDeactivateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    ip = get_client_ip(request)
    success = await service.deactivate_account(
        user_id=current_user.id,
        password=req.password,
        reason=req.reason,
        ip_address=ip
    )
    return ApiResponse.ok_response(data=success, message="Account deactivated successfully.")
