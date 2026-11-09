"""
FluentMeet AI - Step 10 Data Models: Report Generation, Analytics & Dashboard Engine
Specification: Step 10 - Technical Implementation Specification
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


class ReportSnapshot(Base):
    """
    Immutable structured report snapshot for a meeting or an individual participant.
    Report types:
      - 'meeting_summary': Aggregated performance, highlights, participation breakdown
      - 'individual_participant': Single-speaker comprehensive English & pronunciation report
    """
    __tablename__ = "report_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(32), nullable=False)  # 'meeting_summary', 'individual_participant'
    participant_id = Column(String(36), ForeignKey("meeting_participants.id", ondelete="SET NULL"), nullable=True, index=True)
    speaker_label = Column(String(64), nullable=True)
    report_version = Column(Integer, default=1, nullable=False)
    report_status = Column(String(32), default="completed", nullable=False)  # generating, completed, partial, insufficient_evidence, failed
    
    # Versioning & Auditability
    source_analysis_version = Column(String(32), default="1.0", nullable=False)
    source_analysis_references = Column(JSON, nullable=True)  # session_id, assessment_ids, transcript_id, duration_ms
    scoring_rubric_version = Column(String(32), default="1.0", nullable=False)
    
    # Core Aggregated Metrics (extracted for fast querying & indexing)
    overall_score = Column(Float, nullable=True)  # null if insufficient evidence or missing category
    confidence_score = Column(Float, nullable=True)
    word_count = Column(Integer, default=0, nullable=False)
    speaking_duration_seconds = Column(Float, default=0.0, nullable=False)
    
    # Full Immutable Structured Payload
    report_payload = Column(JSON, nullable=False)
    
    generated_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_report_snapshots_lookup", "meeting_id", "report_type", "participant_id", "report_version"),
        Index("ix_report_snapshots_tenant_meeting", "tenant_id", "meeting_id"),
        Index("ix_report_snapshots_participant_time", "participant_id", "generated_at"),
    )

    # Relationships
    exports = relationship("ReportExport", back_populates="snapshot", cascade="all, delete-orphan")
    access_logs = relationship("ReportAccessLog", back_populates="snapshot", cascade="all, delete-orphan")


class ReportExport(Base):
    """
    Tracks exported artifacts (PDF, CSV, HTML) generated from a ReportSnapshot.
    """
    __tablename__ = "report_exports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    report_snapshot_id = Column(String(36), ForeignKey("report_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    export_format = Column(String(16), nullable=False)  # 'pdf', 'csv', 'html'
    storage_reference = Column(String(512), nullable=True)  # Local file path or S3 key
    export_status = Column(String(32), default="completed", nullable=False)  # pending, completed, failed
    file_size_bytes = Column(Integer, nullable=True)
    content_hash = Column(String(64), nullable=True)  # SHA-256 hash for integrity
    expires_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_report_exports_snapshot_fmt", "report_snapshot_id", "export_format"),
    )

    # Relationships
    snapshot = relationship("ReportSnapshot", back_populates="exports")


class ReportAccessLog(Base):
    """
    Audit log for compliance and access tracking of reports and exports.
    """
    __tablename__ = "report_access_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    report_snapshot_id = Column(String(36), ForeignKey("report_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(String(36), nullable=True, index=True)
    action = Column(String(32), nullable=False)  # 'view', 'export_pdf', 'export_csv', 'export_html', 'share'
    request_metadata = Column(JSON, nullable=True)  # ip_address, user_agent, headers
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_report_access_logs_snapshot", "report_snapshot_id", "created_at"),
    )

    # Relationships
    snapshot = relationship("ReportSnapshot", back_populates="access_logs")

