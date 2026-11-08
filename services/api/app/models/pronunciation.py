"""
FluentMeet AI - Step 09 Data Models: Pronunciation Analysis & IELTS-Style Assessment Engine
Specification: Step 09 - Section 19 (Database Design)
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Boolean,
    Integer,
    Float,
    ForeignKey,
    Text,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import generate_uuid, get_utc_now


class PronunciationAssessment(Base):
    """
    Top-level assessment record for a participant's spoken audio evidence.
    Tracks status: pending -> validating -> analyzing -> completed / partial / insufficient_evidence / failed
    """
    __tablename__ = "pronunciation_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("meeting_participants.id", ondelete="SET NULL"), nullable=True, index=True)
    speaker_id = Column(String(36), ForeignKey("meeting_speakers.id", ondelete="SET NULL"), nullable=True, index=True)
    speaker_label = Column(String(64), nullable=False)
    transcript_id = Column(String(36), nullable=True)
    assessment_status = Column(String(32), default="pending", nullable=False)
    audio_quality_status = Column(String(32), default="suitable", nullable=False)  # suitable, low_quality, insufficient_speech, high_noise, overlapping_speech, speaker_uncertain, processing_failed
    overall_pronunciation_score = Column(Float, nullable=True)  # 0.0 - 100.0 or null if insufficient evidence
    evidence_confidence = Column(Float, nullable=True)  # [0.0, 1.0]
    evidence_coverage = Column(Float, default=1.0, nullable=False)  # [0.0, 1.0]
    evaluated_word_count = Column(Integer, default=0, nullable=False)
    excluded_word_count = Column(Integer, default=0, nullable=False)
    scoring_version = Column(String(32), default="1.0", nullable=False)
    processing_started_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message_safe = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_pronunciation_assessments_meeting_status", "meeting_id", "assessment_status"),
        Index("ix_pronunciation_assessments_speaker", "meeting_id", "speaker_label"),
    )

    # Relationships
    word_results = relationship("PronunciationWordResult", back_populates="assessment", cascade="all, delete-orphan")
    prosody_result = relationship("PronunciationProsodyResult", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("PronunciationRecommendation", back_populates="assessment", cascade="all, delete-orphan")
    ielts_assessment = relationship("IELTSSpeakingPracticeAssessment", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    model_runs = relationship("AssessmentModelRun", back_populates="assessment", cascade="all, delete-orphan")


class PronunciationWordResult(Base):
    """
    Word-level acoustic pronunciation scoring linked to timestamps and audio segment references.
    """
    __tablename__ = "pronunciation_word_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("pronunciation_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    word_text = Column(String(128), nullable=False)
    start_time_ms = Column(Integer, nullable=False, index=True)
    end_time_ms = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=False)
    audio_segment_reference = Column(String(1024), nullable=True)
    expected_phonemes = Column(String(256), nullable=False)  # ARPAbet or IPA representation
    observed_phonetic_evidence = Column(String(256), nullable=True)
    pronunciation_score = Column(Float, nullable=True)  # 0.0 - 100.0
    confidence = Column(Float, nullable=True)  # [0.0, 1.0]
    evaluation_status = Column(String(32), default="evaluated", nullable=False)  # evaluated, excluded, uncertain
    exclusion_reason = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_word_results_assessment_time", "assessment_id", "start_time_ms", "end_time_ms"),
    )

    # Relationships
    assessment = relationship("PronunciationAssessment", back_populates="word_results")
    phoneme_results = relationship("PronunciationPhonemeResult", back_populates="word_result", cascade="all, delete-orphan")


class PronunciationPhonemeResult(Base):
    """
    Phoneme-level evaluation evidence when supported by phonetic/acoustic model.
    """
    __tablename__ = "pronunciation_phoneme_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    word_result_id = Column(String(36), ForeignKey("pronunciation_word_results.id", ondelete="CASCADE"), nullable=False, index=True)
    phoneme_reference = Column(String(32), nullable=False)  # e.g. "TH", "IH", "NG", "K"
    phoneme_evidence = Column(String(32), nullable=True)
    phoneme_score = Column(Float, nullable=True)  # 0.0 - 100.0
    confidence = Column(Float, nullable=True)
    issue_type = Column(String(64), default="correct", nullable=False)  # correct, substitution, omission, distortion, insertion
    evaluation_status = Column(String(32), default="evaluated", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    word_result = relationship("PronunciationWordResult", back_populates="phoneme_results")


class PronunciationProsodyResult(Base):
    """
    Prosody analysis: stress (syllable, word, sentence), intonation (F0 pitch contour),
    speaking pace (WPM), pause metrics, and intelligibility.
    """
    __tablename__ = "pronunciation_prosody_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("pronunciation_assessments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    word_stress_score = Column(Float, nullable=True)  # 0.0 - 100.0
    sentence_stress_score = Column(Float, nullable=True)  # 0.0 - 100.0
    syllable_analysis = Column(JSON, nullable=True)
    pitch_features = Column(JSON, nullable=True)  # mean_f0, min_f0, max_f0, pitch_range_hz, contour_type
    intonation_score = Column(Float, nullable=True)  # 0.0 - 100.0
    speaking_pace_score = Column(Float, nullable=True)  # 0.0 - 100.0
    pause_metrics = Column(JSON, nullable=True)  # total_pauses, avg_pause_ms, long_pauses_count
    intelligibility_score = Column(Float, nullable=True)  # 0.0 - 100.0
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    assessment = relationship("PronunciationAssessment", back_populates="prosody_result")


class PronunciationRecommendation(Base):
    """
    Actionable pronunciation and prosody improvement exercises.
    """
    __tablename__ = "pronunciation_recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("pronunciation_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(64), nullable=False)  # phoneme, minimal_pair, word_stress, sentence_stress, intonation, speaking_pace, connected_speech
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    evidence_reference = Column(String(512), nullable=True)
    expected_pronunciation = Column(String(256), nullable=True)
    suggested_exercise = Column(Text, nullable=False)
    priority = Column(String(16), default="medium", nullable=False)  # high, medium, low
    difficulty_level = Column(String(16), default="intermediate", nullable=False)  # beginner, intermediate, advanced
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_pronunciation_recommendations_priority", "assessment_id", "priority"),
    )

    assessment = relationship("PronunciationAssessment", back_populates="recommendations")


class IELTSSpeakingPracticeAssessment(Base):
    """
    IELTS-Style Speaking Practice Assessment.
    Educational practice estimate synthesizing Step 08 grammar/lexical/fluency evidence
    with Step 09 acoustic pronunciation evidence.
    Includes strict educational practice disclaimer.
    """
    __tablename__ = "ielts_practice_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("pronunciation_assessments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("meeting_participants.id", ondelete="SET NULL"), nullable=True, index=True)
    fluency_coherence_estimate = Column(Float, nullable=True)  # Practice band score e.g. 6.5
    lexical_resource_estimate = Column(Float, nullable=True)
    grammatical_accuracy_estimate = Column(Float, nullable=True)
    pronunciation_estimate = Column(Float, nullable=True)
    overall_practice_estimate = Column(Float, nullable=True)  # Null until calibrated or calibrated estimate
    qualitative_band_descriptor = Column(String(128), nullable=False)  # e.g., "Competent User (Band 6.0 Practice Estimate)"
    rubric_version = Column(String(32), default="1.0-qualitative-calibrated", nullable=False)
    confidence = Column(Float, nullable=True)
    evidence_coverage = Column(Float, default=1.0, nullable=False)
    assessment_status = Column(String(32), default="completed", nullable=False)
    disclaimer_version = Column(String(32), default="1.0", nullable=False)
    disclaimer_text = Column(
        Text,
        default="Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner.",
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    assessment = relationship("PronunciationAssessment", back_populates="ielts_assessment")


class AssessmentModelRun(Base):
    """
    Auditing record for acoustic and phoneme model runs.
    """
    __tablename__ = "assessment_model_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("pronunciation_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    model_configuration = Column(JSON, nullable=True)
    processing_status = Column(String(32), default="success", nullable=False)
    processing_duration_ms = Column(Integer, default=0, nullable=False)
    error_code = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    assessment = relationship("PronunciationAssessment", back_populates="model_runs")

