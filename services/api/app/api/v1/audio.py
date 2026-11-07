"""
FluentMeet AI - Audio Ingestion & Streaming REST Endpoints
Specification: Step 06 - Section 18
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User
from app.models.audio import (
    AudioStream,
    AudioSegment,
    AudioQualityMetric,
    AudioStreamGap
)
from app.schemas.audio import (
    AudioStreamCreate,
    AudioStreamResponse,
    AudioSegmentResponse,
    AudioMeetingStatusResponse,
    AudioMeetingQualityResponse
)
from app.schemas.common import ApiResponse
from app.audio.service import audio_ingestion_service

logger = logging.getLogger("api.audio")
router = APIRouter(prefix="", tags=["Audio Ingestion"])


@router.post("/meetings/{meeting_id}/audio-streams", response_model=ApiResponse[AudioStreamResponse])
async def create_or_register_audio_stream(
    meeting_id: str,
    payload: AudioStreamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new audio stream (Pipeline A or Pipeline B) for a meeting.
    """
    stmt = select(AudioStream).where(
        AudioStream.meeting_id == meeting_id,
        AudioStream.source_id == payload.source_id,
        AudioStream.stream_status == "active"
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        return ApiResponse.ok_response(data=existing, message="Active stream already exists for source")

    stream_uuid = f"stream-{payload.source_id}-{uuid.uuid4().hex[:8]}"
    new_stream = AudioStream(
        meeting_id=meeting_id,
        organization_id=payload.organization_id or getattr(current_user, "current_organization_id", None),
        user_id=current_user.id,
        source_id=payload.source_id,
        stream_id=stream_uuid,
        encoding=payload.codec,
        sample_rate=payload.sample_rate,
        channels=payload.channels,
        stream_status="active"
    )
    db.add(new_stream)
    await db.commit()
    await db.refresh(new_stream)

    logger.info(f"Registered audio stream {new_stream.id} for meeting {meeting_id}, source {payload.source_id}")
    return ApiResponse.ok_response(data=new_stream, message="Audio stream initialized")


@router.get("/meetings/{meeting_id}/audio-streams", response_model=ApiResponse[List[AudioStreamResponse]])
async def list_meeting_audio_streams(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all audio streams registered for a specific meeting.
    """
    stmt = select(AudioStream).where(AudioStream.meeting_id == meeting_id).order_by(AudioStream.source_id.asc())
    res = await db.execute(stmt)
    streams = res.scalars().all()
    return ApiResponse.ok_response(data=list(streams))


@router.get("/audio-streams/{stream_id}", response_model=ApiResponse[AudioStreamResponse])
async def get_audio_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves metadata for a specific audio stream.
    """
    stmt = select(AudioStream).where(AudioStream.id == stream_id)
    res = await db.execute(stmt)
    stream = res.scalar_one_or_none()
    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio stream not found")
    return ApiResponse.ok_response(data=stream)


@router.get("/audio-streams/{stream_id}/segments", response_model=ApiResponse[List[AudioSegmentResponse]])
async def list_stream_segments(
    stream_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists persisted audio segments belonging to a specific stream.
    """
    stmt = (
        select(AudioSegment)
        .options(selectinload(AudioSegment.quality_metric))
        .where(AudioSegment.stream_id == stream_id)
        .order_by(AudioSegment.first_sequence.asc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    segments = res.scalars().all()
    return ApiResponse.ok_response(data=list(segments))


@router.get("/audio-segments/{segment_id}", response_model=ApiResponse[AudioSegmentResponse])
async def get_audio_segment(
    segment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves detailed metadata, checksum, storage key, and quality metrics for an audio segment.
    """
    stmt = (
        select(AudioSegment)
        .options(selectinload(AudioSegment.quality_metric))
        .where(AudioSegment.id == segment_id)
    )
    res = await db.execute(stmt)
    segment = res.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio segment not found")
    return ApiResponse.ok_response(data=segment)


@router.get("/meetings/{meeting_id}/audio-status", response_model=ApiResponse[AudioMeetingStatusResponse])
async def get_meeting_audio_status(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns aggregated real-time ingestion status across both audio pipelines for a meeting.
    """
    stmt = select(
        AudioSegment.source_id,
        func.count(AudioSegment.id).label("segment_count"),
        func.sum(AudioSegment.duration_ms).label("total_duration_ms"),
        func.sum(AudioSegment.sample_count * 2).label("total_bytes"),
        func.max(AudioSegment.last_sequence).label("last_sequence")
    ).where(AudioSegment.meeting_id == meeting_id).group_by(AudioSegment.source_id)

    res = await db.execute(stmt)
    rows = res.fetchall()

    source_stats = {}
    active_sources = []
    total_segments = 0
    total_duration_ms = 0
    total_bytes = 0

    for row in rows:
        source_id = row[0]
        active_sources.append(source_id)
        s_count = row[1] or 0
        s_dur = row[2] or 0
        s_bytes = row[3] or 0
        s_last_seq = row[4] or 0

        source_stats[source_id] = {
            "segments_count": s_count,
            "duration_ms": s_dur,
            "bytes": s_bytes,
            "last_sequence": s_last_seq,
        }
        total_segments += s_count
        total_duration_ms += s_dur
        total_bytes += s_bytes

    gaps_stmt = select(func.count(AudioStreamGap.id)).select_from(AudioStreamGap).join(
        AudioStream, AudioStreamGap.stream_id == AudioStream.id
    ).where(AudioStream.meeting_id == meeting_id)
    gaps_res = await db.execute(gaps_stmt)
    total_gaps = gaps_res.scalar() or 0

    status_data = AudioMeetingStatusResponse(
        meeting_id=meeting_id,
        status="active" if active_sources else "inactive",
        active_sources=active_sources,
        source_stats=source_stats,
        total_segments=total_segments,
        total_duration_ms=total_duration_ms,
        total_bytes=total_bytes,
        total_gaps_detected=total_gaps
    )

    return ApiResponse.ok_response(data=status_data)


@router.get("/meetings/{meeting_id}/audio-quality", response_model=ApiResponse[AudioMeetingQualityResponse])
async def get_meeting_audio_quality(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns aggregated audio quality diagnostics for a meeting.
    """
    stmt = (
        select(AudioSegment, AudioQualityMetric)
        .join(AudioQualityMetric, AudioSegment.id == AudioQualityMetric.segment_id)
        .where(AudioSegment.meeting_id == meeting_id)
    )
    res = await db.execute(stmt)
    rows = res.all()

    if not rows:
        return ApiResponse.ok_response(
            data=AudioMeetingQualityResponse(
                meeting_id=meeting_id,
                overall_quality="NO_DATA",
                total_segments_analyzed=0,
                average_rms=0.0,
                peak_amplitude=0.0,
                average_clipping_ratio=0.0,
                average_silence_ratio=0.0,
                degraded_segments_count=0,
                details_by_source={}
            )
        )

    total_rms = 0.0
    max_peak = 0.0
    total_clipping = 0.0
    total_silence = 0.0
    degraded_count = 0
    by_source = {}

    for segment, metric in rows:
        total_rms += metric.rms_level
        max_peak = max(max_peak, metric.peak_amplitude)
        total_clipping += metric.clipping_ratio
        total_silence += metric.silence_ratio

        if metric.clipping_ratio > 0.05 or metric.rms_level < 0.005:
            degraded_count += 1

        sid = segment.source_id
        if sid not in by_source:
            by_source[sid] = {
                "count": 0,
                "total_rms": 0.0,
                "peak": 0.0,
                "total_clipping": 0.0,
                "total_silence": 0.0
            }
        by_source[sid]["count"] += 1
        by_source[sid]["total_rms"] += metric.rms_level
        by_source[sid]["peak"] = max(by_source[sid]["peak"], metric.peak_amplitude)
        by_source[sid]["total_clipping"] += metric.clipping_ratio
        by_source[sid]["total_silence"] += metric.silence_ratio

    count = len(rows)
    avg_rms = total_rms / count
    avg_clipping = total_clipping / count
    avg_silence = total_silence / count

    details = {}
    for sid, stat in by_source.items():
        sc = stat["count"]
        details[sid] = {
            "segments_count": sc,
            "average_rms": round(stat["total_rms"] / sc, 4),
            "peak_amplitude": round(stat["peak"], 4),
            "average_clipping_ratio": round(stat["total_clipping"] / sc, 4),
            "average_silence_ratio": round(stat["total_silence"] / sc, 4)
        }

    overall = "EXCELLENT"
    if degraded_count > count * 0.2:
        overall = "DEGRADED"
    elif degraded_count > 0:
        overall = "FAIR"

    quality_data = AudioMeetingQualityResponse(
        meeting_id=meeting_id,
        overall_quality=overall,
        total_segments_analyzed=count,
        average_rms=round(avg_rms, 4),
        peak_amplitude=round(max_peak, 4),
        average_clipping_ratio=round(avg_clipping, 4),
        average_silence_ratio=round(avg_silence, 4),
        degraded_segments_count=degraded_count,
        details_by_source=details
    )

    return ApiResponse.ok_response(data=quality_data)


@router.post("/audio-streams/{stream_id}/close", response_model=ApiResponse[Dict[str, Any]])
async def close_audio_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Closes an audio stream, flushes pending audio chunks into segments,
    and marks stream status as 'closed'.
    """
    stmt = select(AudioStream).where(AudioStream.id == stream_id)
    res = await db.execute(stmt)
    stream = res.scalar_one_or_none()
    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio stream not found")

    stream.stream_status = "closed"

    flushed_acks = await audio_ingestion_service.flush_remaining_audio(
        session_id=stream.meeting_id,
        organization_id=stream.organization_id,
        db=db
    )
    await db.commit()

    return ApiResponse.ok_response(
        data={
            "stream_id": stream_id,
            "meeting_id": stream.meeting_id,
            "status": "closed",
            "flushed_segments_count": len(flushed_acks)
        },
        message="Audio stream closed successfully"
    )
