import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Boolean,
    Integer,
    ForeignKey,
    Text,
    JSON,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import generate_uuid, get_utc_now

class ExtensionRelease(Base):
    """
    Represents an extension version release artifact and its lifecycle state.
    """
    __tablename__ = "extension_releases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    extension_name = Column(String(255), nullable=False, default="FluentMeet AI — Real-time English Meeting Coach")
    version = Column(String(32), nullable=False, index=True)  # SemVer e.g. "1.0.0"
    channel = Column(String(32), nullable=False, default="stable", index=True)  # stable, beta, internal
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft, building, testing, ready_for_review, approved, published, failed, withdrawn, archived
    manifest_version = Column(Integer, nullable=False, default=3)
    build_number = Column(String(64), nullable=True)
    git_commit_sha = Column(String(64), nullable=True)
    release_notes = Column(JSON, nullable=True)  # list of strings or structured object
    minimum_chrome_version = Column(String(32), nullable=False, default="116.0")
    artifact_storage_key = Column(String(512), unique=True, nullable=True)
    artifact_filename = Column(String(255), nullable=True)
    artifact_size_bytes = Column(Integer, nullable=False, default=0)
    sha256_checksum = Column(String(64), nullable=True)
    download_count = Column(Integer, nullable=False, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    published_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    download_logs = relationship("ExtensionDownloadLog", back_populates="release", cascade="all, delete-orphan")
    events = relationship("ExtensionReleaseEvent", back_populates="release", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("channel", "version", name="uq_extension_release_channel_version"),
        Index("ix_extension_releases_channel_status", "channel", "status"),
    )


class ExtensionDownloadLog(Base):
    """
    Audit log of Chrome Extension downloads for telemetry, analytics, and security.
    """
    __tablename__ = "extension_download_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    release_id = Column(String(36), ForeignKey("extension_releases.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    downloaded_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    download_status = Column(String(32), nullable=False, default="success")  # success, failed, blocked
    client_platform = Column(String(64), nullable=False, default="Unknown")  # Windows, macOS, Linux, ChromeOS, Unknown
    request_id = Column(String(64), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    release = relationship("ExtensionRelease", back_populates="download_logs")


class ExtensionReleaseEvent(Base):
    """
    Audit trail for release management operations (create, build, validate, approve, publish, withdraw, rollback).
    """
    __tablename__ = "extension_release_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    release_id = Column(String(36), ForeignKey("extension_releases.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # created, built, validated, approved, published, withdrawn, rolled_back, archived
    actor_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    release = relationship("ExtensionRelease", back_populates="events")
