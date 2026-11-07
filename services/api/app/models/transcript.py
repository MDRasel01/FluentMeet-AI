"""
FluentMeet AI - Step 07 Data Models: Speech-to-Text & Speaker Diarization
Specification: Step 07 - Core Architecture & Database Schema
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


class MeetingSpeaker(Base):
    """
    Tracks distinct speakers identified in a meeting session.
    Source 0 = user mic (local user).
    Source 1 = remote participants (diarized into distinct speaker labels).
    """
    __tablename__ = "meeting_speakers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_label = Column(String(64), nullable=False)  # e.g. "speaker_user_me", "speaker_001", "speaker_002"
    display_name = Column(String(128), nullable=True)  # Human-readable or user-customized label
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    participant_id = Column(String(36), ForeignKey("meeting_participants.id", ondelete="SET NULL"), nullable=True, index=True)
    is_identified = Column(Boolean, default=False, nullable=False)
    confidence_score = Column(Float, nullable=True)  # Calibrated model confidence or null
    source_id = Column(Integer, nullable=True)  # 0 = local mic, 1 = remote tab audio
    voice_embedding = Column(JSON, nullable=True)  # Optional embedding vector for speaker re-identification
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("meeting_id", "speaker_label", name="uq_meeting_speaker_label"),
        Index("ix_meeting_speakers_meeting_source", "meeting_id", "source_id"),
    )

    # Relationships
    segments = relationship("TranscriptSegment", back_populates="speaker", cascade="all, delete-orphan")
    turns = relationship("SpeakerTurn", back_populates="speaker", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    """
    Speech-to-text segment with temporal boundaries, confidence, and progressive lifecycle.
    Statuses: partial -> provisional -> final -> corrected
    """
    __tablename__ = "transcript_segments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_id = Column(String(36), ForeignKey("meeting_speakers.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id = Column(Integer, default=0, nullable=False)
    start_time_ms = Column(Integer, nullable=False, index=True)
    end_time_ms = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(16), default="en", nullable=False)
    confidence_score = Column(Float, nullable=True)  # Raw Whisper/model probability or null
    status = Column(String(32), default="partial", nullable=False)  # partial, provisional, final, corrected
    revision_number = Column(Integer, default=1, nullable=False)
    audio_segment_id = Column(String(36), ForeignKey("audio_segments.id", ondelete="SET NULL"), nullable=True, index=True)
    words_json = Column(JSON, nullable=True)  # JSON-serialized word objects with timestamps
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_transcript_segment_meeting_time", "meeting_id", "start_time_ms", "end_time_ms"),
        Index("ix_transcript_segment_status", "meeting_id", "status"),
    )

    # Relationships
    speaker = relationship("MeetingSpeaker", back_populates="segments")
    words = relationship("TranscriptWord", back_populates="segment", cascade="all, delete-orphan")


class TranscriptWord(Base):
    """
    Granular word-level transcription with precise millisecond boundaries.
    """
    __tablename__ = "transcript_words"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transcript_segment_id = Column(String(36), ForeignKey("transcript_segments.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_id = Column(String(36), ForeignKey("meeting_speakers.id", ondelete="SET NULL"), nullable=True, index=True)
    word = Column(String(128), nullable=False)
    start_time_ms = Column(Integer, nullable=False)
    end_time_ms = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=True)
    word_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_transcript_words_meeting_time", "meeting_id", "start_time_ms"),
    )

    # Relationships
    segment = relationship("TranscriptSegment", back_populates="words")


class SpeakerTurn(Base):
    """
    Contiguous speech intervals attributed to a specific speaker.
    """
    __tablename__ = "speaker_turns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_id = Column(String(36), ForeignKey("meeting_speakers.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, default=0, nullable=False)
    start_time_ms = Column(Integer, nullable=False, index=True)
    end_time_ms = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=False)
    turn_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_speaker_turns_meeting_interval", "meeting_id", "start_time_ms", "end_time_ms"),
    )

    # Relationships
    speaker = relationship("MeetingSpeaker", back_populates="turns")


class SpeechOverlap(Base):
    """
    Detected cross-talk intervals where multiple speakers speak simultaneously.
    """
    __tablename__ = "speech_overlaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time_ms = Column(Integer, nullable=False, index=True)
    end_time_ms = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=False)
    overlapping_speaker_ids = Column(JSON, nullable=False)  # List of speaker IDs involved
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_speech_overlaps_meeting_interval", "meeting_id", "start_time_ms", "end_time_ms"),
    )


class TranscriptEvent(Base):
    """
    Audit log and event stream representation for real-time distribution and debugging.
    """
    __tablename__ = "transcript_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # transcript.partial, transcript.final, speaker.detected, speaker.overlap, transcript.corrected
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_transcript_events_meeting_type", "meeting_id", "event_type"),
    )

