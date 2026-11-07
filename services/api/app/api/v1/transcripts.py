"""
FluentMeet AI - Transcript & Speaker Diarization REST Endpoints
Specification: Step 07 - Section 8 & Section 18
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User, Meeting
from app.models.transcript import (
    MeetingSpeaker,
    TranscriptSegment,
    TranscriptWord,
    SpeakerTurn,
    SpeechOverlap,
    TranscriptEvent,
)
from app.schemas.transcript import (
    TranscriptSegmentResponse,
    TranscriptCorrectionRequest,
    MeetingSpeakerResponse,
    SpeakerUpdateRequest,
    SpeechOverlapResponse,
)
from app.schemas.common import ApiResponse
from app.events.publisher import event_publisher

logger = logging.getLogger("api.transcripts")
router = APIRouter(prefix="", tags=["Transcripts & Diarization"])


async def _verify_meeting_access(meeting_id: str, current_user: User, db: AsyncSession) -> Meeting:
    stmt = select(Meeting).where(Meeting.id == meeting_id)
    res = await db.execute(stmt)
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    # Multi-tenant organization or user boundary check
    user_org_id = getattr(current_user, "current_organization_id", None)
    if meeting.user_id != current_user.id and (not user_org_id or meeting.organization_id != user_org_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to meeting transcripts")

    return meeting


@router.get("/meetings/{meeting_id}/transcripts", response_model=ApiResponse[List[TranscriptSegmentResponse]])
async def list_meeting_transcripts(
    meeting_id: str,
    speaker_id: Optional[str] = Query(None, description="Filter by speaker UUID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: partial, provisional, final, corrected"),
    start_ms: Optional[int] = Query(None, description="Start millisecond boundary"),
    end_ms: Optional[int] = Query(None, description="End millisecond boundary"),
    limit: int = Query(200, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List structured transcript segments with word-level timestamps and speaker attributions.
    """
    await _verify_meeting_access(meeting_id, current_user, db)

    query = (
        select(TranscriptSegment)
        .options(selectinload(TranscriptSegment.speaker))
        .where(TranscriptSegment.meeting_id == meeting_id)
    )

    if speaker_id:
        query = query.where(TranscriptSegment.speaker_id == speaker_id)
    if status_filter:
        query = query.where(TranscriptSegment.status == status_filter)
    if start_ms is not None:
        query = query.where(TranscriptSegment.start_time_ms >= start_ms)
    if end_ms is not None:
        query = query.where(TranscriptSegment.end_time_ms <= end_ms)

    query = query.order_by(TranscriptSegment.start_time_ms.asc()).limit(limit)
    result = await db.execute(query)
    segments = result.scalars().all()

    response_items = []
    for s in segments:
        speaker_label = s.speaker.speaker_label if s.speaker else None
        speaker_name = s.speaker.display_name if s.speaker else speaker_label

        response_items.append(
            TranscriptSegmentResponse(
                id=s.id,
                meeting_id=s.meeting_id,
                speaker_id=s.speaker_id,
                speaker_label=speaker_label,
                speaker_name=speaker_name,
                source_id=s.source_id,
                start_time_ms=s.start_time_ms,
                end_time_ms=s.end_time_ms,
                duration_ms=s.duration_ms,
                text=s.text,
                language=s.language,
                confidence_score=s.confidence_score,
                status=s.status,
                revision_number=s.revision_number,
                words=s.words_json or [],
                created_at=s.created_at
            )
        )

    return ApiResponse(success=True, data=response_items)


