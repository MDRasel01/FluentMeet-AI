"""
FluentMeet AI - Step 09: Pydantic Schemas for Pronunciation & IELTS Assessment
Specification: Step 09 - Section 20 & 22
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TriggerPronunciationRequest(BaseModel):
    meeting_id: Optional[str] = None
    speaker_id: Optional[str] = None
    participant_id: Optional[str] = None
    force_reassess: bool = False


class PhonemeResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phoneme_reference: str
    phoneme_evidence: Optional[str] = None
    phoneme_score: Optional[float] = None
    confidence: Optional[float] = None
    issue_type: str
    evaluation_status: str


class WordPronunciationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    word_text: str
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    audio_segment_reference: Optional[str] = None
    expected_phonemes: str
    observed_phonetic_evidence: Optional[str] = None
    pronunciation_score: Optional[float] = None
    confidence: Optional[float] = None
    evaluation_status: str
    exclusion_reason: Optional[str] = None
    phonemes: List[PhonemeResultResponse] = Field(default_factory=list, validation_alias="phoneme_results")


class ProsodyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    word_stress_score: Optional[float] = None
    sentence_stress_score: Optional[float] = None
    syllable_analysis: Optional[Dict[str, Any]] = None
    pitch_features: Optional[Dict[str, Any]] = None
    intonation_score: Optional[float] = None
    speaking_pace_score: Optional[float] = None
    pause_metrics: Optional[Dict[str, Any]] = None
    intelligibility_score: Optional[float] = None
    confidence: Optional[float] = None


class PronunciationRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    category: str
    title: str
    description: str
    evidence_reference: Optional[str] = None
    expected_pronunciation: Optional[str] = None
    suggested_exercise: str
    priority: str
    difficulty_level: str
    confidence: Optional[float] = None


class IELTSPracticeAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    participant_id: Optional[str] = None
    fluency_coherence_estimate: Optional[float] = None
    lexical_resource_estimate: Optional[float] = None
    grammatical_accuracy_estimate: Optional[float] = None
    pronunciation_estimate: Optional[float] = None
    overall_practice_estimate: Optional[float] = None
    qualitative_band_descriptor: str
    rubric_version: str
    confidence: Optional[float] = None
    evidence_coverage: float = 1.0
    assessment_status: str
    disclaimer_version: str = "1.0"
    disclaimer_text: str


class PronunciationAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meeting_id: str
    participant_id: Optional[str] = None
    speaker_id: Optional[str] = None
    speaker_label: str
    assessment_status: str
    audio_quality_status: str
    overall_pronunciation_score: Optional[float] = None
    evidence_confidence: Optional[float] = None
    evidence_coverage: float = 1.0
    evaluated_word_count: int = 0
    excluded_word_count: int = 0
    scoring_version: str = "1.0"
    processing_started_at: datetime
    processing_completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message_safe: Optional[str] = None

    prosody_result: Optional[ProsodyResponse] = None
    ielts_assessment: Optional[IELTSPracticeAssessmentResponse] = None
    recommendations: List[PronunciationRecommendationResponse] = Field(default_factory=list)

