"""Add Report Generation, Analytics and Dashboard Engine schema

Revision ID: 006_report_engine_schema
Revises: 005_pronunciation_schema
Create Date: 2026-11-09 08:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006_report_engine_schema'
down_revision: Union[str, None] = '005_pronunciation_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. report_snapshots
    op.create_table(
        'report_snapshots',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('report_type', sa.String(length=32), nullable=False),
        sa.Column('participant_id', sa.String(length=36), sa.ForeignKey('meeting_participants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('speaker_label', sa.String(length=64), nullable=True),
        sa.Column('report_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('report_status', sa.String(length=32), server_default='completed', nullable=False),
        sa.Column('source_analysis_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.Column('source_analysis_references', sa.JSON(), nullable=True),
        sa.Column('scoring_rubric_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('word_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('speaking_duration_seconds', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('report_payload', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_report_snapshots_lookup', 'report_snapshots', ['meeting_id', 'report_type', 'participant_id', 'report_version'])
    op.create_index('ix_report_snapshots_tenant_meeting', 'report_snapshots', ['tenant_id', 'meeting_id'])
    op.create_index('ix_report_snapshots_participant_time', 'report_snapshots', ['participant_id', 'generated_at'])
    op.create_index('ix_report_snapshots_tenant_id', 'report_snapshots', ['tenant_id'])
    op.create_index('ix_report_snapshots_meeting_id', 'report_snapshots', ['meeting_id'])
    op.create_index('ix_report_snapshots_participant_id', 'report_snapshots', ['participant_id'])

    # 2. report_exports
    op.create_table(
        'report_exports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('report_snapshot_id', sa.String(length=36), sa.ForeignKey('report_snapshots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('export_format', sa.String(length=16), nullable=False),
        sa.Column('storage_reference', sa.String(length=512), nullable=True),
        sa.Column('export_status', sa.String(length=32), server_default='completed', nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_report_exports_snapshot_fmt', 'report_exports', ['report_snapshot_id', 'export_format'])
    op.create_index('ix_report_exports_tenant_id', 'report_exports', ['tenant_id'])
    op.create_index('ix_report_exports_user_id', 'report_exports', ['user_id'])
    op.create_index('ix_report_exports_snapshot_id', 'report_exports', ['report_snapshot_id'])

    # 3. report_access_logs
    op.create_table(
        'report_access_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('report_snapshot_id', sa.String(length=36), sa.ForeignKey('report_snapshots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('actor_id', sa.String(length=36), nullable=True),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('request_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_report_access_logs_snapshot', 'report_access_logs', ['report_snapshot_id', 'created_at'])
    op.create_index('ix_report_access_logs_tenant_id', 'report_access_logs', ['tenant_id'])
    op.create_index('ix_report_access_logs_actor_id', 'report_access_logs', ['actor_id'])


def downgrade() -> None:
    op.drop_table('report_access_logs')
    op.drop_table('report_exports')
    op.drop_table('report_snapshots')

