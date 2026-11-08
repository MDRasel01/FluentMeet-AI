"""
FluentMeet AI - Step 09: Pronunciation Analysis & IELTS Assessment REST Endpoints
Specification: Step 09 - Section 20
Provides endpoints for triggering pronunciation assessments, retrieving acoustic word scores,
inspecting prosody & speaking pace, practice recommendations, and IELTS-style practice estimates.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User, Meeting
from app.models.pronunciation import (
    PronunciationAssessment,
    PronunciationWordResult,
    PronunciationProsodyResult,
    PronunciationRecommendation,
    IELTSSpeakingPracticeAssessment,
)
from app.schemas.common import ApiResponse
from app.schemas.pronunciation import (
    TriggerPronunciationRequest,
    PronunciationAssessmentResponse,
    WordPronunciationResponse,
    ProsodyResponse,
    PronunciationRecommendationResponse,
    IELTSPracticeAssessmentResponse,
)
from app.pronunciation.orchestrator import PronunciationOrchestrator

logger = logging.getLogger("api.pronunciation")
router = APIRouter(prefix="", tags=["Pronunciation & IELTS Assessment"])


async def _verify_meeting_access(meeting_id: str, current_user: User, db: AsyncSession) -> Meeting:
    """
    Enforces multi-tenant and user isolation boundaries for meetings.
    """
    stmt = select(Meeting).where(Meeting.id == meeting_id)
    res = await db.execute(stmt)
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    user_org_id = getattr(current_user, "current_organization_id", None)
    if meeting.user_id != current_user.id and (not user_org_id or meeting.organization_id != user_org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to meeting pronunciation assessment",
        )
    return meeting


async def _get_assessment_with_access(
    assessment_id: str,
    current_user: User,
    db: AsyncSession,
) -> PronunciationAssessment:
    """
    Fetches assessment and verifies user has authorized access to parent meeting.
    """
    stmt = (
        select(PronunciationAssessment)
        .where(PronunciationAssessment.id == assessment_id)
        .options(
            selectinload(PronunciationAssessment.prosody_result),
            selectinload(PronunciationAssessment.ielts_assessment),
            selectinload(PronunciationAssessment.recommendations),
        )
    )
    res = await db.execute(stmt)
    assessment = res.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    await _verify_meeting_access(assessment.meeting_id, current_user, db)
    return assessment


@router.post("/meetings/{meeting_id}/pronunciation", response_model=ApiResponse[List[PronunciationAssessmentResponse]])
async def trigger_meeting_pronunciation(
    meeting_id: str,
    payload: Optional[TriggerPronunciationRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers or retrieves pronunciation and IELTS-style assessment for participant(s) in a meeting.
    """
    await _verify_meeting_access(meeting_id, current_user, db)

    force_reassess = payload.force_reassess if payload else False
    speaker_id = payload.speaker_id if payload else None
    participant_id = payload.participant_id if payload else None

    orchestrator = PronunciationOrchestrator()
    try:
        assessments = await orchestrator.run_assessment(
            db=db,
            meeting_id=meeting_id,
            user_id=current_user.id,
            speaker_id=speaker_id,
            participant_id=participant_id,
            tenant_id=getattr(current_user, "current_organization_id", None),
            force_reassess=force_reassess,
        )
        return ApiResponse.ok_response(data=assessments)
    except Exception as exc:
        logger.exception(f"Pronunciation assessment failed for meeting {meeting_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pronunciation assessment execution failed: {str(exc)}",
        )


