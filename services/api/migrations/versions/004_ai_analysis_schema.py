"""Add AI English Analysis Engine schema

Revision ID: 004_ai_analysis_schema
Revises: 003_transcript_diarization
Create Date: 2026-11-08 23:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_ai_analysis_schema'
down_revision: Union[str, None] = '003_transcript_diarization'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. analysis_sessions
    op.create_table(
        'analysis_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transcript_id', sa.String(length=36), nullable=True),
        sa.Column('transcript_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('analysis_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='queued', nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.Column('error_message_safe', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_analysis_sessions_meeting_status', 'analysis_sessions', ['meeting_id', 'status'])
    op.create_index('ix_analysis_sessions_tenant_meeting', 'analysis_sessions', ['tenant_id', 'meeting_id'])

    # 2. participant_analysis
    op.create_table(
        'participant_analysis',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('analysis_session_id', sa.String(length=36), sa.ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('participant_id', sa.String(length=36), sa.ForeignKey('meeting_participants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('speaker_id', sa.String(length=36), sa.ForeignKey('meeting_speakers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('speaker_label', sa.String(length=64), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('score_status', sa.String(length=32), server_default='available', nullable=False),
        sa.Column('evidence_coverage', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('analysis_confidence', sa.Float(), nullable=True),
        sa.Column('scoring_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='completed', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('analysis_session_id', 'speaker_label', name='uq_participant_analysis_session_speaker'),
    )
    op.create_index('ix_participant_analysis_session_id', 'participant_analysis', ['analysis_session_id'])

    # 3. analysis_category_scores
    op.create_table(
        'analysis_category_scores',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('participant_analysis_id', sa.String(length=36), sa.ForeignKey('participant_analysis.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=32), server_default='available', nullable=False),
        sa.Column('evidence_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('scoring_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.UniqueConstraint('participant_analysis_id', 'category', name='uq_category_score_participant_cat'),
    )

    # 4. grammar_issues
    op.create_table(
        'grammar_issues',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('participant_analysis_id', sa.String(length=36), sa.ForeignKey('participant_analysis.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transcript_segment_id', sa.String(length=36), sa.ForeignKey('transcript_segments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('corrected_text', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('rule_name', sa.String(length=128), nullable=True),
        sa.Column('suggested_alternative', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=16), server_default='moderate', nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('evidence_status', sa.String(length=32), server_default='verified', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_grammar_issues_participant_id', 'grammar_issues', ['participant_analysis_id'])

    # 5. vocabulary_insights
    op.create_table(
        'vocabulary_insights',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('participant_analysis_id', sa.String(length=36), sa.ForeignKey('participant_analysis.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transcript_segment_id', sa.String(length=36), sa.ForeignKey('transcript_segments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('original_expression', sa.Text(), nullable=False),
        sa.Column('suggested_expression', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('insight_type', sa.String(length=64), nullable=False),
        sa.Column('context_note', sa.Text(), nullable=True),
        sa.Column('example_sentence', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_vocabulary_insights_participant_id', 'vocabulary_insights', ['participant_analysis_id'])

    # 6. fluency_metrics
    op.create_table(
        'fluency_metrics',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('participant_analysis_id', sa.String(length=36), sa.ForeignKey('participant_analysis.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_name', sa.String(length=64), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=32), nullable=False),
        sa.Column('evidence_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('calculation_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.UniqueConstraint('participant_analysis_id', 'metric_name', name='uq_fluency_metric_participant_name'),
    )

    # 7. communication_insights
    op.create_table(
        'communication_insights',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('participant_analysis_id', sa.String(length=36), sa.ForeignKey('participant_analysis.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insight_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
    )

    # 8. improvement_recommendations
    op.create_table(
        'improvement_recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('participant_analysis_id', sa.String(length=36), sa.ForeignKey('participant_analysis.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_category', sa.String(length=64), nullable=False),
        sa.Column('priority', sa.String(length=16), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('actionable_suggestion', sa.Text(), nullable=False),
        sa.Column('evidence_reference', sa.Text(), nullable=True),
        sa.Column('example', sa.Text(), nullable=True),
        sa.Column('expected_outcome', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_recommendations_participant_priority', 'improvement_recommendations', ['participant_analysis_id', 'priority'])

    # 9. analysis_events
    op.create_table(
        'analysis_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('analysis_session_id', sa.String(length=36), sa.ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('event_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_analysis_events_session_created', 'analysis_events', ['analysis_session_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('analysis_events')
    op.drop_table('improvement_recommendations')
    op.drop_table('communication_insights')
    op.drop_table('fluency_metrics')
    op.drop_table('vocabulary_insights')
    op.drop_table('grammar_issues')
    op.drop_table('analysis_category_scores')
    op.drop_table('participant_analysis')
    op.drop_table('analysis_sessions')

