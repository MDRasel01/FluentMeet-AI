"""
FluentMeet AI - Step 08: AI English Analysis REST Endpoints
Specification: Step 08 - Section 20
Provides endpoints for triggering analysis, polling status, retrieving participant breakdowns,
and tracking cross-meeting historical progress.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.base import User, Meeting
from app.models.analysis import (
    AnalysisSession,
    ParticipantAnalysis,
    AnalysisCategoryScore,
    GrammarIssue,
    VocabularyInsight,
    FluencyMetric,
    CommunicationInsight,
    ImprovementRecommendation,
    AnalysisEvent,
)
from app.schemas.common import ApiResponse
from app.schemas.analysis import (
    TriggerAnalysisRequest,
    AnalysisSessionResponse,
    ParticipantDetailedAnalysisResponse,
    HistoricalProgressResponse,
    HistoricalProgressPoint,
    CategoryScoreResponse,
    RecommendationResponse,
)
from app.analysis.orchestrator import AnalysisOrchestrator

logger = logging.getLogger("api.analysis")
router = APIRouter(prefix="", tags=["AI English Analysis"])


async def _verify_meeting_access(meeting_id: str, current_user: User, db: AsyncSession) -> Meeting:
    """
    Enforces tenant and user isolation boundaries for meetings.
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
            detail="Access denied to meeting analysis",
        )
    return meeting


