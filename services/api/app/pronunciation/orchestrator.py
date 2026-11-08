"""
FluentMeet AI - Step 09: Pronunciation Analysis & IELTS Assessment Orchestrator
Coordinates end-to-end spoken English assessment:
1. Audio evidence validation & signal quality verification
2. Dual-track audio routing (local_mic vs remote_mix) & overlap filtering
3. Word-level acoustic alignment and PCM buffer slicing
4. Acoustic-phonetic evaluation & spectral analysis
5. Prosody (F0 contour, pitch, intonation, syllable stress) & speaking pace (WPM, pauses)
6. Accent-neutral intelligibility assessment
7. Deterministic pronunciation scoring & evidence gating
8. 4-Dimension IELTS-style speaking practice assessment with educational disclaimer
9. Personalized pronunciation exercises & contextual feedback
10. Multi-tenant database persistence & Redis event publishing
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.base import get_utc_now
from app.models.transcript import MeetingSpeaker, TranscriptSegment, TranscriptWord
from app.models.audio import AudioSegment, AudioStream
from app.models.analysis import ParticipantAnalysis, AnalysisCategoryScore
from app.models.pronunciation import (
    PronunciationAssessment,
    PronunciationWordResult,
    PronunciationPhonemeResult,
    PronunciationProsodyResult,
    PronunciationRecommendation,
    IELTSSpeakingPracticeAssessment,
    AssessmentModelRun,
)

from app.audio.storage.object_storage import ObjectStorageService
from app.events.publisher import RedisEventPublisher
from app.analysis.gemini.client import GeminiClient

from app.pronunciation.validation.evidence_validator import AudioEvidenceValidator, AudioQualityReport
from app.pronunciation.validation.speaker_resolver import SpeakerAudioResolver, ResolvedSpeakerAudio
from app.pronunciation.alignment.word_aligner import WordAlignmentProcessor, AlignedWordAudio
from app.pronunciation.acoustic.phonetics import PhoneticAnalysisEngine, WordPronunciationEvidence
from app.pronunciation.acoustic.prosody import ProsodyAnalysisEngine, ProsodyReport
from app.pronunciation.acoustic.pace import SpeakingPaceAnalyzer, SpeakingPaceReport
from app.pronunciation.acoustic.intelligibility import IntelligibilityAnalyzer, IntelligibilityReport
from app.pronunciation.scoring.pronunciation_scorer import PronunciationScorer, PronunciationScoreResult
from app.pronunciation.scoring.ielts_engine import IELTSAssessmentEngine, IELTSEstimateResult
from app.pronunciation.feedback.recommendation_generator import PronunciationRecommendationGenerator, PronunciationExercise
from app.pronunciation.feedback.gemini_feedback import PronunciationFeedbackEngine

logger = logging.getLogger("pronunciation.orchestrator")


class PronunciationOrchestrator:
    """
    Main orchestrator for Step 09 Pronunciation & IELTS-Style English Assessment Engine.
    """

    def __init__(
        self,
        storage_service: Optional[ObjectStorageService] = None,
        gemini_client: Optional[GeminiClient] = None,
        event_publisher: Optional[RedisEventPublisher] = None,
    ):
        self.storage = storage_service or ObjectStorageService()
        self.gemini = gemini_client or GeminiClient()
        self.publisher = event_publisher or RedisEventPublisher()

        self.validator = AudioEvidenceValidator(self.storage)
        self.resolver = SpeakerAudioResolver()
        self.aligner = WordAlignmentProcessor()
        self.phonetics_engine = PhoneticAnalysisEngine()
        self.prosody_engine = ProsodyAnalysisEngine()
        self.pace_analyzer = SpeakingPaceAnalyzer()
        self.intelligibility_analyzer = IntelligibilityAnalyzer()
        self.scorer = PronunciationScorer()
        self.ielts_engine = IELTSAssessmentEngine()
        self.rec_generator = PronunciationRecommendationGenerator()
        self.feedback_engine = PronunciationFeedbackEngine(self.gemini)

    async def run_assessment(
        self,
        db: AsyncSession,
        meeting_id: str,
        user_id: str,
        speaker_id: Optional[str] = None,
        participant_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        force_reassess: bool = False,
        audio_override_bytes: Optional[bytes] = None,
    ) -> List[PronunciationAssessment]:
        """
        Executes complete spoken English and pronunciation evaluation for meeting participant(s).
        """
        logger.info(f"Starting Pronunciation Assessment for meeting={meeting_id}, speaker={speaker_id}")
        start_mono = time.monotonic()

        # 1. Fetch target speakers
        stmt = select(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting_id)
        if speaker_id:
            stmt = stmt.where(MeetingSpeaker.id == speaker_id)
        elif participant_id:
            stmt = stmt.where(MeetingSpeaker.participant_id == participant_id)

        speakers_res = await db.execute(stmt)
        target_speakers = list(speakers_res.scalars().all())

        if not target_speakers:
            # Check if there are segments without explicit speaker records
            logger.warning(f"No specific MeetingSpeaker found for meeting={meeting_id}")
            # Fallback: check transcript segments for distinct speaker labels
            segs_res = await db.execute(
                select(TranscriptSegment)
                .where(TranscriptSegment.meeting_id == meeting_id)
                .order_by(TranscriptSegment.start_time_ms.asc())
            )
            fallback_segs = list(segs_res.scalars().all())
            if not fallback_segs:
                logger.warning(f"No transcript segments found for meeting={meeting_id}")
                return []

        # 2. Fetch all transcript segments and words for this meeting
        segments_stmt = (
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .options(selectinload(TranscriptSegment.words))
            .order_by(TranscriptSegment.start_time_ms.asc())
        )
        segments_res = await db.execute(segments_stmt)
        all_segments = list(segments_res.scalars().all())

        # 3. Fetch all audio segments for this meeting
        audio_stmt = (
            select(AudioSegment)
            .where(AudioSegment.meeting_id == meeting_id)
            .order_by(AudioSegment.start_timestamp.asc())
        )
        audio_res = await db.execute(audio_stmt)
        all_audio_segments = list(audio_res.scalars().all())

        # 4. Fetch Step 08 participant analysis if available for IELTS synthesis
        p_analysis_stmt = select(ParticipantAnalysis).where(
            ParticipantAnalysis.speaker_id.in_([s.id for s in target_speakers])
            if target_speakers
            else ParticipantAnalysis.speaker_id.isnot(None)
        ).options(selectinload(ParticipantAnalysis.category_scores))
        p_analysis_res = await db.execute(p_analysis_stmt)
        step08_analyses = {pa.speaker_id: pa for pa in p_analysis_res.scalars().all()}

        assessments: List[PronunciationAssessment] = []

        # If no speakers table rows, synthesize virtual speaker from segments
        if not target_speakers and all_segments:
            distinct_labels = {seg.speaker_id or "speaker_user_me" for seg in all_segments}
            target_speakers = [
                MeetingSpeaker(
                    id=lbl,
                    meeting_id=meeting_id,
                    speaker_label=lbl,
                    source_id=0 if "me" in lbl or "local" in lbl else 1,
                )
                for lbl in distinct_labels
            ]

        for speaker in target_speakers:
            s_label = speaker.speaker_label or f"speaker_{speaker.id}"

            # Check existing assessment
            existing_res = await db.execute(
                select(PronunciationAssessment)
                .where(
                    and_(
                        PronunciationAssessment.meeting_id == meeting_id,
                        PronunciationAssessment.speaker_label == s_label,
                    )
                )
                .order_by(PronunciationAssessment.created_at.desc())
            )
            existing_assessment = existing_res.scalars().first()

            if (
                existing_assessment
                and existing_assessment.assessment_status == "completed"
                and not force_reassess
            ):
                logger.info(f"Returning existing completed assessment {existing_assessment.id} for {s_label}")
                assessments.append(existing_assessment)
                continue

            # Initialize or reuse assessment record
            if existing_assessment:
                assessment = existing_assessment
                assessment.assessment_status = "analyzing"
                assessment.processing_started_at = get_utc_now()
                # Clear previous child entities for clean idempotency
                await db.execute(
                    delete(PronunciationWordResult).where(
                        PronunciationWordResult.assessment_id == assessment.id
                    )
                )
                await db.execute(
                    delete(PronunciationProsodyResult).where(
                        PronunciationProsodyResult.assessment_id == assessment.id
                    )
                )
                await db.execute(
                    delete(PronunciationRecommendation).where(
                        PronunciationRecommendation.assessment_id == assessment.id
                    )
                )
                await db.execute(
                    delete(IELTSSpeakingPracticeAssessment).where(
                        IELTSSpeakingPracticeAssessment.assessment_id == assessment.id
                    )
                )
                await db.execute(
                    delete(AssessmentModelRun).where(
                        AssessmentModelRun.assessment_id == assessment.id
                    )
                )
                await db.flush()
            else:
                assessment = PronunciationAssessment(
                    meeting_id=meeting_id,
                    participant_id=speaker.participant_id or participant_id,
                    speaker_id=speaker.id,
                    speaker_label=s_label,
                    assessment_status="analyzing",
                    audio_quality_status="suitable",
                    scoring_version="1.0",
                    processing_started_at=get_utc_now(),
                )
                db.add(assessment)
                await db.flush()

            # Filter segments belonging to this speaker
            speaker_segs = [
                seg
                for seg in all_segments
                if (seg.speaker_id == speaker.id or seg.speaker_id == s_label)
            ]

            if not speaker_segs:
                assessment.assessment_status = "insufficient_evidence"
                assessment.audio_quality_status = "insufficient_speech"
                assessment.overall_pronunciation_score = None
                assessment.evidence_coverage = 0.0
                assessment.evidence_confidence = 0.5
                assessment.processing_completed_at = get_utc_now()
                assessment.error_message_safe = "No speech segments found for speaker."
                await db.commit()
                assessments.append(assessment)
                continue

            # Resolve audio source routing
            resolved_source: ResolvedSpeakerAudio = self.resolver.resolve_speaker_source(
                speaker_label=s_label,
                speaker_id=speaker.id,
                participant_id=speaker.participant_id,
                source_id=speaker.source_id,
                diarization_confidence=speaker.confidence_score,
                has_local_mic_audio=any(a.source_id == 1 for a in all_audio_segments),
            )

            # Match audio segments to speaker track
            matching_audio_segs = [
                a for a in all_audio_segments if a.source_id == resolved_source.source_id
            ]
            if not matching_audio_segs:
                # Fallback to any audio segment for this meeting
                matching_audio_segs = all_audio_segments

            # Load audio buffer
            speaker_pcm_buffers: List[bytes] = []
            audio_status = "suitable"
            snr_db = 22.0
            clipping_ratio = 0.001

            if audio_override_bytes:
                speaker_pcm_buffers.append(audio_override_bytes)
            else:
                for a_seg in matching_audio_segs:
                    if a_seg.storage_key:
                        is_valid, err, pcm_bytes = self.validator.validate_audio_reference(a_seg.storage_key)
                        if is_valid and pcm_bytes:
                            speaker_pcm_buffers.append(pcm_bytes)

            if not speaker_pcm_buffers:
                logger.warning(f"No physical audio buffer accessible for speaker={s_label}")
                assessment.assessment_status = "insufficient_evidence"
                assessment.audio_quality_status = "audio_missing"
                assessment.overall_pronunciation_score = None
                assessment.evidence_coverage = 0.0
                assessment.evidence_confidence = 0.5
                assessment.processing_completed_at = get_utc_now()
                assessment.error_message_safe = "Acoustic audio evidence was missing or inaccessible."
                db.add(
                    AssessmentModelRun(
                        assessment_id=assessment.id,
                        model_name="AudioEvidenceValidator",
                        model_version="1.0",
                        model_configuration={"source_id": resolved_source.source_id},
                        processing_status="insufficient_evidence",
                        processing_duration_ms=int((time.monotonic() - start_mono) * 1000),
                        error_code="AUDIO_MISSING",
                    )
                )
                await db.commit()
                assessments.append(assessment)
                continue

            # Concatenate or analyze primary acoustic PCM buffer
            combined_pcm = b"".join(speaker_pcm_buffers)
            quality_report: AudioQualityReport = self.validator.analyze_audio_quality(combined_pcm)
            audio_status = quality_report.status
            snr_db = quality_report.snr_db
            clipping_ratio = quality_report.clipping_ratio
            assessment.audio_quality_status = audio_status

            # Word Alignment & Acoustic Slicing
            aligned_words: List[AlignedWordAudio] = []
            for seg in speaker_segs:
                # Collect words from relationship or JSON
                raw_words = seg.words or []
                if not raw_words and seg.words_json:
                    raw_words = [
                        type("Obj", (), w) if isinstance(w, dict) else w
                        for w in seg.words_json
                    ]

                storage_ref = matching_audio_segs[0].storage_key if matching_audio_segs else None
                seg_aligned = self.aligner.align_words_to_audio(
                    words_data=raw_words,
                    segment_id=seg.id,
                    segment_start_ms=seg.start_time_ms,
                    segment_end_ms=seg.end_time_ms,
                    audio_storage_key=storage_ref,
                    speaker_label=s_label,
                    segment_pcm_bytes=combined_pcm,
                )
                aligned_words.extend(seg_aligned)

            # Phonetic Analysis on Aligned Words
            word_evidences: List[WordPronunciationEvidence] = []
            for aw in aligned_words:
                we = self.phonetics_engine.analyze_word(aw)
                word_evidences.append(we)

            # Prosody & Intonation Analysis
            prosody_report: ProsodyReport = self.prosody_engine.analyze_prosody(
                pcm_bytes=combined_pcm,
                words_count=len(aligned_words),
            )

            # Speaking Pace Analysis
            word_timestamps = [
                {"start_ms": aw.start_time_ms, "end_ms": aw.end_time_ms}
                for aw in aligned_words
                if aw.duration_ms > 0
            ]
            total_speech_duration_ms = (
                max((aw.end_time_ms for aw in aligned_words), default=0)
                - min((aw.start_time_ms for aw in aligned_words), default=0)
            )
            pace_report: SpeakingPaceReport = self.pace_analyzer.analyze_pace(
                word_timestamps=word_timestamps,
                total_duration_ms=max(total_speech_duration_ms, 1000),
            )

            # Accent-Neutral Intelligibility Evaluation
            avg_word_conf = (
                sum(aw.confidence for aw in aligned_words) / len(aligned_words)
                if aligned_words
                else 0.8
            )
            avg_phoneme_sc = (
                sum(we.pronunciation_score for we in word_evidences if we.evaluation_status == "evaluated")
                / max(1, sum(1 for we in word_evidences if we.evaluation_status == "evaluated"))
            )
            intelligibility_report: IntelligibilityReport = self.intelligibility_analyzer.analyze_intelligibility(
                avg_phoneme_score=avg_phoneme_sc,
                avg_word_confidence=avg_word_conf,
                snr_db=snr_db,
                clipping_ratio=clipping_ratio,
                evaluated_words_count=len([we for we in word_evidences if we.evaluation_status == "evaluated"]),
            )

            # Deterministic Pronunciation Scoring Gate
            score_result: PronunciationScoreResult = self.scorer.calculate_scores(
                word_evidences=word_evidences,
                prosody=prosody_report,
                pace=pace_report,
                intelligibility=intelligibility_report,
            )

            # IELTS-Style Practice Estimation (Synthesizing Step 08 evidence)
            s08_analysis = step08_analyses.get(speaker.id)
            fluency_s = None
            lexical_s = None
            grammar_s = None
            if s08_analysis and s08_analysis.category_scores:
                for cs in s08_analysis.category_scores:
                    if cs.category == "fluency":
                        fluency_s = cs.score
                    elif cs.category == "vocabulary":
                        lexical_s = cs.score
                    elif cs.category == "grammar":
                        grammar_s = cs.score

            ielts_result: IELTSEstimateResult = self.ielts_engine.generate_assessment(
                pronunciation_score=score_result.overall_score,
                fluency_score=fluency_s or pace_report.speaking_pace_score,
                vocabulary_score=lexical_s,
                grammar_score=grammar_s,
                confidence=score_result.evidence_confidence,
                evidence_coverage=score_result.evidence_coverage,
            )

            # Recommendations Generation
            exercises: List[PronunciationExercise] = self.rec_generator.generate_recommendations(
                word_evidences=word_evidences,
                prosody=prosody_report,
                pace=pace_report,
            )

            # Persist Assessment Entity
            assessment.assessment_status = score_result.assessment_status
            assessment.overall_pronunciation_score = score_result.overall_score
            assessment.evidence_confidence = score_result.evidence_confidence
            assessment.evidence_coverage = score_result.evidence_coverage
            assessment.evaluated_word_count = score_result.evaluated_word_count
            assessment.excluded_word_count = score_result.excluded_word_count
            assessment.processing_completed_at = get_utc_now()
            assessment.error_message_safe = score_result.explanation if score_result.overall_score is None else None

            # Persist Word and Phoneme Results
            for we in word_evidences:
                w_record = PronunciationWordResult(
                    assessment_id=assessment.id,
                    word_text=we.word_text,
                    start_time_ms=we.start_time_ms,
                    end_time_ms=we.end_time_ms,
                    duration_ms=we.duration_ms,
                    audio_segment_reference=we.audio_segment_reference,
                    expected_phonemes=we.expected_phonemes,
                    observed_phonetic_evidence=we.observed_phonemes,
                    pronunciation_score=we.pronunciation_score,
                    confidence=we.confidence,
                    evaluation_status=we.evaluation_status,
                    exclusion_reason=we.exclusion_reason,
                )
                db.add(w_record)
                await db.flush()

                for ph in we.phonemes:
                    p_record = PronunciationPhonemeResult(
                        word_result_id=w_record.id,
                        phoneme_reference=ph.phoneme_reference,
                        phoneme_evidence=ph.phoneme_evidence,
                        phoneme_score=ph.phoneme_score,
                        confidence=ph.confidence,
                        issue_type=ph.issue_type,
                        evaluation_status=ph.evaluation_status,
                    )
                    db.add(p_record)

            # Persist Prosody Result
            db.add(
                PronunciationProsodyResult(
                    assessment_id=assessment.id,
                    word_stress_score=prosody_report.word_stress_score,
                    sentence_stress_score=prosody_report.sentence_stress_score,
                    syllable_analysis=prosody_report.syllable_analysis,
                    pitch_features={
                        "mean_f0_hz": prosody_report.pitch_features.mean_f0_hz,
                        "min_f0_hz": prosody_report.pitch_features.min_f0_hz,
                        "max_f0_hz": prosody_report.pitch_features.max_f0_hz,
                        "pitch_range_hz": prosody_report.pitch_features.pitch_range_hz,
                        "contour_type": prosody_report.pitch_features.contour_type,
                    },
                    intonation_score=prosody_report.intonation_score,
                    speaking_pace_score=pace_report.speaking_pace_score,
                    pause_metrics=pace_report.pause_metrics,
                    intelligibility_score=intelligibility_report.intelligibility_score,
                    confidence=prosody_report.confidence,
                )
            )

            # Persist Recommendations
            for ex in exercises:
                db.add(
                    PronunciationRecommendation(
                        assessment_id=assessment.id,
                        category=ex.category,
                        title=ex.title,
                        description=ex.description,
                        evidence_reference=ex.evidence_reference,
                        expected_pronunciation=ex.expected_pronunciation,
                        suggested_exercise=ex.suggested_exercise,
                        priority=ex.priority,
                        difficulty_level=ex.difficulty_level,
                        confidence=ex.confidence,
                    )
                )

            # Persist IELTS Practice Assessment
            db.add(
                IELTSSpeakingPracticeAssessment(
                    assessment_id=assessment.id,
                    participant_id=assessment.participant_id,
                    fluency_coherence_estimate=ielts_result.fluency_coherence_estimate,
                    lexical_resource_estimate=ielts_result.lexical_resource_estimate,
                    grammatical_accuracy_estimate=ielts_result.grammatical_accuracy_estimate,
                    pronunciation_estimate=ielts_result.pronunciation_estimate,
                    overall_practice_estimate=ielts_result.overall_practice_estimate,
                    qualitative_band_descriptor=ielts_result.qualitative_band_descriptor,
                    rubric_version=ielts_result.rubric_version,
                    confidence=ielts_result.confidence,
                    evidence_coverage=ielts_result.evidence_coverage,
                    assessment_status=ielts_result.assessment_status,
                    disclaimer_version="1.0",
                    disclaimer_text=ielts_result.disclaimer_text,
                )
            )

            # Persist Model Run Audit
            duration_total_ms = int((time.monotonic() - start_mono) * 1000)
            db.add(
                AssessmentModelRun(
                    assessment_id=assessment.id,
                    model_name="PhoneticProsodyAcousticPipeline",
                    model_version="1.0",
                    model_configuration={
                        "sample_rate": 16000,
                        "source_id": resolved_source.source_id,
                        "intelligibility_class": intelligibility_report.classification,
                    },
                    processing_status="success",
                    processing_duration_ms=duration_total_ms,
                )
            )

            await db.commit()
            assessments.append(assessment)

            # Publish Redis completion event
            try:
                await self.publisher.publish_event(
                    stream_name="pronunciation:events",
                    event_type="pronunciation.completed",
                    aggregate_id=assessment.id,
                    payload={
                        "assessment_id": assessment.id,
                        "meeting_id": meeting_id,
                        "speaker_label": s_label,
                        "overall_score": score_result.overall_score,
                        "status": score_result.assessment_status,
                        "ielts_estimate": ielts_result.overall_practice_estimate,
                    },
                )
            except Exception as pe:
                logger.warning(f"Could not publish pronunciation.completed event: {pe}")

        logger.info(f"Completed Pronunciation Assessment for meeting={meeting_id}: {len(assessments)} evaluated.")
        return assessments
