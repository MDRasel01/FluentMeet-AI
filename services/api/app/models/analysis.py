"""
FluentMeet AI - Step 08 Data Models: AI English Analysis Engine
Specification: Step 08 - Section 22 (Database Architecture)
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


class AnalysisSession(Base):
    """
    Tracks an end-to-end English communication analysis job for a meeting.
    Status transitions: queued -> processing -> completed / partially_completed / failed / insufficient_data
    """
    __tablename__ = "analysis_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    transcript_id = Column(String(36), nullable=True)
    transcript_version = Column(Integer, default=1, nullable=False)
    analysis_version = Column(String(32), default="1.0", nullable=False)
    status = Column(String(32), default="queued", nullable=False)
    requested_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message_safe = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_analysis_sessions_meeting_status", "meeting_id", "status"),
        Index("ix_analysis_sessions_tenant_meeting", "tenant_id", "meeting_id"),
    )

    # Relationships
    participants = relationship("ParticipantAnalysis", back_populates="session", cascade="all, delete-orphan")
    events = relationship("AnalysisEvent", back_populates="session", cascade="all, delete-orphan")


class ParticipantAnalysis(Base):
    """
    Individual participant's complete English assessment across all linguistic categories.
    """
    __tablename__ = "participant_analysis"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_session_id = Column(String(36), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("meeting_participants.id", ondelete="SET NULL"), nullable=True, index=True)
    speaker_id = Column(String(36), ForeignKey("meeting_speakers.id", ondelete="SET NULL"), nullable=True, index=True)
    speaker_label = Column(String(64), nullable=False)  # e.g., "speaker_user_me", "speaker_001"
    overall_score = Column(Float, nullable=True)  # 0.0 - 100.0 or null
    score_status = Column(String(32), default="available", nullable=False)  # available, insufficient_data, unavailable
    evidence_coverage = Column(Float, default=1.0, nullable=False)  # [0.0, 1.0]
    analysis_confidence = Column(Float, nullable=True)
    scoring_version = Column(String(32), default="1.0", nullable=False)
    status = Column(String(32), default="completed", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("analysis_session_id", "speaker_label", name="uq_participant_analysis_session_speaker"),
    )

    # Relationships
    session = relationship("AnalysisSession", back_populates="participants")
    category_scores = relationship("AnalysisCategoryScore", back_populates="participant", cascade="all, delete-orphan")
    grammar_issues = relationship("GrammarIssue", back_populates="participant", cascade="all, delete-orphan")
    vocabulary_insights = relationship("VocabularyInsight", back_populates="participant", cascade="all, delete-orphan")
    fluency_metrics = relationship("FluencyMetric", back_populates="participant", cascade="all, delete-orphan")
    communication_insights = relationship("CommunicationInsight", back_populates="participant", cascade="all, delete-orphan")
    recommendations = relationship("ImprovementRecommendation", back_populates="participant", cascade="all, delete-orphan")


class AnalysisCategoryScore(Base):
    """
    Category-level score (Grammar, Vocabulary, Fluency, Sentence Structure, Communication, Contextual Language).
    """
    __tablename__ = "analysis_category_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_analysis_id = Column(String(36), ForeignKey("participant_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(64), nullable=False)  # grammar, vocabulary, fluency, sentence_structure, communication, contextual_language
    score = Column(Float, nullable=True)  # 0.0 - 100.0
    status = Column(String(32), default="available", nullable=False)  # available, insufficient_data, unavailable
    evidence_count = Column(Integer, default=0, nullable=False)
    confidence = Column(Float, nullable=True)
    scoring_version = Column(String(32), default="1.0", nullable=False)

    __table_args__ = (
        UniqueConstraint("participant_analysis_id", "category", name="uq_category_score_participant_cat"),
    )

    participant = relationship("ParticipantAnalysis", back_populates="category_scores")


class GrammarIssue(Base):
    """
    Specific grammatical finding with evidence mapping to a transcript segment.
    """
    __tablename__ = "grammar_issues"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_analysis_id = Column(String(36), ForeignKey("participant_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    transcript_segment_id = Column(String(36), ForeignKey("transcript_segments.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String(64), nullable=False)  # tense, subject_verb_agreement, articles, prepositions, pronouns, sentence_construction, conditionals, modals, other
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    rule_name = Column(String(128), nullable=True)
    suggested_alternative = Column(Text, nullable=True)
    severity = Column(String(16), default="moderate", nullable=False)  # minor, moderate, major
    confidence = Column(Float, nullable=True)
    evidence_status = Column(String(32), default="verified", nullable=False)  # verified, ambiguous, unverified
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    participant = relationship("ParticipantAnalysis", back_populates="grammar_issues")


class VocabularyInsight(Base):
    """
    Vocabulary precision and enrichment recommendations.
    """
    __tablename__ = "vocabulary_insights"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_analysis_id = Column(String(36), ForeignKey("participant_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    transcript_segment_id = Column(String(36), ForeignKey("transcript_segments.id", ondelete="SET NULL"), nullable=True, index=True)
    original_expression = Column(Text, nullable=False)
    suggested_expression = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    insight_type = Column(String(64), nullable=False)  # word_choice, overused, repetition, business_expression, collocation, precision
    context_note = Column(Text, nullable=True)
    example_sentence = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    participant = relationship("ParticipantAnalysis", back_populates="vocabulary_insights")


class FluencyMetric(Base):
    """
    Calculated fluency analytics: filler word rate, repetition rate, speaking pace, pauses.
    """
    __tablename__ = "fluency_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_analysis_id = Column(String(36), ForeignKey("participant_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(64), nullable=False)  # filler_word_rate, repetition_rate, speech_rate_wpm, avg_utterance_length_words, pause_frequency
    metric_value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)  # per_minute, wpm, words, count, seconds
    evidence_count = Column(Integer, default=0, nullable=False)
    confidence = Column(Float, nullable=True)
    calculation_version = Column(String(32), default="1.0", nullable=False)

    __table_args__ = (
        UniqueConstraint("participant_analysis_id", "metric_name", name="uq_fluency_metric_participant_name"),
    )

    participant = relationship("ParticipantAnalysis", back_populates="fluency_metrics")


class CommunicationInsight(Base):
    """
    Qualitative communicative effectiveness, response relevance, active listening indicators.
    """
    __tablename__ = "communication_insights"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_analysis_id = Column(String(36), ForeignKey("participant_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    insight_type = Column(String(64), nullable=False)  # response_relevance, active_listening, conversation_management, professional_tone, clarity
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    participant = relationship("ParticipantAnalysis", back_populates="communication_insights")


class ImprovementRecommendation(Base):
    """
    Actionable personalized recommendations ordered by priority.
    """
    __tablename__ = "improvement_recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_analysis_id = Column(String(36), ForeignKey("participant_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_category = Column(String(64), nullable=False)  # grammar, vocabulary, fluency, communication, contextual
    priority = Column(String(16), nullable=False)  # high, medium, low
    title = Column(String(128), nullable=False)
    actionable_suggestion = Column(Text, nullable=False)
    evidence_reference = Column(Text, nullable=True)
    example = Column(Text, nullable=True)
    expected_outcome = Column(Text, nullable=True)
    status = Column(String(32), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_recommendations_participant_priority", "participant_analysis_id", "priority"),
    )

    participant = relationship("ParticipantAnalysis", back_populates="recommendations")


class AnalysisEvent(Base):
    """
    Audit log of analysis orchestrator state changes.
    """
    __tablename__ = "analysis_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_session_id = Column(String(36), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # analysis.queued, analysis.started, analysis.completed, analysis.failed
    status = Column(String(32), nullable=False)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_analysis_events_session_created", "analysis_session_id", "created_at"),
    )

    session = relationship("AnalysisSession", back_populates="events")
