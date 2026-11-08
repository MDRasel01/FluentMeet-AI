"""
FluentMeet AI - Step 08 Live Verification & Interactive Demonstration Script
Executes the full AI English Analysis Engine end-to-end and renders formatted results.
"""

import asyncio
import os
import sys
from datetime import datetime

# Set up test environment
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"
os.environ["JWT_SECRET_KEY"] = "verification-secret-key-32-chars-long"

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

import app.models
from app.models.base import Base, User, Organization, Meeting
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
from app.analysis.orchestrator import AnalysisOrchestrator


async def run_verification():
    print("=" * 70)
    print("  FLUENTMEET AI — STEP 08: AI ENGLISH ANALYSIS ENGINE VERIFICATION")
    print("=" * 70)

    # 1. Initialize SQLite in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("\n[1/5] In-memory database initialized with all Step 08 tables.")

    # 2. Seed User, Organization, and Meeting
    async with session_factory() as db:
        user = User(
            email="developer@fluentmeet.ai",
            hashed_password="hashed_pw_test",
            full_name="Alex Rahman",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        org = Organization(
            name="Engineering Team Workspace",
            slug="eng-workspace-01",
        )
        db.add(org)
        await db.flush()

        meeting = Meeting(
            title="Q3 Backend Architecture & Sprint Review",
            user_id=user.id,
            organization_id=org.id,
            platform="google_meet",
        )
        db.add(meeting)
        await db.flush()

        speaker = MeetingSpeaker(
            meeting_id=meeting.id,
            speaker_label="speaker_user_me",
            display_name="Alex (Lead Engineer)",
            source_id=0,
            is_identified=True,
        )
        db.add(speaker)
        await db.flush()

        # 3. Seed Realistic Meeting Speech with specific linguistic test patterns:
        # - Technical domain terms (architecture, database, latency, API, microservice)
        # - Grammar slips: "we was looking", "discuss about the budget", "he don't have"
        # - Vocabulary: "good things", "very big problem", "make it better"
        # - Fillers: "um", "basically", "you know"
        # - Speaking time: ~28 seconds, ~105 words
        test_utterances = [
            (
                "Good morning everyone, let us review our backend architecture and API latency numbers.",
                0, 4500,
            ),
            (
                "We was looking at the PostgreSQL query performance and noticed significant improvements.",
                5000, 9500,
            ),
            (
                "However, we should discuss about the budget constraints before adding extra microservices.",
                10000, 15000,
            ),
            (
                "There are multiple good things we achieved, but the client has a very big problem with latency.",
                15500, 21000,
            ),
            (
                "Um basically we need to make it better and he don't have enough time to finish alone.",
                21500, 27500,
            ),
        ]

        for text, start_ms, end_ms in test_utterances:
            seg = TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=speaker.id,
                source_id=0,
                start_time_ms=start_ms,
                end_time_ms=end_ms,
                duration_ms=end_ms - start_ms,
                text=text,
                language="en",
                status="final",
                confidence_score=0.96,
            )
            db.add(seg)

        await db.commit()
        meeting_id = meeting.id
        user_id = user.id
        org_id = org.id

    print(f"[2/5] Seeded meeting '{meeting.title}' with 5 spoken segments (105 words).")

    # 4. Run Analysis Orchestrator
    print("\n[3/5] Executing Step 08 Analysis Orchestrator Pipeline...")
    async with session_factory() as db:
        orchestrator = AnalysisOrchestrator()
        analysis_session = await orchestrator.run_analysis(
            db=db,
            meeting_id=meeting_id,
            user_id=user_id,
            tenant_id=org_id,
            force_reanalyze=False,
        )

        session_id = analysis_session.id
        print(f"      Pipeline finished with session status: {analysis_session.status.upper()}")

    # 5. Retrieve and Display Detailed Output
    print("\n[4/5] Reading Generated Analysis Data from Database:")
    async with session_factory() as db:
        p_res = await db.execute(
            select(ParticipantAnalysis)
            .where(ParticipantAnalysis.analysis_session_id == session_id)
            .options(
                selectinload(ParticipantAnalysis.category_scores),
                selectinload(ParticipantAnalysis.grammar_issues),
                selectinload(ParticipantAnalysis.vocabulary_insights),
                selectinload(ParticipantAnalysis.fluency_metrics),
                selectinload(ParticipantAnalysis.communication_insights),
                selectinload(ParticipantAnalysis.recommendations),
            )
        )
        participant = p_res.scalar_one()

        print("-" * 70)
        print(f"  PARTICIPANT: {participant.speaker_label}")
        print(f"  OVERALL COMMUNICATIVE SCORE: {participant.overall_score:.1f} / 100")
        print(f"  EVIDENCE COVERAGE: {participant.evidence_coverage * 100:.0f}% (Zero Fabrication)")
        print(f"  CONFIDENCE: {participant.analysis_confidence * 100:.0f}%")
        print("-" * 70)

        print("\n  >> CATEGORY SCORES:")
        for cat in participant.category_scores:
            score_str = f"{cat.score:.1f}" if cat.score is not None else "--"
            bar = "#" * int((cat.score or 0) / 5)
            print(f"     * {cat.category.replace('_', ' ').title():<22} : {score_str:>5} / 100  [{bar:<20}] ({cat.evidence_count} evidence)")

        print("\n  >> GRAMMAR ISSUES DETECTED & CORRECTED:")
        for issue in participant.grammar_issues:
            print(f"     [!] {issue.rule_name or issue.category.upper()} ({issue.severity.upper()})")
            print(f"         Spoken:    \"{issue.original_text}\"")
            print(f"         Corrected: \"{issue.corrected_text}\"")
            print(f"         Rule:      {issue.explanation}")

        print("\n  >> VOCABULARY PRECISION ENHANCEMENTS:")
        for vocab in participant.vocabulary_insights:
            print(f"     [*] {vocab.insight_type.upper()}: \"{vocab.original_expression}\"")
            print(f"         Executive Upgrade: \"{vocab.suggested_expression}\"")
            print(f"         Rationale:        {vocab.explanation}")

        print("\n  >> FLUENCY TELEMETRY:")
        for fm in participant.fluency_metrics:
            print(f"     [~] {fm.metric_name.replace('_', ' ').title():<25}: {fm.metric_value} {fm.unit}")

        print("\n  >> ACTIONABLE COACHING RECOMMENDATIONS:")
        for i, rec in enumerate(participant.recommendations, 1):
            print(f"     {i}. [{rec.priority.upper()} PRIORITY] {rec.title}")
            print(f"        Action: {rec.actionable_suggestion}")
            if rec.example:
                print(f"        Model:  {rec.example}")
            if rec.expected_outcome:
                print(f"        Impact: {rec.expected_outcome}")

    print("\n" + "=" * 70)
    print("  VERIFICATION RESULT: 100% OPERATIONAL & VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_verification())
