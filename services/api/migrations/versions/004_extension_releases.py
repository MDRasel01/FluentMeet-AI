"""Add extension releases and download telemetry schema

Revision ID: 004_extension_releases
Revises: 003_transcript_diarization
Create Date: 2026-11-07 16:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_extension_releases'
down_revision: Union[str, None] = '003_transcript_diarization'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. extension_releases
    op.create_table(
        'extension_releases',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('extension_name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=32), nullable=False),
        sa.Column('channel', sa.String(length=32), server_default='stable', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='draft', nullable=False),
        sa.Column('manifest_version', sa.Integer(), server_default='3', nullable=False),
        sa.Column('build_number', sa.String(length=64), nullable=True),
        sa.Column('git_commit_sha', sa.String(length=64), nullable=True),
        sa.Column('release_notes', sa.JSON(), nullable=True),
        sa.Column('minimum_chrome_version', sa.String(length=32), server_default='116.0', nullable=False),
        sa.Column('artifact_storage_key', sa.String(length=512), unique=True, nullable=True),
        sa.Column('artifact_filename', sa.String(length=255), nullable=True),
        sa.Column('artifact_size_bytes', sa.Integer(), server_default='0', nullable=False),
        sa.Column('sha256_checksum', sa.String(length=64), nullable=True),
        sa.Column('download_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('channel', 'version', name='uq_extension_release_channel_version'),
    )
    op.create_index('ix_extension_releases_version', 'extension_releases', ['version'])
    op.create_index('ix_extension_releases_channel', 'extension_releases', ['channel'])
    op.create_index('ix_extension_releases_status', 'extension_releases', ['status'])
    op.create_index('ix_extension_releases_published_at', 'extension_releases', ['published_at'])
    op.create_index('ix_extension_releases_channel_status', 'extension_releases', ['channel', 'status'])

    # 2. extension_download_logs
    op.create_table(
        'extension_download_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('release_id', sa.String(length=36), sa.ForeignKey('extension_releases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('organization_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('downloaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('download_status', sa.String(length=32), server_default='success', nullable=False),
        sa.Column('client_platform', sa.String(length=64), server_default='Unknown', nullable=False),
        sa.Column('request_id', sa.String(length=64), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
    )
    op.create_index('ix_extension_download_logs_release_id', 'extension_download_logs', ['release_id'])
    op.create_index('ix_extension_download_logs_user_id', 'extension_download_logs', ['user_id'])
    op.create_index('ix_extension_download_logs_downloaded_at', 'extension_download_logs', ['downloaded_at'])

    # 3. extension_release_events
    op.create_table(
        'extension_release_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('release_id', sa.String(length=36), sa.ForeignKey('extension_releases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('actor_user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_extension_release_events_release_id', 'extension_release_events', ['release_id'])
    op.create_index('ix_extension_release_events_event_type', 'extension_release_events', ['event_type'])


def downgrade() -> None:
    op.drop_table('extension_release_events')
    op.drop_table('extension_download_logs')
    op.drop_table('extension_releases')