@router.get("/meetings/{meeting_id}/transcripts/{segment_id}", response_model=ApiResponse[TranscriptSegmentResponse])
async def get_transcript_segment(
    meeting_id: str,
    segment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await _verify_meeting_access(meeting_id, current_user, db)

    stmt = (
        select(TranscriptSegment)
        .options(selectinload(TranscriptSegment.speaker))
        .where(and_(TranscriptSegment.id == segment_id, TranscriptSegment.meeting_id == meeting_id))
    )
    res = await db.execute(stmt)
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript segment not found")

    speaker_label = s.speaker.speaker_label if s.speaker else None
    speaker_name = s.speaker.display_name if s.speaker else speaker_label

    return ApiResponse(
        success=True,
        data=TranscriptSegmentResponse(
            id=s.id,
            meeting_id=s.meeting_id,
            speaker_id=s.speaker_id,
            speaker_label=speaker_label,
            speaker_name=speaker_name,
            source_id=s.source_id,
            start_time_ms=s.start_time_ms,
            end_time_ms=s.end_time_ms,
            duration_ms=s.duration_ms,
            text=s.text,
            language=s.language,
            confidence_score=s.confidence_score,
            status=s.status,
            revision_number=s.revision_number,
            words=s.words_json or [],
            created_at=s.created_at
        )
    )


@router.patch("/meetings/{meeting_id}/transcripts/{segment_id}", response_model=ApiResponse[TranscriptSegmentResponse])
async def correct_transcript_segment(
    meeting_id: str,
    segment_id: str,
    payload: TranscriptCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manual human correction with audit trail and revision incrementing.
    """
    await _verify_meeting_access(meeting_id, current_user, db)

    stmt = (
        select(TranscriptSegment)
        .options(selectinload(TranscriptSegment.speaker))
        .where(and_(TranscriptSegment.id == segment_id, TranscriptSegment.meeting_id == meeting_id))
    )
    res = await db.execute(stmt)
    seg = res.scalar_one_or_none()
    if not seg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript segment not found")

    old_text = seg.text
    old_speaker_id = seg.speaker_id

    if payload.text is not None:
        seg.text = payload.text.strip()
    if payload.speaker_id is not None:
        seg.speaker_id = payload.speaker_id

    seg.status = "corrected"
    seg.revision_number += 1

    # Record event in transcript_events audit table
    event = TranscriptEvent(
        id=str(uuid.uuid4()),
        meeting_id=meeting_id,
        event_type="transcript.corrected",
        payload={
            "segment_id": seg.id,
            "old_text": old_text,
            "new_text": seg.text,
            "old_speaker_id": old_speaker_id,
            "new_speaker_id": seg.speaker_id,
            "revision": seg.revision_number,
            "corrected_by": current_user.id
        }
    )
    db.add(event)
    await db.commit()
    await db.refresh(seg)

    # Broadcast event via Redis
    stream_name = f"meeting:{meeting_id}:events"
    await event_publisher.publish_event(
        stream_name=stream_name,
        event_type="transcript.corrected",
        aggregate_id=meeting_id,
        payload={
            "segment_id": seg.id,
            "text": seg.text,
            "speaker_id": seg.speaker_id,
            "revision_number": seg.revision_number,
            "status": "corrected",
            "meeting_id": meeting_id
        }
    )

    speaker_label = seg.speaker.speaker_label if seg.speaker else None
    speaker_name = seg.speaker.display_name if seg.speaker else speaker_label

    return ApiResponse(
        success=True,
        data=TranscriptSegmentResponse(
            id=seg.id,
            meeting_id=seg.meeting_id,
            speaker_id=seg.speaker_id,
            speaker_label=speaker_label,
            speaker_name=speaker_name,
            source_id=seg.source_id,
            start_time_ms=seg.start_time_ms,
            end_time_ms=seg.end_time_ms,
            duration_ms=seg.duration_ms,
            text=seg.text,
            language=seg.language,
            confidence_score=seg.confidence_score,
            status=seg.status,
            revision_number=seg.revision_number,
            words=seg.words_json or [],
            created_at=seg.created_at
        )
    )


@router.get("/meetings/{meeting_id}/speakers", response_model=ApiResponse[List[MeetingSpeakerResponse]])
async def list_meeting_speakers(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await _verify_meeting_access(meeting_id, current_user, db)

    stmt = select(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting_id).order_by(MeetingSpeaker.created_at.asc())
    res = await db.execute(stmt)
    speakers = res.scalars().all()

    return ApiResponse(
        success=True,
        data=[
            MeetingSpeakerResponse(
                id=spk.id,
                meeting_id=spk.meeting_id,
                speaker_label=spk.speaker_label,
                display_name=spk.display_name,
                is_identified=spk.is_identified,
                confidence_score=spk.confidence_score,
                source_id=spk.source_id
            )
            for spk in speakers
        ]
    )


@router.patch("/meetings/{meeting_id}/speakers/{speaker_id}", response_model=ApiResponse[MeetingSpeakerResponse])
async def update_meeting_speaker(
    meeting_id: str,
    speaker_id: str,
    payload: SpeakerUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await _verify_meeting_access(meeting_id, current_user, db)

    stmt = select(MeetingSpeaker).where(and_(MeetingSpeaker.id == speaker_id, MeetingSpeaker.meeting_id == meeting_id))
    res = await db.execute(stmt)
    spk = res.scalar_one_or_none()
    if not spk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")

    spk.display_name = payload.display_name.strip()
    if payload.participant_id is not None:
        spk.participant_id = payload.participant_id
        spk.is_identified = True

    await db.commit()
    await db.refresh(spk)

    # Broadcast speaker update
    stream_name = f"meeting:{meeting_id}:events"
    await event_publisher.publish_event(
        stream_name=stream_name,
        event_type="speaker.updated",
        aggregate_id=meeting_id,
        payload={
            "speaker_id": spk.id,
            "speaker_label": spk.speaker_label,
            "display_name": spk.display_name,
            "is_identified": spk.is_identified,
            "meeting_id": meeting_id
        }
    )

    return ApiResponse(
        success=True,
        data=MeetingSpeakerResponse(
            id=spk.id,
            meeting_id=spk.meeting_id,
            speaker_label=spk.speaker_label,
            display_name=spk.display_name,
            is_identified=spk.is_identified,
            confidence_score=spk.confidence_score,
            source_id=spk.source_id
        )
    )


@router.get("/meetings/{meeting_id}/overlaps", response_model=ApiResponse[List[SpeechOverlapResponse]])
async def list_meeting_overlaps(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await _verify_meeting_access(meeting_id, current_user, db)

    stmt = select(SpeechOverlap).where(SpeechOverlap.meeting_id == meeting_id).order_by(SpeechOverlap.start_time_ms.asc())
    res = await db.execute(stmt)
    overlaps = res.scalars().all()

    return ApiResponse(
        success=True,
        data=[
            SpeechOverlapResponse(
                id=o.id,
                meeting_id=o.meeting_id,
                start_time_ms=o.start_time_ms,
                end_time_ms=o.end_time_ms,
                duration_ms=o.duration_ms,
                overlapping_speaker_ids=o.overlapping_speaker_ids or [],
                confidence_score=o.confidence_score
            )
            for o in overlaps
        ]
    )
