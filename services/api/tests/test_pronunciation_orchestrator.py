"""
FluentMeet AI - Step 09 Test Suite: Pronunciation Orchestrator End-to-End
Specification: Step 09 - Section 17 & 18
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Meeting, User, Organization
from app.models.transcript import MeetingSpeaker, TranscriptSegment, TranscriptWord
from app.models.audio import AudioSegment, AudioStream
from app.models.pronunciation import PronunciationAssessment
from app.pronunciation.orchestrator import PronunciationOrchestrator


class TestPronunciationOrchestrator:
    @pytest.mark.asyncio
    async def test_orchestrator_successful_assessment_run(self, db_session: AsyncSession = None):
        """End-to-end assessment execution creating words, prosody, recommendations, and IELTS estimate."""
        from app.database.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            # 1. Seed user, org, and meeting
            user = User(email="speaker_user@example.com", hashed_password="pwd", full_name="Speaker User")
            session.add(user)
            await session.flush()

            meeting = Meeting(user_id=user.id, title="Product Strategy Meeting", platform="google_meet", status="ended")
            session.add(meeting)
            await session.flush()

            speaker = MeetingSpeaker(
                meeting_id=meeting.id,
                speaker_label="speaker_001",
                display_name="Product Lead",
                source_id=0,
                confidence_score=0.92,
            )
            session.add(speaker)
            await session.flush()

            # 2. Seed transcript segment with >= 5 words
            seg = TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=speaker.id,
                start_time_ms=1000,
                end_time_ms=4000,
                duration_ms=3000,
                text="we think project architecture has favorable outcomes",
                language="en",
                status="final",
            )
            session.add(seg)
            await session.flush()

            words = [
                ("we", 1000, 1300),
                ("think", 1350, 1750),
                ("project", 1800, 2250),
                ("architecture", 2300, 2900),
                ("has", 2950, 3200),
                ("favorable", 3250, 3700),
                ("outcomes", 3750, 4000),
            ]
            for idx, (w, s, e) in enumerate(words):
                session.add(
                    TranscriptWord(
                        transcript_segment_id=seg.id,
                        meeting_id=meeting.id,
                        speaker_id=speaker.id,
                        word=w,
                        start_time_ms=s,
                        end_time_ms=e,
                        word_index=idx,
                    )
                )
            await session.commit()

            # 3. Create synthetic audio PCM (16kHz 16-bit mono 3.5s)
            sample_rate = 16000
            t = np.linspace(0, 3.5, int(sample_rate * 3.5), False)
            sine_wave = 0.5 * np.sin(2 * np.pi * 180 * t) + 0.1 * np.sin(2 * np.pi * 3200 * t)
            synth_pcm = (sine_wave * 16384).astype(np.int16).tobytes()

            mock_publisher = AsyncMock()
            mock_publisher.publish_event = AsyncMock()

            orchestrator = PronunciationOrchestrator(event_publisher=mock_publisher)

            assessments = await orchestrator.run_assessment(
                db=session,
                meeting_id=meeting.id,
                user_id=user.id,
                speaker_id=speaker.id,
                audio_override_bytes=synth_pcm,
            )

            assert len(assessments) == 1
            asmt = assessments[0]
            assert asmt.assessment_status == "completed"
            assert asmt.overall_pronunciation_score is not None
            assert asmt.overall_pronunciation_score >= 60.0
            assert asmt.evaluated_word_count >= 5

            # Verify published completion event
            mock_publisher.publish_event.assert_called_once()
            call_args = mock_publisher.publish_event.call_args[1]
            assert call_args["stream_name"] == "pronunciation:events"
            assert call_args["event_type"] == "pronunciation.completed"

    @pytest.mark.asyncio
    async def test_orchestrator_insufficient_words_gate(self):
        """When evaluated speech words < 5, status is insufficient_evidence and overall_score is None."""
        from app.database.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            user = User(email="brief_user@example.com", hashed_password="pwd", full_name="Brief User")
            session.add(user)
            await session.flush()

            meeting = Meeting(user_id=user.id, title="Brief Sync", platform="google_meet", status="ended")
            session.add(meeting)
            await session.flush()

            speaker = MeetingSpeaker(
                meeting_id=meeting.id,
                speaker_label="speaker_brief",
                source_id=0,
            )
            session.add(speaker)
            await session.flush()

            # Only 2 words
            seg = TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=speaker.id,
                start_time_ms=1000,
                end_time_ms=1800,
                duration_ms=800,
                text="hello yes",
                language="en",
                status="final",
            )
            session.add(seg)
            await session.flush()

            session.add(TranscriptWord(transcript_segment_id=seg.id, meeting_id=meeting.id, word="hello", start_time_ms=1000, end_time_ms=1350))
            session.add(TranscriptWord(transcript_segment_id=seg.id, meeting_id=meeting.id, word="yes", start_time_ms=1400, end_time_ms=1750))
            await session.commit()

            synth_pcm = (np.ones(16000, dtype=np.int16) * 500).tobytes()

            orchestrator = PronunciationOrchestrator(event_publisher=AsyncMock())
            assessments = await orchestrator.run_assessment(
                db=session,
                meeting_id=meeting.id,
                user_id=user.id,
                speaker_id=speaker.id,
                audio_override_bytes=synth_pcm,
            )

            assert len(assessments) == 1
            asmt = assessments[0]
            assert asmt.assessment_status == "insufficient_evidence"
            assert asmt.overall_pronunciation_score is None
            assert asmt.evaluated_word_count < 5

    @pytest.mark.asyncio
    async def test_orchestrator_missing_audio_gate(self):
        """When audio buffer is missing, does not fabricate scores and returns audio_missing."""
        from app.database.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            user = User(email="no_audio_user@example.com", hashed_password="pwd", full_name="No Audio User")
            session.add(user)
            await session.flush()

            meeting = Meeting(user_id=user.id, title="No Audio Meeting", platform="google_meet", status="ended")
            session.add(meeting)
            await session.flush()

            speaker = MeetingSpeaker(
                meeting_id=meeting.id,
                speaker_label="speaker_silent",
                source_id=0,
            )
            session.add(speaker)
            await session.flush()

            seg = TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=speaker.id,
                start_time_ms=1000,
                end_time_ms=4000,
                duration_ms=3000,
                text="this is a meeting without physical audio segment files",
                status="final",
            )
            session.add(seg)
            await session.commit()

            orchestrator = PronunciationOrchestrator(event_publisher=AsyncMock())
            # Run without audio override and without audio segments in storage
            assessments = await orchestrator.run_assessment(
                db=session,
                meeting_id=meeting.id,
                user_id=user.id,
                speaker_id=speaker.id,
            )

            assert len(assessments) == 1
            asmt = assessments[0]
            assert asmt.assessment_status == "insufficient_evidence"
            assert asmt.audio_quality_status == "audio_missing"
            assert asmt.overall_pronunciation_score is None
