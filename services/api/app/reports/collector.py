"""
FluentMeet AI - Step 10: Multi-Source Report Data Collector
Gathers data from Step 06 (Audio), Step 07 (Transcript/Diarization), Step 08 (AI English Analysis), and Step 09 (Pronunciation/IELTS).
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.base import Meeting, MeetingParticipant
from app.models.transcript import MeetingSpeaker, TranscriptSegment, TranscriptWord
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


class CollectedParticipantData:
    """Encapsulates all raw data gathered for an individual participant."""
    def __init__(self, speaker_label: str, participant_id: Optional[str] = None):
        self.speaker_label = speaker_label
        self.participant_id = participant_id
        self.display_name: str = speaker_label
        
        # Step 07 Transcript Stats
        self.total_words: int = 0
        self.speaking_duration_seconds: float = 0.0
        self.transcript_segments: List[Dict[str, Any]] = []
        
        # Step 08 English Analysis Data
        self.analysis_status: Optional[str] = None
        self.grammar_score: Optional[float] = None
        self.vocabulary_score: Optional[float] = None
        self.fluency_score: Optional[float] = None
        self.communication_score: Optional[float] = None
        self.step08_overall_score: Optional[float] = None
        self.step08_confidence: Optional[float] = None
        self.grammar_issues: List[Dict[str, Any]] = []
        self.vocabulary_insights: Optional[Dict[str, Any]] = None
        self.fluency_metrics: Optional[Dict[str, Any]] = None
        self.step08_recommendations: List[Dict[str, Any]] = []
        
        # Step 09 Pronunciation & IELTS Data
        self.pronunciation_status: Optional[str] = None
        self.pronunciation_score: Optional[float] = None
        self.step09_confidence: Optional[float] = None
        self.step09_coverage: float = 1.0
        self.mispronounced_words: List[Dict[str, Any]] = []
        self.prosody: Optional[Dict[str, Any]] = None
        self.ielts_assessment: Optional[Dict[str, Any]] = None
        self.pronunciation_recommendations: List[Dict[str, Any]] = []


class ReportDataCollector:
    """
    Collects and validates inputs from all previous pipeline steps.
    """

    @classmethod
    async def collect_meeting_data(cls, db: AsyncSession, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Gathers meeting metadata, speakers, transcripts, analyses, and pronunciation assessments.
        """
        res = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = res.scalar_one_or_none()
        if not meeting:
            return None

        # Fetch speakers & participants
        res = await db.execute(select(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting_id))
        speakers = res.scalars().all()
        speaker_map = {s.speaker_label: s for s in speakers}
        speaker_id_to_label = {s.id: s.speaker_label for s in speakers}

        res = await db.execute(select(MeetingParticipant).where(MeetingParticipant.meeting_id == meeting_id))
        participants = res.scalars().all()
        participant_map = {p.id: p for p in participants}

        # Step 07 Transcripts
        res = await db.execute(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.start_time_ms.asc())
        )
        segments = res.scalars().all()

        # Step 08 Analysis Session & Participant Analysis
        res = await db.execute(
            select(AnalysisSession)
            .where(
                AnalysisSession.meeting_id == meeting_id,
                AnalysisSession.status == "completed"
            )
            .order_by(AnalysisSession.completed_at.desc())
        )
        analysis_session = res.scalars().first()

        participant_analyses = []
        if analysis_session:
            res = await db.execute(
                select(ParticipantAnalysis).where(ParticipantAnalysis.analysis_session_id == analysis_session.id)
            )
            participant_analyses = res.scalars().all()

        # Step 09 Pronunciation Assessments
        res = await db.execute(
            select(PronunciationAssessment).where(
                PronunciationAssessment.meeting_id == meeting_id,
                PronunciationAssessment.assessment_status.in_(["completed", "partial", "insufficient_evidence"])
            )
        )
        pron_assessments = res.scalars().all()

        # Build raw participant data registry
        speaker_labels = set(speaker_map.keys())
        for seg in segments:
            lbl = speaker_id_to_label.get(seg.speaker_id)
            if lbl:
                speaker_labels.add(lbl)
        for pa in participant_analyses:
            speaker_labels.add(pa.speaker_label)
        for pra in pron_assessments:
            speaker_labels.add(pra.speaker_label)

        participant_data_dict: Dict[str, CollectedParticipantData] = {}
        for label in speaker_labels:
            spk = speaker_map.get(label)
            part_id = spk.participant_id if spk and spk.participant_id else None
            data = CollectedParticipantData(speaker_label=label, participant_id=part_id)
            if spk and spk.display_name:
                data.display_name = spk.display_name
            elif part_id and part_id in participant_map and participant_map[part_id].name:
                data.display_name = participant_map[part_id].name
            participant_data_dict[label] = data

        # Populate transcript stats
        for seg in segments:
            lbl = speaker_id_to_label.get(seg.speaker_id)
            pdata = participant_data_dict.get(lbl) if lbl else None
            if pdata:
                seg_words = len(seg.text.split()) if seg.text else 0
                pdata.total_words += seg_words
                dur_s = max(0.0, (seg.end_time_ms - seg.start_time_ms) / 1000.0)
                pdata.speaking_duration_seconds += dur_s
                pdata.transcript_segments.append({
                    "start_time_ms": seg.start_time_ms,
                    "end_time_ms": seg.end_time_ms,
                    "text": seg.text,
                })

        # Populate Step 08 data
        for pa in participant_analyses:
            pdata = participant_data_dict.get(pa.speaker_label)
            if not pdata:
                continue
            pdata.analysis_status = pa.status
            pdata.step08_overall_score = pa.overall_score
            pdata.step08_confidence = pa.analysis_confidence
            if pa.participant_id and not pdata.participant_id:
                pdata.participant_id = pa.participant_id

            # Category scores
            res = await db.execute(
                select(AnalysisCategoryScore).where(
                    AnalysisCategoryScore.participant_analysis_id == pa.id
                )
            )
            cat_scores = res.scalars().all()
            for cs in cat_scores:
                cat_lower = cs.category.lower()
                if "grammar" in cat_lower:
                    pdata.grammar_score = cs.score
                elif "vocabulary" in cat_lower:
                    pdata.vocabulary_score = cs.score
                elif "fluency" in cat_lower:
                    pdata.fluency_score = cs.score
                elif "communication" in cat_lower or "clarity" in cat_lower:
                    pdata.communication_score = cs.score

            # Grammar issues
            res = await db.execute(
                select(GrammarIssue).where(GrammarIssue.participant_analysis_id == pa.id)
            )
            issues = res.scalars().all()
            for gi in issues:
                pdata.grammar_issues.append({
                    "id": gi.id,
                    "rule_type": getattr(gi, "category", None) or getattr(gi, "rule_name", None) or "grammar",
                    "offending_text": getattr(gi, "original_text", ""),
                    "corrected_text": gi.corrected_text,
                    "explanation": gi.explanation,
                    "severity": gi.severity,
                })

            # Vocabulary insights
            res = await db.execute(
                select(VocabularyInsight).where(VocabularyInsight.participant_analysis_id == pa.id)
            )
            v_items = res.scalars().all()
            if v_items:
                pdata.vocabulary_insights = {
                    "lexical_diversity": None,
                    "high_impact_words": [v.suggested_expression for v in v_items if getattr(v, "insight_type", "") == "business_expression"],
                    "repetitive_words": [v.original_expression for v in v_items if getattr(v, "insight_type", "") in ("overused", "repetition")],
                }

            # Fluency metrics
            res = await db.execute(
                select(FluencyMetric).where(FluencyMetric.participant_analysis_id == pa.id)
            )
            f_items = res.scalars().all()
            if f_items:
                f_map = {f.metric_name: f.metric_value for f in f_items}
                pdata.fluency_metrics = {
                    "words_per_minute": f_map.get("speech_rate_wpm", 0.0),
                    "filler_word_count": int(f_map.get("filler_word_rate", 0)),
                    "pause_count": int(f_map.get("pause_frequency", 0)),
                    "speech_rate_category": "moderate",
                }

            # Recommendations
            res = await db.execute(
                select(ImprovementRecommendation).where(
                    ImprovementRecommendation.participant_analysis_id == pa.id
                )
            )
            recs = res.scalars().all()
            for r in recs:
                pdata.step08_recommendations.append({
                    "category": getattr(r, "skill_category", "General"),
                    "priority": r.priority,
                    "recommendation_text": f"{getattr(r, 'title', '')}: {getattr(r, 'actionable_suggestion', '')}".strip(": "),
                })

        # Populate Step 09 data
        for pra in pron_assessments:
            pdata = participant_data_dict.get(pra.speaker_label)
            if not pdata:
                continue
            pdata.pronunciation_status = pra.assessment_status
            pdata.pronunciation_score = pra.overall_pronunciation_score
            pdata.step09_confidence = pra.evidence_confidence
            pdata.step09_coverage = pra.evidence_coverage or 1.0
            if pra.participant_id and not pdata.participant_id:
                pdata.participant_id = pra.participant_id

            # Word results
            res = await db.execute(
                select(PronunciationWordResult).where(
                    PronunciationWordResult.assessment_id == pra.id
                )
            )
            words = res.scalars().all()
            for w in words:
                score = getattr(w, "pronunciation_score", None)
                if score is not None and score < 80.0:
                    pdata.mispronounced_words.append({
                        "word": getattr(w, "word_text", ""),
                        "accuracy_score": score,
                        "phonemes_expected": getattr(w, "expected_phonemes", ""),
                        "phonemes_produced": getattr(w, "observed_phonetic_evidence", ""),
                    })

            # Prosody
            res = await db.execute(
                select(PronunciationProsodyResult).where(
                    PronunciationProsodyResult.assessment_id == pra.id
                )
            )
            pros = res.scalars().first()
            if pros:
                pitch_feat = getattr(pros, "pitch_features", {}) or {}
                pdata.prosody = {
                    "speaking_rate_wpm": getattr(pros, "speaking_pace_score", 0.0),
                    "pitch_range_hz": pitch_feat.get("pitch_range_hz", 0.0) if isinstance(pitch_feat, dict) else 0.0,
                    "sentence_stress_accuracy": getattr(pros, "sentence_stress_score", 0.0),
                    "intonation_naturalness": getattr(pros, "intonation_score", 0.0),
                }

            # IELTS practice
            res = await db.execute(
                select(IELTSSpeakingPracticeAssessment).where(
                    IELTSSpeakingPracticeAssessment.assessment_id == pra.id
                )
            )
            ielts = res.scalars().first()
            if ielts:
                pdata.ielts_assessment = {
                    "overall_band_estimate": getattr(ielts, "overall_practice_estimate", None),
                    "fluency_coherence_band": getattr(ielts, "fluency_coherence_estimate", None),
                    "lexical_resource_band": getattr(ielts, "lexical_resource_estimate", None),
                    "grammatical_range_band": getattr(ielts, "grammatical_accuracy_estimate", None),
                    "pronunciation_band": getattr(ielts, "pronunciation_estimate", None),
                    "cefr_level": "C1" if (getattr(ielts, "overall_practice_estimate", 0) or 0) >= 7.0 else "B2",
                    "band_descriptor_summary": getattr(ielts, "qualitative_band_descriptor", ""),
                }

            # Recommendations
            res = await db.execute(
                select(PronunciationRecommendation).where(
                    PronunciationRecommendation.assessment_id == pra.id
                )
            )
            precs = res.scalars().all()
            for pr in precs:
                pdata.pronunciation_recommendations.append({
                    "drill_type": getattr(pr, "category", "Phonetics"),
                    "title": pr.title,
                    "practice_text": getattr(pr, "suggested_exercise", ""),
                    "explanation": getattr(pr, "description", ""),
                })

        return {
            "meeting": meeting,
            "session": analysis_session,
            "participants_data": participant_data_dict,
            "total_segments": len(segments),
        }
