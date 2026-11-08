"""Add Pronunciation Analysis and IELTS-Style Assessment Engine schema

Revision ID: 005_pronunciation_schema
Revises: 004_ai_analysis_schema
Create Date: 2026-11-09 00:10:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005_pronunciation_schema'
down_revision: Union[str, None] = '004_ai_analysis_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. pronunciation_assessments
    op.create_table(
        'pronunciation_assessments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('participant_id', sa.String(length=36), sa.ForeignKey('meeting_participants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('speaker_id', sa.String(length=36), sa.ForeignKey('meeting_speakers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('speaker_label', sa.String(length=64), nullable=False),
        sa.Column('transcript_id', sa.String(length=36), nullable=True),
        sa.Column('assessment_status', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('audio_quality_status', sa.String(length=32), server_default='suitable', nullable=False),
        sa.Column('overall_pronunciation_score', sa.Float(), nullable=True),
        sa.Column('evidence_confidence', sa.Float(), nullable=True),
        sa.Column('evidence_coverage', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('evaluated_word_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('excluded_word_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('scoring_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.Column('error_message_safe', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_pronunciation_assessments_meeting_status', 'pronunciation_assessments', ['meeting_id', 'assessment_status'])
    op.create_index('ix_pronunciation_assessments_speaker', 'pronunciation_assessments', ['meeting_id', 'speaker_label'])

    # 2. pronunciation_word_results
    op.create_table(
        'pronunciation_word_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('pronunciation_assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('word_text', sa.String(length=128), nullable=False),
        sa.Column('start_time_ms', sa.Integer(), nullable=False),
        sa.Column('end_time_ms', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('audio_segment_reference', sa.String(length=1024), nullable=True),
        sa.Column('expected_phonemes', sa.String(length=256), nullable=False),
        sa.Column('observed_phonetic_evidence', sa.String(length=256), nullable=True),
        sa.Column('pronunciation_score', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('evaluation_status', sa.String(length=32), server_default='evaluated', nullable=False),
        sa.Column('exclusion_reason', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_word_results_assessment_time', 'pronunciation_word_results', ['assessment_id', 'start_time_ms', 'end_time_ms'])

    # 3. pronunciation_phoneme_results
    op.create_table(
        'pronunciation_phoneme_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('word_result_id', sa.String(length=36), sa.ForeignKey('pronunciation_word_results.id', ondelete='CASCADE'), nullable=False),
        sa.Column('phoneme_reference', sa.String(length=32), nullable=False),
        sa.Column('phoneme_evidence', sa.String(length=32), nullable=True),
        sa.Column('phoneme_score', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('issue_type', sa.String(length=64), server_default='correct', nullable=False),
        sa.Column('evaluation_status', sa.String(length=32), server_default='evaluated', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_phoneme_results_word_id', 'pronunciation_phoneme_results', ['word_result_id'])

    # 4. pronunciation_prosody_results
    op.create_table(
        'pronunciation_prosody_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('pronunciation_assessments.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('word_stress_score', sa.Float(), nullable=True),
        sa.Column('sentence_stress_score', sa.Float(), nullable=True),
        sa.Column('syllable_analysis', sa.JSON(), nullable=True),
        sa.Column('pitch_features', sa.JSON(), nullable=True),
        sa.Column('intonation_score', sa.Float(), nullable=True),
        sa.Column('speaking_pace_score', sa.Float(), nullable=True),
        sa.Column('pause_metrics', sa.JSON(), nullable=True),
        sa.Column('intelligibility_score', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_prosody_results_assessment_id', 'pronunciation_prosody_results', ['assessment_id'])

    # 5. pronunciation_recommendations
    op.create_table(
        'pronunciation_recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('pronunciation_assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence_reference', sa.String(length=512), nullable=True),
        sa.Column('expected_pronunciation', sa.String(length=256), nullable=True),
        sa.Column('suggested_exercise', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=16), server_default='medium', nullable=False),
        sa.Column('difficulty_level', sa.String(length=16), server_default='intermediate', nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_pronunciation_recommendations_priority', 'pronunciation_recommendations', ['assessment_id', 'priority'])

    # 6. ielts_practice_assessments
    op.create_table(
        'ielts_practice_assessments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('pronunciation_assessments.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('participant_id', sa.String(length=36), sa.ForeignKey('meeting_participants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('fluency_coherence_estimate', sa.Float(), nullable=True),
        sa.Column('lexical_resource_estimate', sa.Float(), nullable=True),
        sa.Column('grammatical_accuracy_estimate', sa.Float(), nullable=True),
        sa.Column('pronunciation_estimate', sa.Float(), nullable=True),
        sa.Column('overall_practice_estimate', sa.Float(), nullable=True),
        sa.Column('qualitative_band_descriptor', sa.String(length=128), nullable=False),
        sa.Column('rubric_version', sa.String(length=32), server_default='1.0-qualitative-calibrated', nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('evidence_coverage', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('assessment_status', sa.String(length=32), server_default='completed', nullable=False),
        sa.Column('disclaimer_version', sa.String(length=32), server_default='1.0', nullable=False),
        sa.Column('disclaimer_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_ielts_assessments_participant', 'ielts_practice_assessments', ['participant_id'])

    # 7. assessment_model_runs
    op.create_table(
        'assessment_model_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('pronunciation_assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('model_name', sa.String(length=128), nullable=False),
        sa.Column('model_version', sa.String(length=32), nullable=False),
        sa.Column('model_configuration', sa.JSON(), nullable=True),
        sa.Column('processing_status', sa.String(length=32), server_default='success', nullable=False),
        sa.Column('processing_duration_ms', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_model_runs_assessment_id', 'assessment_model_runs', ['assessment_id'])


def downgrade() -> None:
    op.drop_table('assessment_model_runs')
    op.drop_table('ielts_practice_assessments')
    op.drop_table('pronunciation_recommendations')
    op.drop_table('pronunciation_prosody_results')
    op.drop_table('pronunciation_phoneme_results')
    op.drop_table('pronunciation_word_results')
    op.drop_table('pronunciation_assessments')
