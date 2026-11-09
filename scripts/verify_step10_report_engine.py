"""
FluentMeet AI - Step 10 Verification Script: Complete Report Generation, Analytics & Dashboard Engine
Runs an end-to-end verification of multi-source aggregation, validation rules, snapshots, exports, and history.
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime, timezone, timedelta

# Configure environment for standalone execution
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"
os.environ["JWT_SECRET_KEY"] = "verification-key-step10-report-engine"

# Add backend path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "api")))

from app.database.session import AsyncSessionLocal, init_db
from app.models.base import Meeting, MeetingParticipant, User
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
from app.models.report import ReportSnapshot, ReportExport, ReportAccessLog
from app.reports.orchestrator import ReportOrchestrator
from app.reports.validator import ReportValidationEngine, CollectedParticipantData
from app.reports.export import ReportExportService, sanitize_csv_cell, MANDATORY_IELTS_DISCLAIMER
from app.reports.history import HistoricalProgressService
from app.reports.analytics import DashboardAnalyticsService


async def run_verification():
    print("=" * 70)
    print("FLUENTMEET AI - STEP 10 REPORT GENERATION & ANALYTICS ENGINE VERIFICATION")
    print("=" * 70)

    await init_db()
    print("[1/6] Database initialized and tables verified.")

    # 1. Test CSV Injection Sanitizer
    assert sanitize_csv_cell("=CMD|' /C calc'!A0") == "'=CMD|' /C calc'!A0", "Failed to sanitize ="
    assert sanitize_csv_cell("+12345") == "'+12345", "Failed to sanitize +"
    assert sanitize_csv_cell("-555") == "'-555", "Failed to sanitize -"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)", "Failed to sanitize @"
    assert sanitize_csv_cell("Normal text") == "Normal text", "Normal text altered"
    print("[2/6] CSV Spreadsheet Formula Injection Defense verified.")

    # 2. Test Validation Engine Rules
    # Rule A: < 5 words => insufficient_evidence
    p_insuf = CollectedParticipantData(speaker_label="speaker_sparse")
    p_insuf.total_words = 4
    val_insuf = ReportValidationEngine.validate_participant(p_insuf)
    assert val_insuf.report_status == "insufficient_evidence", "Insufficient evidence rule failed"
    assert val_insuf.overall_score is None, "Score fabricated for sparse speech"

    # Rule B: Missing core pillar => Overall score unavailable (never substitute 0)
    p_partial = CollectedParticipantData(speaker_label="speaker_partial")
    p_partial.total_words = 50
    p_partial.grammar_score = 80.0
    p_partial.vocabulary_score = 80.0
    p_partial.fluency_score = 80.0
    p_partial.pronunciation_score = None  # Missing!
    val_partial = ReportValidationEngine.validate_participant(p_partial)
    assert val_partial.report_status == "partial", "Missing component status failed"
    assert val_partial.overall_score is None, "Missing component score must be None"
    assert val_partial.status_label == "Overall score unavailable"

    # Rule C: All 4 pillars present => Calibrated
    p_cal = CollectedParticipantData(speaker_label="speaker_calibrated")
    p_cal.total_words = 100
    p_cal.grammar_score = 80.0
    p_cal.vocabulary_score = 90.0
    p_cal.fluency_score = 70.0
    p_cal.pronunciation_score = 80.0
    val_cal = ReportValidationEngine.validate_participant(p_cal)
    assert val_cal.is_calibrated is True
    assert val_cal.overall_score == 80.0  # 0.25 * (80 + 90 + 70 + 80) = 80.0
    assert val_cal.status_label == "Calibrated"
    print("[3/6] Report Calibration & Zero-Fabrication Rules verified.")

    # 3. Seed Meeting & Multi-Source Step 06-09 Data
    async with AsyncSessionLocal() as db:
        user = User(
            email=f"report_verifier_{uuid.uuid4().hex[:6]}@fluentmeet.ai",
            hashed_password="fakehashedpassword",
            full_name="Report Verifier",
        )
        db.add(user)
        await db.flush()

        meeting = Meeting(
            title="Executive Quarterly English Review",
            platform="google_meet",
            user_id=user.id,
        )
        db.add(meeting)
        await db.flush()
        meet_id = meeting.id

        part = MeetingParticipant(
            meeting_id=meet_id,
            name="Sarah Jenkins",
        )
        db.add(part)
        await db.flush()

        speaker = MeetingSpeaker(
            meeting_id=meet_id,
            speaker_label="speaker_sarah",
            participant_id=part.id,
            display_name="Sarah Jenkins",
            source_id=0,
            is_identified=True,
        )
        db.add(speaker)
        await db.flush()

        # Step 07 Transcripts
        db.add(
            TranscriptSegment(
                meeting_id=meet_id,
                speaker_id=speaker.id,
                start_time_ms=0,
                end_time_ms=20000,
                duration_ms=20000,
                text="We are currently demonstrating our production report generation pipeline across all multi-tenant boundaries.",
            )
        )

        # Step 08 Analysis
        session = AnalysisSession(
            user_id=user.id,
            meeting_id=meet_id,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()

        pa = ParticipantAnalysis(
            analysis_session_id=session.id,
            speaker_label="speaker_sarah",
            participant_id=part.id,
            status="completed",
            overall_score=84.0,
            analysis_confidence=0.94,
        )
        db.add(pa)
        await db.flush()

        db.add(AnalysisCategoryScore(participant_analysis_id=pa.id, category="Grammar", score=86.0))
        db.add(AnalysisCategoryScore(participant_analysis_id=pa.id, category="Vocabulary", score=88.0))
        db.add(AnalysisCategoryScore(participant_analysis_id=pa.id, category="Fluency", score=82.0))

        db.add(
            GrammarIssue(
                participant_analysis_id=pa.id,
                category="prepositions",
                original_text="across all multi-tenant boundaries",
                corrected_text="within all multi-tenant boundaries",
                explanation="Refine boundary preposition for technical accuracy.",
                severity="low",
            )
        )

        # Step 09 Pronunciation
        pra = PronunciationAssessment(
            meeting_id=meet_id,
            participant_id=part.id,
            speaker_label="speaker_sarah",
            assessment_status="completed",
            overall_pronunciation_score=84.0,
            evidence_confidence=0.92,
            evaluated_word_count=15,
            processing_started_at=datetime.now(timezone.utc),
        )
        db.add(pra)
        await db.flush()

        db.add(
            PronunciationWordResult(
                assessment_id=pra.id,
                word_text="demonstrating",
                start_time_ms=2000,
                end_time_ms=2800,
                duration_ms=800,
                expected_phonemes="d ɛ m ə n s t r eɪ t ɪ ŋ",
                observed_phonetic_evidence="d ɛ m ɒ n s t r eɪ t ɪ ŋ",
                pronunciation_score=74.0,
            )
        )

        db.add(
            IELTSSpeakingPracticeAssessment(
                assessment_id=pra.id,
                overall_practice_estimate=7.5,
                fluency_coherence_estimate=7.5,
                lexical_resource_estimate=8.0,
                grammatical_accuracy_estimate=7.5,
                pronunciation_estimate=7.0,
                qualitative_band_descriptor="Good User (Band 7.5 Practice Estimate)",
            )
        )
        await db.commit()

        # 4. Run Orchestrator
        orch_res = await ReportOrchestrator.generate_meeting_reports(
            db=db,
            meeting_id=meet_id,
            user_id=user.id,
            force_regenerate=False,
        )
        assert orch_res.meeting_summary_snapshot is not None
        assert len(orch_res.participant_snapshots) == 1
        summary_snap = orch_res.meeting_summary_snapshot
        part_snap = orch_res.participant_snapshots[0]

        print(f"[4/6] Report Snapshots generated successfully (Meeting ID: {meet_id[:8]}).")
        print(f"      - Summary Version: {summary_snap.report_version}")
        print(f"      - Participant Overall Score: {part_snap.overall_score}/100")
        print(f"      - Status: {part_snap.report_status}")

        # 5. Export Validation
        csv_out = await ReportExportService.export_csv(db, part_snap, user.id)
        assert "FluentMeet AI - Individual English Assessment Report" in csv_out
        assert "Sarah Jenkins" in csv_out

        html_out = await ReportExportService.export_html(db, part_snap, user.id)
        assert MANDATORY_IELTS_DISCLAIMER in html_out, "Mandatory IELTS disclaimer missing from HTML report!"
        assert "Sarah Jenkins" in html_out
        print("[5/6] Export Service verified (CSV + HTML print view with mandatory IELTS disclaimer).")

        # 6. Analytics & Dashboard Summary
        summary = await DashboardAnalyticsService.get_dashboard_summary(db)
        assert summary.total_meetings_analyzed >= 1
        assert summary.average_english_score is not None

        history = await HistoricalProgressService.get_participant_history(db, part.id)
        assert history.participant_id == part.id
        print("[6/6] Dashboard Analytics & Historical Progress Service verified.")

    print("\n" + "=" * 70)
    print("STEP 10 VERIFICATION COMPLETED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_verification())
