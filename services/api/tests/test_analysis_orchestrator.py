"""
FluentMeet AI - Step 08 Integration Tests: Analysis Orchestrator
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
import app.database.session as app_session_mod
from app.models.transcript import MeetingSpeaker, TranscriptSegment
from app.models.analysis import (
    AnalysisSession,
    ParticipantAnalysis,
    AnalysisCategoryScore,
    GrammarIssue,
    VocabularyInsight,
    FluencyMetric,
    ImprovementRecommendation,
    AnalysisEvent,
)
from app.analysis.orchestrator import AnalysisOrchestrator


@pytest.mark.asyncio
async def test_analysis_orchestrator_complete_lifecycle(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create meeting
    resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Sprint Retrospective & Architecture Review", "platform": "google_meet"},
        headers=headers,
    )
    assert resp.status_code == 201
    meeting_id = resp.json()["data"]["id"]
    user_id = auth_token["user_id"]

    # 2. Seed speaker and robust speech transcript (>50 words, >15s)
    async with app_session_mod.AsyncSessionLocal() as db:
        speaker = MeetingSpeaker(
            meeting_id=meeting_id,
            speaker_label="speaker_001",
            display_name="Alex (Staff Engineer)",
            source_id=1,
            is_identified=True,
        )
        db.add(speaker)
        await db.flush()

        # Add multiple segments with technical discussion and typical conversational English
        seg_texts = [
            "Good morning team, let us review our current backend API performance and latency numbers.",
            "We was looking at the Redis cache deployment and observed significant progress across all microservices.",
            "However, we should discuss about the database query bottlenecks in the customer billing pipeline.",
            "There are multiple good things we accomplished, but the team don't have enough bandwidth for extra scope.",
            "So basically we should streamline our deployment workflow and optimize the queries before Friday.",
            "What do you think about our revised timeline and stakeholder deliverables for the next sprint?",
        ]

        time_cursor = 0
        for i, text in enumerate(seg_texts):
            seg_duration = 4000
            seg = TranscriptSegment(
                meeting_id=meeting_id,
                speaker_id=speaker.id,
                source_id=1,
                start_time_ms=time_cursor,
                end_time_ms=time_cursor + seg_duration,
                duration_ms=seg_duration,
                text=text,
                language="en",
                confidence_score=0.96,
                status="final",
            )
            db.add(seg)
            time_cursor += seg_duration + 500

        await db.commit()

    # 3. Run analysis orchestrator
    async with app_session_mod.AsyncSessionLocal() as db:
        orchestrator = AnalysisOrchestrator()
        session = await orchestrator.run_analysis(
            db=db,
            meeting_id=meeting_id,
            user_id=user_id,
            tenant_id=None,
        )

        assert session is not None
        assert session.status == "completed"
        assert session.completed_at is not None

        # Verify ParticipantAnalysis
        p_res = await db.execute(
            select(ParticipantAnalysis).where(
                ParticipantAnalysis.analysis_session_id == session.id
            )
        )
        participants = list(p_res.scalars().all())
        assert len(participants) == 1
        p = participants[0]
        assert p.speaker_label == "speaker_001"
        assert p.score_status == "available"
        assert p.overall_score is not None
        assert 50.0 <= p.overall_score <= 100.0

        # Verify Category Scores
        cat_res = await db.execute(
            select(AnalysisCategoryScore).where(
                AnalysisCategoryScore.participant_analysis_id == p.id
            )
        )
        cats = list(cat_res.scalars().all())
        assert len(cats) >= 6
        for cat in cats:
            assert cat.status == "available"
            assert cat.score is not None

        # Verify Fluency Metrics
        fluency_res = await db.execute(
            select(FluencyMetric).where(
                FluencyMetric.participant_analysis_id == p.id
            )
        )
        f_metrics = list(fluency_res.scalars().all())
        assert len(f_metrics) >= 4
        m_names = {m.metric_name for m in f_metrics}
        assert "speech_rate_wpm" in m_names
        assert "filler_word_rate" in m_names

        # Verify Recommendations
        rec_res = await db.execute(
            select(ImprovementRecommendation).where(
                ImprovementRecommendation.participant_analysis_id == p.id
            )
        )
        recs = list(rec_res.scalars().all())
        assert len(recs) > 0
        assert recs[0].priority in ("high", "medium", "low")
        assert recs[0].actionable_suggestion != ""

        # Verify Analysis Events audit log
        event_res = await db.execute(
            select(AnalysisEvent).where(
                AnalysisEvent.analysis_session_id == session.id
            )
        )
        events = list(event_res.scalars().all())
        assert len(events) >= 2
        e_types = [e.event_type for e in events]
        assert "analysis.started" in e_types
        assert "analysis.completed" in e_types


@pytest.mark.asyncio
async def test_analysis_orchestrator_insufficient_data(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # Create meeting
    resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Brief Check-in", "platform": "zoom"},
        headers=headers,
    )
    meeting_id = resp.json()["data"]["id"]
    user_id = auth_token["user_id"]

    # Seed 1 single tiny segment (< 50 words, < 15s)
    async with app_session_mod.AsyncSessionLocal() as db:
        speaker = MeetingSpeaker(
            meeting_id=meeting_id,
            speaker_label="speaker_002",
            source_id=1,
            is_identified=True,
        )
        db.add(speaker)
        await db.flush()

        db.add(
            TranscriptSegment(
                meeting_id=meeting_id,
                speaker_id=speaker.id,
                source_id=1,
                start_time_ms=0,
                end_time_ms=3000,
                duration_ms=3000,
                text="Yes I agree.",
                language="en",
                status="final",
            )
        )
        await db.commit()

    async with app_session_mod.AsyncSessionLocal() as db:
        orchestrator = AnalysisOrchestrator()
        session = await orchestrator.run_analysis(
            db=db,
            meeting_id=meeting_id,
            user_id=user_id,
        )

        p_res = await db.execute(
            select(ParticipantAnalysis).where(
                ParticipantAnalysis.analysis_session_id == session.id
            )
        )
        p = p_res.scalar_one()
        assert p.score_status == "insufficient_data"
        assert p.overall_score is None


@pytest.mark.asyncio
async def test_analysis_orchestrator_empty_segments(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Empty Meeting", "platform": "teams"},
        headers=headers,
    )
    meeting_id = resp.json()["data"]["id"]
    user_id = auth_token["user_id"]

    async with app_session_mod.AsyncSessionLocal() as db:
        orchestrator = AnalysisOrchestrator()
        session = await orchestrator.run_analysis(
            db=db,
            meeting_id=meeting_id,
            user_id=user_id,
        )
        assert session.status == "insufficient_data"
