"""Add transcript and diarization schema

Revision ID: 003_transcript_diarization
Revises: 002_auth_and_organizations
Create Date: 2026-11-07 13:10:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_transcript_diarization'
down_revision: Union[str, None] = '002_auth_and_organizations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. meeting_speakers
    op.create_table(
        'meeting_speakers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker_label', sa.String(length=64), nullable=False),
        sa.Column('display_name', sa.String(length=128), nullable=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('participant_id', sa.String(length=36), sa.ForeignKey('meeting_participants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_identified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('voice_embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('meeting_id', 'speaker_label', name='uq_meeting_speaker_label'),
    )
    op.create_index('ix_meeting_speakers_meeting_id', 'meeting_speakers', ['meeting_id'])
    op.create_index('ix_meeting_speakers_meeting_source', 'meeting_speakers', ['meeting_id', 'source_id'])

    # 2. transcript_segments
    op.create_table(
        'transcript_segments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker_id', sa.String(length=36), sa.ForeignKey('meeting_speakers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_id', sa.Integer(), server_default='0', nullable=False),
        sa.Column('start_time_ms', sa.Integer(), nullable=False),
        sa.Column('end_time_ms', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=16), server_default='en', nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=32), server_default='partial', nullable=False),
        sa.Column('revision_number', sa.Integer(), server_default='1', nullable=False),
        sa.Column('audio_segment_id', sa.String(length=36), sa.ForeignKey('audio_segments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('words_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_transcript_segments_meeting_id', 'transcript_segments', ['meeting_id'])
    op.create_index('ix_transcript_segment_meeting_time', 'transcript_segments', ['meeting_id', 'start_time_ms', 'end_time_ms'])
    op.create_index('ix_transcript_segment_status', 'transcript_segments', ['meeting_id', 'status'])

    # 3. transcript_words
    op.create_table(
        'transcript_words',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('transcript_segment_id', sa.String(length=36), sa.ForeignKey('transcript_segments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker_id', sa.String(length=36), sa.ForeignKey('meeting_speakers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('word', sa.String(length=128), nullable=False),
        sa.Column('start_time_ms', sa.Integer(), nullable=False),
        sa.Column('end_time_ms', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('word_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_transcript_words_meeting_time', 'transcript_words', ['meeting_id', 'start_time_ms'])

    # 4. speaker_turns
    op.create_table(
        'speaker_turns',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker_id', sa.String(length=36), sa.ForeignKey('meeting_speakers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', sa.Integer(), server_default='0', nullable=False),
        sa.Column('start_time_ms', sa.Integer(), nullable=False),
        sa.Column('end_time_ms', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('turn_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_speaker_turns_meeting_interval', 'speaker_turns', ['meeting_id', 'start_time_ms', 'end_time_ms'])

    # 5. speech_overlaps
    op.create_table(
        'speech_overlaps',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_time_ms', sa.Integer(), nullable=False),
        sa.Column('end_time_ms', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('overlapping_speaker_ids', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_speech_overlaps_meeting_interval', 'speech_overlaps', ['meeting_id', 'start_time_ms', 'end_time_ms'])

    # 6. transcript_events
    op.create_table(
        'transcript_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('meeting_id', sa.String(length=36), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_transcript_events_meeting_type', 'transcript_events', ['meeting_id', 'event_type'])


def downgrade() -> None:
    op.drop_table('transcript_events')
    op.drop_table('speech_overlaps')
    op.drop_table('speaker_turns')
    op.drop_table('transcript_words')
    op.drop_table('transcript_segments')
    op.drop_table('meeting_speakers')