@router.post("/meetings/{meeting_id}/analysis", response_model=ApiResponse[AnalysisSessionResponse])
async def trigger_meeting_analysis(
    meeting_id: str,
    payload: Optional[TriggerAnalysisRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers an English analysis session for the given meeting.
    Idempotent: returns existing analysis if completed and force_reanalyze is False.
    """
    meeting = await _verify_meeting_access(meeting_id, current_user, db)
    force = payload.force_reanalyze if payload else False

    tenant_id = meeting.organization_id or getattr(current_user, "current_organization_id", None)
    orchestrator = AnalysisOrchestrator()

    session = await orchestrator.run_analysis(
        db=db,
        meeting_id=meeting.id,
        user_id=current_user.id,
        tenant_id=tenant_id,
        force_reanalyze=force,
    )

    # Reload session with participants and category scores
    res = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.id == session.id)
        .options(
            selectinload(AnalysisSession.participants).selectinload(
                ParticipantAnalysis.category_scores
            )
        )
    )
    loaded_session = res.scalar_one()

    return ApiResponse.ok_response(
        data=AnalysisSessionResponse.model_validate(loaded_session),
        message=f"Analysis session status: {loaded_session.status}",
    )


@router.get("/analysis/{analysis_id}/status", response_model=ApiResponse[dict])
async def get_analysis_status(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lightweight status polling endpoint for background analysis jobs.
    """
    res = await db.execute(select(AnalysisSession).where(AnalysisSession.id == analysis_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis session not found")

    await _verify_meeting_access(session.meeting_id, current_user, db)

    return ApiResponse.ok_response(
        data={
            "analysis_id": session.id,
            "meeting_id": session.meeting_id,
            "status": session.status,
            "requested_at": session.requested_at,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "error_code": session.error_code,
        }
    )


@router.get("/analysis/{analysis_id}", response_model=ApiResponse[AnalysisSessionResponse])
async def get_analysis_session(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves full analysis session details and participant score overviews.
    """
    res = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.id == analysis_id)
        .options(
            selectinload(AnalysisSession.participants).selectinload(
                ParticipantAnalysis.category_scores
            )
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis session not found")

    await _verify_meeting_access(session.meeting_id, current_user, db)

    return ApiResponse.ok_response(data=AnalysisSessionResponse.model_validate(session))


@router.get(
    "/analysis/{analysis_id}/participants/{participant_analysis_id}",
    response_model=ApiResponse[ParticipantDetailedAnalysisResponse],
)
async def get_participant_analysis_details(
    analysis_id: str,
    participant_analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves deep participant analysis: grammar issues, vocabulary insights,
    fluency metrics, communication insights, and prioritized recommendations.
    """
    res = await db.execute(
        select(ParticipantAnalysis)
        .where(
            and_(
                ParticipantAnalysis.id == participant_analysis_id,
                ParticipantAnalysis.analysis_session_id == analysis_id,
            )
        )
        .options(
            selectinload(ParticipantAnalysis.category_scores),
            selectinload(ParticipantAnalysis.grammar_issues),
            selectinload(ParticipantAnalysis.vocabulary_insights),
            selectinload(ParticipantAnalysis.fluency_metrics),
            selectinload(ParticipantAnalysis.communication_insights),
            selectinload(ParticipantAnalysis.recommendations),
        )
    )
    participant = res.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant analysis record not found",
        )

    # Check meeting access
    res_session = await db.execute(select(AnalysisSession).where(AnalysisSession.id == analysis_id))
    session = res_session.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis session not found")

    await _verify_meeting_access(session.meeting_id, current_user, db)

    return ApiResponse.ok_response(
        data=ParticipantDetailedAnalysisResponse.model_validate(participant)
    )


@router.get("/participants/{speaker_label}/progress", response_model=ApiResponse[HistoricalProgressResponse])
async def get_participant_progress(
    speaker_label: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves chronological score progression across meetings for a speaker.
    """
    user_org_id = getattr(current_user, "current_organization_id", None)

    # Query participant analyses joined to session and meeting to enforce tenant boundary
    stmt = (
        select(ParticipantAnalysis)
        .join(AnalysisSession, ParticipantAnalysis.analysis_session_id == AnalysisSession.id)
        .join(Meeting, AnalysisSession.meeting_id == Meeting.id)
        .where(
            and_(
                ParticipantAnalysis.speaker_label == speaker_label,
                ParticipantAnalysis.score_status == "available",
                Meeting.organization_id == user_org_id if user_org_id else Meeting.user_id == current_user.id,
            )
        )
        .order_by(ParticipantAnalysis.created_at.asc())
        .options(
            selectinload(ParticipantAnalysis.category_scores),
            selectinload(ParticipantAnalysis.session),
        )
    )

    res = await db.execute(stmt)
    records = list(res.scalars().all())

    history_points = []
    for r in records:
        history_points.append(
            HistoricalProgressPoint(
                meeting_id=r.session.meeting_id if hasattr(r, "session") and r.session else "",
                analysis_session_id=r.analysis_session_id,
                session_date=r.created_at,
                overall_score=r.overall_score,
                category_scores=[CategoryScoreResponse.model_validate(c) for c in r.category_scores],
            )
        )

    return ApiResponse.ok_response(
        data=HistoricalProgressResponse(
            speaker_label=speaker_label,
            history=history_points,
        )
    )


@router.get(
    "/participants/{speaker_label}/recommendations",
    response_model=ApiResponse[List[RecommendationResponse]],
)
async def get_participant_recommendations(
    speaker_label: str,
    priority: Optional[str] = Query(None, description="Filter by high, medium, low"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves active coaching recommendations across all meetings for a speaker.
    """
    user_org_id = getattr(current_user, "current_organization_id", None)

    stmt = (
        select(ImprovementRecommendation)
        .join(ParticipantAnalysis, ImprovementRecommendation.participant_analysis_id == ParticipantAnalysis.id)
        .join(AnalysisSession, ParticipantAnalysis.analysis_session_id == AnalysisSession.id)
        .join(Meeting, AnalysisSession.meeting_id == Meeting.id)
        .where(
            and_(
                ParticipantAnalysis.speaker_label == speaker_label,
                ImprovementRecommendation.status == "active",
                Meeting.organization_id == user_org_id if user_org_id else Meeting.user_id == current_user.id,
            )
        )
    )
    if priority:
        stmt = stmt.where(ImprovementRecommendation.priority == priority)

    stmt = stmt.order_by(desc(ImprovementRecommendation.created_at))

    res = await db.execute(stmt)
    recs = list(res.scalars().all())

    return ApiResponse.ok_response(
        data=[RecommendationResponse.model_validate(r) for r in recs]
    )
