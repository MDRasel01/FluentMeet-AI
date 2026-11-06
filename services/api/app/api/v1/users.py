from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User
from app.schemas.auth import UserProfileResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/users", tags=["Users"])

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    native_language: Optional[str] = None

@router.get("/me", response_model=ApiResponse[UserProfileResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    profile = UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        native_language=current_user.native_language,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )
    return ApiResponse.ok_response(data=profile)

@router.put("/me", response_model=ApiResponse[UserProfileResponse])
async def update_my_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.native_language is not None:
        current_user.native_language = req.native_language

    await db.commit()
    await db.refresh(current_user)

    profile = UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        native_language=current_user.native_language,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )
    return ApiResponse.ok_response(data=profile)