@router.post("/pronunciation/assessments", response_model=ApiResponse[List[PronunciationAssessmentResponse]])
async def trigger_assessment_by_body(
    payload: TriggerPronunciationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger assessment with meeting_id in payload body.
    """
    if not payload.meeting_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="meeting_id is required")

    return await trigger_meeting_pronunciation(
        meeting_id=payload.meeting_id,
        payload=payload,
        current_user=current_user,
        db=db,
    )


@router.get("/meetings/{meeting_id}/pronunciation", response_model=ApiResponse[List[PronunciationAssessmentResponse]])
async def list_meeting_pronunciation_assessments(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all pronunciation assessments for a meeting.
    """
    await _verify_meeting_access(meeting_id, current_user, db)

    stmt = (
        select(PronunciationAssessment)
        .where(PronunciationAssessment.meeting_id == meeting_id)
        .options(
            selectinload(PronunciationAssessment.prosody_result),
            selectinload(PronunciationAssessment.ielts_assessment),
            selectinload(PronunciationAssessment.recommendations),
        )
        .order_by(PronunciationAssessment.created_at.desc())
    )
    res = await db.execute(stmt)
    records = list(res.scalars().all())
    return ApiResponse.ok_response(data=records)


@router.get("/pronunciation/assessments/{assessment_id}", response_model=ApiResponse[PronunciationAssessmentResponse])
async def get_pronunciation_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves full pronunciation assessment summary, quality status, and IELTS practice estimate.
    """
    assessment = await _get_assessment_with_access(assessment_id, current_user, db)
    return ApiResponse.ok_response(data=assessment)


@router.get("/pronunciation/assessments/{assessment_id}/words", response_model=ApiResponse[List[WordPronunciationResponse]])
async def get_assessment_word_results(
    assessment_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves granular word-level acoustic scoring and phoneme evidence.
    """
    await _get_assessment_with_access(assessment_id, current_user, db)

    stmt = (
        select(PronunciationWordResult)
        .where(PronunciationWordResult.assessment_id == assessment_id)
        .options(selectinload(PronunciationWordResult.phoneme_results))
        .order_by(PronunciationWordResult.start_time_ms.asc())
    )
    if status_filter:
        stmt = stmt.where(PronunciationWordResult.evaluation_status == status_filter)

    res = await db.execute(stmt)
    words = list(res.scalars().all())
    return ApiResponse.ok_response(data=words)


@router.get("/pronunciation/assessments/{assessment_id}/prosody", response_model=ApiResponse[ProsodyResponse])
async def get_assessment_prosody(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves prosody, intonation (F0 pitch features), stress scores, speaking pace, and intelligibility.
    """
    assessment = await _get_assessment_with_access(assessment_id, current_user, db)
    if not assessment.prosody_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prosody analysis not available for this assessment",
        )
    return ApiResponse.ok_response(data=assessment.prosody_result)


@router.get("/pronunciation/assessments/{assessment_id}/recommendations", response_model=ApiResponse[List[PronunciationRecommendationResponse]])
async def get_assessment_recommendations(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves targeted pronunciation practice exercises (minimal pairs, syllable stress, intonation drills).
    """
    assessment = await _get_assessment_with_access(assessment_id, current_user, db)
    return ApiResponse.ok_response(data=assessment.recommendations or [])


@router.get("/pronunciation/assessments/{assessment_id}/ielts", response_model=ApiResponse[IELTSPracticeAssessmentResponse])
async def get_assessment_ielts_estimate(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the 4-dimension IELTS-style speaking practice estimate with qualitative descriptor and educational disclaimer.
    """
    assessment = await _get_assessment_with_access(assessment_id, current_user, db)
    if not assessment.ielts_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IELTS practice estimate not available for this assessment",
        )
    return ApiResponse.ok_response(data=assessment.ielts_assessment)


@router.post("/pronunciation/assessments/{assessment_id}/retry", response_model=ApiResponse[PronunciationAssessmentResponse])
async def retry_pronunciation_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Re-runs pronunciation assessment for a participant.
    """
    assessment = await _get_assessment_with_access(assessment_id, current_user, db)
    orchestrator = PronunciationOrchestrator()
    updated_assessments = await orchestrator.run_assessment(
        db=db,
        meeting_id=assessment.meeting_id,
        user_id=current_user.id,
        speaker_id=assessment.speaker_id,
        tenant_id=getattr(current_user, "current_organization_id", None),
        force_reassess=True,
    )
    if not updated_assessments:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Retry yielded no assessment")

    target = next((a for a in updated_assessments if a.id == assessment.id), updated_assessments[0])
    return ApiResponse.ok_response(data=target)
