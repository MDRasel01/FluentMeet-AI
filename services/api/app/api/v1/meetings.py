from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User, Meeting, MeetingParticipant, ConsentRecord
from app.schemas.meeting import MeetingCreateRequest, MeetingResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/meetings", tags=["Meetings"])

@router.get("", response_model=ApiResponse[List[MeetingResponse]])
async def list_meetings(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Meeting)
        .where(Meeting.user_id == current_user.id)
        .order_by(desc(Meeting.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    meetings = result.scalars().all()
    
    response_data = [
        MeetingResponse(
            id=m.id,
            title=m.title,
            platform=m.platform,
            meeting_url=m.meeting_url,
            status=m.status,
            duration_seconds=m.duration_seconds,
            my_speaking_seconds=m.my_speaking_seconds,
            overall_score=m.overall_score,
            started_at=m.started_at,
        )
        for m in meetings
    ]
    return ApiResponse.ok_response(data=response_data)

@router.post("", response_model=ApiResponse[MeetingResponse], status_code=status.HTTP_201_CREATED)
async def create_meeting(
    req: MeetingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    meeting = Meeting(
        user_id=current_user.id,
        title=req.title,
        platform=req.platform,
        meeting_url=req.meeting_url,
        status="active",
        started_at=datetime.now(timezone.utc),
    )
    db.add(meeting)
    await db.flush()

    # Local user participant
    local_part = MeetingParticipant(
        meeting_id=meeting.id,
        name=current_user.full_name,
        is_local_user=True,
    )
    db.add(local_part)

    # Consent record if user confirmed consent
    if req.consent_confirmed:
        consent = ConsentRecord(
            meeting_id=meeting.id,
            user_id=current_user.id,
            consented=True,
            consented_at=datetime.now(timezone.utc),
        )
        db.add(consent)

    if req.participants:
        for p in req.participants:
            part = MeetingParticipant(
                meeting_id=meeting.id,
                name=p.name,
                is_local_user=p.is_local_user,
            )
            db.add(part)

    await db.commit()
    await db.refresh(meeting)

    response_data = MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        platform=meeting.platform,
        meeting_url=meeting.meeting_url,
        status=meeting.status,
        duration_seconds=meeting.duration_seconds,
        my_speaking_seconds=meeting.my_speaking_seconds,
        overall_score=meeting.overall_score,
        started_at=meeting.started_at,
    )
    return ApiResponse.ok_response(data=response_data, message="Meeting created successfully")

@router.get("/{meeting_id}", response_model=ApiResponse[MeetingResponse])
async def get_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == current_user.id)
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    response_data = MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        platform=meeting.platform,
        meeting_url=meeting.meeting_url,
        status=meeting.status,
        duration_seconds=meeting.duration_seconds,
        my_speaking_seconds=meeting.my_speaking_seconds,
        overall_score=meeting.overall_score,
        started_at=meeting.started_at,
    )
    return ApiResponse.ok_response(data=response_data)

@router.patch("/{meeting_id}/end", response_model=ApiResponse[MeetingResponse])
async def end_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == current_user.id)
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    now = datetime.now(timezone.utc)
    meeting.ended_at = now
    meeting.status = "completed"
    if meeting.started_at:
        started = meeting.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        meeting.duration_seconds = max(0, int((now - started).total_seconds()))

    await db.commit()
    await db.refresh(meeting)

    response_data = MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        platform=meeting.platform,
        meeting_url=meeting.meeting_url,
        status=meeting.status,
        duration_seconds=meeting.duration_seconds,
        my_speaking_seconds=meeting.my_speaking_seconds,
        overall_score=meeting.overall_score,
        started_at=meeting.started_at,
    )
    return ApiResponse.ok_response(data=response_data, message="Meeting ended successfully")
