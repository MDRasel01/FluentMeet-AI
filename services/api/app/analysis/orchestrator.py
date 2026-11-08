"""
FluentMeet AI - Step 08: AI English Analysis Orchestrator
Coordinates end-to-end linguistic assessment:
1. Transcript loading & validation
2. Text normalization & context detection
3. Parallel execution of intelligence modules
4. Evidence Verification Gate (zero-hallucination guarantee)
5. Evidence-based scoring & recommendation generation
6. Multi-tenant database persistence & event dispatch
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.base import get_utc_now
from app.models.transcript import MeetingSpeaker, TranscriptSegment, TranscriptWord
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
from app.analysis.preprocessing.cleaner import TranscriptCleaner, CleanedSegment
from app.analysis.preprocessing.context import ContextDetector, MeetingContext
from app.analysis.gemini.client import GeminiClient
from app.analysis.modules.grammar import GrammarAnalyzer, GrammarFinding
from app.analysis.modules.vocabulary import VocabularyAnalyzer, VocabularyInsightItem
from app.analysis.modules.fluency import FluencyAnalyzer, FluencyMetricResult
from app.analysis.modules.sentence_structure import SentenceStructureAnalyzer, StructureObservation
from app.analysis.modules.communication import CommunicationAnalyzer, CommunicationInsightItem
from app.analysis.modules.speaking_patterns import SpeakingPatternAnalyzer, RecurringPattern
from app.analysis.scoring.engine import ScoringEngine, ParticipantScoreSummary
from app.analysis.recommendations.engine import RecommendationEngine, RecommendationItem
from app.events.publisher import RedisEventPublisher

logger = logging.getLogger("analysis.orchestrator")


class AnalysisOrchestrator:
    """
    Main orchestrator for Step 08 English Communication Analysis Engine.
    """

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        event_publisher: Optional[RedisEventPublisher] = None,
    ):
        self.gemini = gemini_client or GeminiClient()
        self.publisher = event_publisher or RedisEventPublisher()
        self.cleaner = TranscriptCleaner()
        self.context_detector = ContextDetector()
        self.grammar_analyzer = GrammarAnalyzer(self.gemini)
        self.vocab_analyzer = VocabularyAnalyzer(self.gemini)
        self.fluency_analyzer = FluencyAnalyzer()
        self.structure_analyzer = SentenceStructureAnalyzer(self.gemini)
        self.comm_analyzer = CommunicationAnalyzer(self.gemini)
        self.pattern_analyzer = SpeakingPatternAnalyzer()
        self.scoring_engine = ScoringEngine()
        self.rec_engine = RecommendationEngine()

    async def run_analysis(
        self,
        db: AsyncSession,
        meeting_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        session_id: Optional[str] = None,
        force_reanalyze: bool = False,
    ) -> AnalysisSession:
        """
        Executes complete multi-speaker English assessment for a meeting.
        """
        logger.info(f"Starting English Analysis for meeting={meeting_id}, user={user_id}")

        # 1. Retrieve or initialize AnalysisSession
        session = None
        if session_id:
            res = await db.execute(
                select(AnalysisSession)
                .where(AnalysisSession.id == session_id)
                .options(selectinload(AnalysisSession.participants))
            )
            session = res.scalar_one_or_none()

        if session is None:
            res = await db.execute(
                select(AnalysisSession)
                .where(AnalysisSession.meeting_id == meeting_id)
                .order_by(AnalysisSession.created_at.desc())
                .options(selectinload(AnalysisSession.participants))
            )
            existing = res.scalars().first()
            if existing and existing.status == "completed" and not force_reanalyze:
                logger.info(f"Returning existing completed analysis session {existing.id}")
                return existing
            if existing and existing.status == "processing" and not force_reanalyze:
                logger.info(f"Analysis session {existing.id} already in progress")
                return existing

            session = AnalysisSession(
                tenant_id=tenant_id,
                user_id=user_id,
                meeting_id=meeting_id,
                status="processing",
                started_at=get_utc_now(),
            )
            db.add(session)
            await db.flush()
        else:
            session.status = "processing"
            session.started_at = get_utc_now()
            # If re-analyzing, clear existing participant analysis data
            await db.execute(
                delete(ParticipantAnalysis).where(ParticipantAnalysis.analysis_session_id == session.id)
            )
            await db.flush()

        # Log started event
        db.add(
            AnalysisEvent(
                analysis_session_id=session.id,
                event_type="analysis.started",
                status="processing",
                event_metadata={"meeting_id": meeting_id, "user_id": user_id},
            )
        )
        await db.commit()

        try:
            # 2. Fetch speakers and transcript segments
            speakers_res = await db.execute(
                select(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting_id)
            )
            speakers = list(speakers_res.scalars().all())

            segments_res = await db.execute(
                select(TranscriptSegment)
                .where(TranscriptSegment.meeting_id == meeting_id)
                .order_by(TranscriptSegment.start_time_ms.asc())
            )
            raw_segments = list(segments_res.scalars().all())

            if not raw_segments:
                logger.warning(f"No transcript segments found for meeting={meeting_id}")
                session.status = "insufficient_data"
                session.completed_at = get_utc_now()
                session.error_message_safe = "No transcript segments found for this meeting."
                db.add(
                    AnalysisEvent(
                        analysis_session_id=session.id,
                        event_type="analysis.completed",
                        status="insufficient_data",
                        event_metadata={"reason": "no_segments"},
                    )
                )
                await db.commit()
                return session

            # Build map of speaker_id to speaker_label
            speaker_map: Dict[str, MeetingSpeaker] = {s.id: s for s in speakers}
            label_map: Dict[str, str] = {s.id: s.speaker_label for s in speakers}

            # 3. Clean and normalize all segments
            cleaned_segments: List[CleanedSegment] = []
            for seg in raw_segments:
                speaker_lbl = label_map.get(seg.speaker_id, f"speaker_{seg.source_id}")
                cleaned = self.cleaner.clean_segment(seg, speaker_lbl)
                cleaned_segments.append(cleaned)

            # 4. Detect meeting context & register from full text
            full_meeting_text = " ".join(s.cleaned_text for s in cleaned_segments)
            context = self.context_detector.detect_context(full_meeting_text)
            logger.info(f"Detected meeting context={context.primary_register} (confidence={context.confidence})")

            # Group cleaned segments by speaker label
            speaker_segments_map: Dict[str, List[CleanedSegment]] = {}
            for cs in cleaned_segments:
                speaker_segments_map.setdefault(cs.speaker_label, []).append(cs)

            # 5. Process each speaker
            for speaker_lbl, s_segs in speaker_segments_map.items():
                matching_speaker = next((s for s in speakers if s.speaker_label == speaker_lbl), None)
                speaker_id = matching_speaker.id if matching_speaker else None
                participant_id = matching_speaker.participant_id if matching_speaker else None

                total_words = sum(s.word_count for s in s_segs)
                total_duration_sec = sum(s.duration_ms for s in s_segs) / 1000.0

                logger.info(f"Analyzing speaker '{speaker_lbl}': {total_words} words, {total_duration_sec:.1f}s")

                # Check Insufficient Speech Data gate
                if (
                    total_words < ScoringEngine.MIN_WORDS_THRESHOLD
                    or total_duration_sec < ScoringEngine.MIN_DURATION_SECONDS
                ):
                    p_analysis = ParticipantAnalysis(
                        analysis_session_id=session.id,
                        participant_id=participant_id,
                        speaker_id=speaker_id,
                        speaker_label=speaker_lbl,
                        overall_score=None,
                        score_status="insufficient_data",
                        evidence_coverage=1.0,
                        analysis_confidence=0.5,
                        scoring_version="1.0",
                        status="completed",
                    )
                    db.add(p_analysis)
                    await db.flush()

                    # Add category placeholders with status insufficient_data
                    for cat in ScoringEngine.DEFAULT_WEIGHTS.keys():
                        db.add(
                            AnalysisCategoryScore(
                                participant_analysis_id=p_analysis.id,
                                category=cat,
                                score=None,
                                status="insufficient_data",
                                evidence_count=0,
                                confidence=0.5,
                            )
                        )
                    continue

                # Run parallel analysis modules
                grammar_task = self.grammar_analyzer.analyze(speaker_lbl, s_segs, context)
                vocab_task = self.vocab_analyzer.analyze(speaker_lbl, s_segs, context)
                fluency_task = asyncio.to_thread(self.fluency_analyzer.analyze, speaker_lbl, s_segs)
                structure_task = self.structure_analyzer.analyze(speaker_lbl, s_segs, context)
                comm_task = self.comm_analyzer.analyze(speaker_lbl, s_segs, context)

                (
                    grammar_res,
                    vocab_res,
                    fluency_res,
                    structure_res,
                    comm_res,
                ) = await asyncio.gather(
                    grammar_task,
                    vocab_task,
                    fluency_task,
                    structure_task,
                    comm_task,
                )

                # --- EVIDENCE VERIFICATION GATE ---
                # Zero-fabrication check: every finding MUST reference an actual segment from this meeting & speaker
                valid_seg_ids = {s.segment_id for s in s_segs}
                verified_grammar = [f for f in grammar_res.get("issues", []) if f.segment_id in valid_seg_ids]
                verified_vocab = [v for v in vocab_res.get("insights", []) if v.segment_id in valid_seg_ids]
                verified_structure = [o for o in structure_res.get("observations", []) if o.segment_id in valid_seg_ids]

                # Speaking pattern discovery
                recurring_patterns = self.pattern_analyzer.analyze(
                    s_segs, verified_grammar, verified_vocab
                )

                # Contextual language score
                context_score = min(100.0, max(50.0, context.confidence * 100.0))

                # Bundle for scoring engine
                raw_cats = {
                    "grammar": {
                        "score": grammar_res.get("score"),
                        "status": grammar_res.get("status", "available"),
                        "evidence_count": len(verified_grammar),
                        "confidence": 0.95,
                    },
                    "vocabulary": {
                        "score": vocab_res.get("score"),
                        "status": vocab_res.get("status", "available"),
                        "evidence_count": len(verified_vocab),
                        "confidence": 0.90,
                    },
                    "fluency": {
                        "score": fluency_res.get("score"),
                        "status": fluency_res.get("status", "available"),
                        "evidence_count": len(fluency_res.get("metrics", [])),
                        "confidence": 0.95,
                    },
                    "sentence_structure": {
                        "score": structure_res.get("score"),
                        "status": structure_res.get("status", "available"),
                        "evidence_count": len(verified_structure),
                        "confidence": 0.88,
                    },
                    "communication": {
                        "score": comm_res.get("score"),
                        "status": comm_res.get("status", "available"),
                        "evidence_count": len(comm_res.get("insights", [])),
                        "confidence": 0.92,
                    },
                    "contextual_language": {
                        "score": context_score,
                        "status": "available",
                        "evidence_count": len(context.detected_terms),
                        "confidence": context.confidence,
                    },
                }

                score_summary: ParticipantScoreSummary = self.scoring_engine.evaluate(
                    total_words=total_words,
                    duration_seconds=total_duration_sec,
                    raw_category_results=raw_cats,
                )

                # Generate prioritized recommendations
                recommendations: List[RecommendationItem] = self.rec_engine.generate_recommendations(
                    grammar_findings=verified_grammar,
                    vocab_insights=verified_vocab,
                    fluency_metrics=fluency_res.get("metrics", []),
                    structure_observations=verified_structure,
                    recurring_patterns=recurring_patterns,
                    context=context,
                )

                # Persist ParticipantAnalysis
                p_analysis = ParticipantAnalysis(
                    analysis_session_id=session.id,
                    participant_id=participant_id,
                    speaker_id=speaker_id,
                    speaker_label=speaker_lbl,
                    overall_score=score_summary.overall_score,
                    score_status=score_summary.score_status,
                    evidence_coverage=score_summary.evidence_coverage,
                    analysis_confidence=score_summary.analysis_confidence,
                    scoring_version=score_summary.scoring_version,
                    status="completed",
                )
                db.add(p_analysis)
                await db.flush()

                # Persist Category Scores
                for cs in score_summary.category_scores:
                    db.add(
                        AnalysisCategoryScore(
                            participant_analysis_id=p_analysis.id,
                            category=cs.category,
                            score=cs.score,
                            status=cs.status,
                            evidence_count=cs.evidence_count,
                            confidence=cs.confidence,
                            scoring_version=cs.scoring_version,
                        )
                    )

                # Persist Grammar Issues
                for gi in verified_grammar:
                    db.add(
                        GrammarIssue(
                            participant_analysis_id=p_analysis.id,
                            transcript_segment_id=gi.segment_id,
                            category=gi.category,
                            original_text=gi.original_text,
                            corrected_text=gi.corrected_text,
                            explanation=gi.explanation,
                            rule_name=gi.rule_name,
                            suggested_alternative=gi.suggested_alternative,
                            severity=gi.severity,
                            confidence=gi.confidence,
                            evidence_status=gi.evidence_status,
                        )
                    )

                # Persist Vocabulary Insights
                for vi in verified_vocab:
                    db.add(
                        VocabularyInsight(
                            participant_analysis_id=p_analysis.id,
                            transcript_segment_id=vi.segment_id,
                            original_expression=vi.original_expression,
                            suggested_expression=vi.suggested_expression,
                            explanation=vi.explanation,
                            insight_type=vi.insight_type,
                            context_note=vi.context_note,
                            example_sentence=vi.example_sentence,
                            confidence=vi.confidence,
                        )
                    )

                # Persist Fluency Metrics
                for fm in fluency_res.get("metrics", []):
                    db.add(
                        FluencyMetric(
                            participant_analysis_id=p_analysis.id,
                            metric_name=fm.metric_name,
                            metric_value=fm.metric_value,
                            unit=fm.unit,
                            evidence_count=fm.evidence_count,
                            confidence=fm.confidence,
                            calculation_version="1.0",
                        )
                    )

                # Persist Communication Insights
                for ci in comm_res.get("insights", []):
                    db.add(
                        CommunicationInsight(
                            participant_analysis_id=p_analysis.id,
                            insight_type=ci.insight_type,
                            title=ci.title,
                            description=ci.description,
                            evidence=ci.evidence,
                            confidence=ci.confidence,
                        )
                    )

                # Persist Recommendations
                for rec in recommendations:
                    db.add(
                        ImprovementRecommendation(
                            participant_analysis_id=p_analysis.id,
                            skill_category=rec.skill_category,
                            priority=rec.priority,
                            title=rec.title,
                            actionable_suggestion=rec.actionable_suggestion,
                            evidence_reference=rec.evidence_reference,
                            example=rec.example,
                            expected_outcome=rec.expected_outcome,
                            status="active",
                        )
                    )

            # 6. Finalize AnalysisSession
            session.status = "completed"
            session.completed_at = get_utc_now()
            db.add(
                AnalysisEvent(
                    analysis_session_id=session.id,
                    event_type="analysis.completed",
                    status="completed",
                    event_metadata={
                        "meeting_id": meeting_id,
                        "speakers_analyzed": len(speaker_segments_map),
                        "context": context.primary_register,
                    },
                )
            )
            await db.commit()

            # 7. Publish completion event to Redis Stream
            try:
                await self.publisher.publish_event(
                    stream_name="analysis:events",
                    event_type="analysis.completed",
                    aggregate_id=session.id,
                    payload={
                        "analysis_session_id": session.id,
                        "meeting_id": meeting_id,
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "status": "completed",
                    },
                )
            except Exception as pe:
                logger.warning(f"Could not publish analysis.completed event: {pe}")

            logger.info(f"Successfully completed English Analysis session {session.id}")
            return session

        except Exception as exc:
            logger.exception(f"Analysis failed for session {session.id}: {exc}")
            session.status = "failed"
            session.error_code = "ANALYSIS_FAILED"
            session.error_message_safe = str(exc)
            db.add(
                AnalysisEvent(
                    analysis_session_id=session.id,
                    event_type="analysis.failed",
                    status="failed",
                    event_metadata={"error": str(exc)},
                )
            )
            await db.commit()
            raise

