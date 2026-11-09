"""
FluentMeet AI - Step 10 Integration Tests: Report Generation & Orchestration
Tests report generation lifecycle, idempotency, versioning, and snapshot retrieval.
"""

import uuid
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
import app.database.session as app_session_mod
from app.models.base import Meeting, MeetingParticipant
from app.models.transcript import MeetingSpeaker, TranscriptSegment
from app.models.analysis import (
    AnalysisSession,
    ParticipantAnalysis,
    AnalysisCategoryScore,
    GrammarIssue,
    VocabularyInsight,
    FluencyMetric,
    ImprovementRecommendation,
)
from app.models.pronunciation import (
    PronunciationAssessment,
    PronunciationWordResult,
    PronunciationProsodyResult,
    PronunciationRecommendation,
    IELTSSpeakingPracticeAssessment,
)
from app.models.report import ReportSnapshot


@pytest.mark.asyncio
async def test_report_generation_end_to_end(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    user_id = auth_token["user_id"]

    # 1. Create meeting
    m_resp = await async_client.post(
        "/api/v1/meetings",
        json={"title": "Q3 Planning Strategy Session", "platform": "google_meet"},
        headers=headers,
    )
    assert m_resp.status_code == 201
    meeting_id = m_resp.json()["data"]["id"]

    # 2. Seed participant, speaker, transcript, analysis (Step 08), and pronunciation (Step 09)
    async with app_session_mod.AsyncSessionLocal() as db:
        participant = MeetingParticipant(
            meeting_id=meeting_id,
            name="Alice Smith",
        )
        db.add(participant)
        await db.flush()

        speaker = MeetingSpeaker(
            meeting_id=meeting_id,
            speaker_label="speaker_alice",
            participant_id=participant.id,
            display_name="Alice Smith",
            source_id=0,
            is_identified=True,
        )
        db.add(speaker)
        await db.flush()

        # Transcript
        db.add(
            TranscriptSegment(
                meeting_id=meeting_id,
                speaker_id=speaker.id,
                start_time_ms=0,
                end_time_ms=15000,
                duration_ms=15000,
                text="Good morning team. We have analyzed the quarterly numbers and our results are exceeding projections.",
            )
        )

        # Step 08 Analysis Session
        session = AnalysisSession(
            user_id=user_id,
            meeting_id=meeting_id,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()

        pa = ParticipantAnalysis(
            analysis_session_id=session.id,
            speaker_label="speaker_alice",
            participant_id=participant.id,
            status="completed",
            overall_score=85.0,
            analysis_confidence=0.92,
        )
        db.add(pa)
        await db.flush()

        # Category scores
        db.add(AnalysisCategoryScore(participant_analysis_id=pa.id, category="Grammar", score=88.0))
        db.add(AnalysisCategoryScore(participant_analysis_id=pa.id, category="Vocabulary", score=86.0))
        db.add(AnalysisCategoryScore(participant_analysis_id=pa.id, category="Fluency", score=82.0))

        # Grammar Issue
        db.add(
            GrammarIssue(
                participant_analysis_id=pa.id,
                category="verb_tense",
                original_text="are exceeding",
                corrected_text="have exceeded",
                explanation="Consider perfect aspect for completed milestones.",
                severity="low",
            )
        )

        # Step 09 Pronunciation Assessment
        pra = PronunciationAssessment(
            meeting_id=meeting_id,
            participant_id=participant.id,
            speaker_label="speaker_alice",
            assessment_status="completed",
            audio_quality_status="suitable",
            overall_pronunciation_score=84.0,
            evidence_confidence=0.90,
            evaluated_word_count=16,
            processing_started_at=datetime.now(timezone.utc),
        )
        db.add(pra)
        await db.flush()

        # Pronunciation Word Result
        db.add(
            PronunciationWordResult(
                assessment_id=pra.id,
                word_text="projections",
                start_time_ms=1000,
                end_time_ms=1800,
                duration_ms=800,
                expected_phonemes="p r ə dʒ ɛ k ʃ ə n z",
                observed_phonetic_evidence="p r oʊ dʒ ɛ k ʃ ə n z",
                pronunciation_score=72.0,
            )
        )

        # IELTS Assessment
        db.add(
            IELTSSpeakingPracticeAssessment(
                assessment_id=pra.id,
                overall_practice_estimate=7.5,
                fluency_coherence_estimate=7.5,
                lexical_resource_estimate=7.5,
                grammatical_accuracy_estimate=8.0,
                pronunciation_estimate=7.0,
                qualitative_band_descriptor="Effective operational command of the spoken language with occasional inaccuracies.",
            )
        )
        await db.commit()

    # 3. Trigger Report Generation
    gen_resp = await async_client.post(
        "/api/v1/reports/generate",
        json={"meeting_id": meeting_id, "force_regenerate": False},
        headers=headers,
    )
    assert gen_resp.status_code == 200
    snapshots = gen_resp.json()["data"]
    assert len(snapshots) >= 2  # summary + participant snapshot

    summary_snap = next(s for s in snapshots if s["report_type"] == "meeting_summary")
    part_snap = next(s for s in snapshots if s["report_type"] == "individual_participant")

    assert summary_snap["meeting_id"] == meeting_id
    assert part_snap["speaker_label"] == "speaker_alice"
    # Weighted 25% * (88 + 86 + 82 + 84) = 25% * 340 = 85.0
    assert part_snap["overall_score"] == 85.0

    # 4. Test Idempotency (replay returns existing version)
    gen_resp_2 = await async_client.post(
        "/api/v1/reports/generate",
        json={"meeting_id": meeting_id, "force_regenerate": False},
        headers=headers,
    )
    assert gen_resp_2.status_code == 200
    snapshots_2 = gen_resp_2.json()["data"]
    assert snapshots_2[0]["report_version"] == 1

    # 5. Test Force Regenerate (increments version)
    gen_resp_3 = await async_client.post(
        "/api/v1/reports/generate",
        json={"meeting_id": meeting_id, "force_regenerate": True},
        headers=headers,
    )
    assert gen_resp_3.status_code == 200
    snapshots_3 = gen_resp_3.json()["data"]
    assert snapshots_3[0]["report_version"] == 2

    # 6. Retrieve Meeting Summary via GET
    sum_get = await async_client.get(
        f"/api/v1/reports/meetings/{meeting_id}",
        headers=headers,
    )
    assert sum_get.status_code == 200
    assert sum_get.json()["data"]["report_type"] == "meeting_summary"

    # 7. Retrieve Participant Reports for Meeting via GET
    parts_get = await async_client.get(
        f"/api/v1/reports/meetings/{meeting_id}/participants",
        headers=headers,
    )
    assert parts_get.status_code == 200
    assert len(parts_get.json()["data"]) >= 1

    # 8. Retrieve Snapshot by ID and Status
    rep_id = part_snap["id"]
    byId = await async_client.get(f"/api/v1/reports/{rep_id}", headers=headers)
    assert byId.status_code == 200
    assert byId.json()["data"]["id"] == rep_id

    st = await async_client.get(f"/api/v1/reports/{rep_id}/status", headers=headers)
    assert st.status_code == 200
    assert st.json()["data"]["status"] == "completed"
