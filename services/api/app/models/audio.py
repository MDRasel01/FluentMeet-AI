import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Boolean,
    Integer,
    Float,
    BigInteger,
    ForeignKey,
    Text,
    JSON,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import generate_uuid, get_utc_now

class AudioStream(Base):
    __tablename__ = "audio_streams"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, nullable=False)  # 0 = REMOTE_TAB, 1 = LOCAL_MIC
    stream_id = Column(String(64), nullable=False, index=True)
    protocol_version = Column(Integer, default=1, nullable=False)
    sample_rate = Column(Integer, default=16000, nullable=False)
    channels = Column(Integer, default=1, nullable=False)
    encoding = Column(String(32), default="pcm_s16le", nullable=False)
    stream_status = Column(String(32), default="active", nullable=False)  # active, paused, closed, failed
    started_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_sequence = Column(BigInteger, default=0, nullable=False)
    last_timestamp = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("meeting_id", "source_id", "stream_id", name="uq_meeting_source_stream"),
        Index("ix_audio_stream_meeting_source", "meeting_id", "source_id"),
    )

    # Relationships
    segments = relationship("AudioSegment", back_populates="stream", cascade="all, delete-orphan")
    gaps = relationship("AudioStreamGap", back_populates="stream", cascade="all, delete-orphan")

    @property
    def status(self) -> str:
        return self.stream_status

    @status.setter
    def status(self, val: str):
        self.stream_status = val

    @property
    def codec(self) -> str:
        return self.encoding

    @codec.setter
    def codec(self, val: str):
        self.encoding = val

    @property
    def total_packets(self) -> int:
        return self.last_sequence

    @property
    def total_samples(self) -> int:
        return int(self.last_timestamp * self.sample_rate / 1000.0) if self.sample_rate else 0

    @property
    def total_duration_ms(self) -> int:
        return int(self.last_timestamp)

class AudioSegment(Base):
    __tablename__ = "audio_segments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    stream_id = Column(String(64), nullable=False, index=True)
    audio_stream_id = Column(String(36), ForeignKey("audio_streams.id", ondelete="CASCADE"), nullable=True)
    source_id = Column(Integer, nullable=False)  # 0 = Tab, 1 = Mic
    start_timestamp = Column(Float, nullable=False)
    end_timestamp = Column(Float, nullable=False)
    first_sequence = Column(BigInteger, nullable=False)
    last_sequence = Column(BigInteger, nullable=False)
    sample_rate = Column(Integer, default=16000, nullable=False)
    channels = Column(Integer, default=1, nullable=False)
    encoding = Column(String(32), default="pcm_s16le", nullable=False)
    sample_count = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)  # SHA-256
    storage_key = Column(String(1024), nullable=False)
    storage_status = Column(String(32), default="persisted", nullable=False)  # pending, persisted, deleted
    processing_status = Column(String(32), default="ready", nullable=False, index=True)  # ready, processing, completed, failed
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    stream = relationship("AudioStream", back_populates="segments")
    quality_metric = relationship("AudioQualityMetric", back_populates="segment", uselist=False, cascade="all, delete-orphan")
    jobs = relationship("AudioProcessingJob", back_populates="segment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_audio_segment_stream_seq", "stream_id", "first_sequence"),
    )

class AudioStreamGap(Base):
    __tablename__ = "audio_stream_gaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    stream_id = Column(String(64), nullable=False, index=True)
    audio_stream_id = Column(String(36), ForeignKey("audio_streams.id", ondelete="CASCADE"), nullable=True)
    source_id = Column(Integer, nullable=False)
    missing_sequence_start = Column(BigInteger, nullable=False)
    missing_sequence_end = Column(BigInteger, nullable=False)
    gap_detected_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    gap_resolved = Column(Boolean, default=False, nullable=False)
    resolution_type = Column(String(50), default="unrecoverable_drop", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    stream = relationship("AudioStream", back_populates="gaps")

class AudioProcessingJob(Base):
    __tablename__ = "audio_processing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    segment_id = Column(String(36), ForeignKey("audio_segments.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(50), default="asr_diarization", nullable=False)
    status = Column(String(32), default="queued", nullable=False, index=True)  # queued, processing, completed, failed, dead_letter
    retry_count = Column(Integer, default=0, nullable=False)
    error_code = Column(String(50), nullable=True)
    error_message_safe = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    segment = relationship("AudioSegment", back_populates="jobs")

class AudioQualityMetric(Base):
    __tablename__ = "audio_quality_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    segment_id = Column(String(36), ForeignKey("audio_segments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    rms_level = Column(Float, nullable=False)
    peak_amplitude = Column(Float, nullable=False)
    clipping_ratio = Column(Float, default=0.0, nullable=False)
    silence_ratio = Column(Float, default=0.0, nullable=False)
    invalid_sample_count = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    segment = relationship("AudioSegment", back_populates="quality_metric")

class AudioUsageRecord(Base):
    __tablename__ = "audio_usage_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id = Column(Integer, nullable=False)
    audio_duration_ms = Column(BigInteger, default=0, nullable=False)
    storage_bytes = Column(BigInteger, default=0, nullable=False)
    processed_bytes = Column(BigInteger, default=0, nullable=False)
    billing_period = Column(String(20), nullable=False)  # YYYY-MM
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

class AudioOutboxEvent(Base):
    __tablename__ = "audio_outbox_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(64), nullable=False, index=True)
    aggregate_id = Column(String(64), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

class AudioIngestionEvent(Base):
    __tablename__ = "audio_ingestion_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    stream_id = Column(String(64), nullable=False)
    source_id = Column(Integer, nullable=False)
    event_type = Column(String(64), nullable=False)
    sequence_number = Column(BigInteger, nullable=True)
    error_code = Column(String(50), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
