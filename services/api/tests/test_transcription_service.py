"""
FluentMeet AI - Step 07 Test Suite: Transcription Orchestrator Service
Specification: Step 07 - Processing Pipeline & Multi-Tenant Persistence
"""

import pytest
import uuid
import numpy as np
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select

from app.audio.storage.object_storage import AudioObjectStorage
from app.transcription.service import TranscriptionService
from app.transcription.vad.base import BaseVADProvider, SpeechInterval
from app.transcription.asr.base import BaseASRProvider, ASRResult, ASRSegment, ASRWord
from app.transcription.diarization.base import BaseDiarizationProvider, DiarizationResult, DiarizationSegment
from app.models.base import User, Meeting
from app.models.transcript import (
    MeetingSpeaker,
    TranscriptSegment,
    TranscriptWord,
    SpeakerTurn,
    TranscriptEvent,
)

class MockVAD(BaseVADProvider):
    def __init__(self, intervals):
        self.intervals = intervals
    def detect_speech(self, pcm_bytes, sample_rate=16000, threshold=0.5):
        return self.intervals

class MockASR(BaseASRProvider):
    def __init__(self, result):
        self.result = result
    def transcribe(self, pcm_bytes, sample_rate=16000, language="en"):
        return self.result

class MockDiarization(BaseDiarizationProvider):
    def __init__(self, result):
        self.result = result
    def diarize(self, pcm_bytes, sample_rate=16000, num_speakers=None, source_id=1):
        return self.result

class TestTranscriptionService:
    @pytest.mark.asyncio
    async def test_process_silence_returns_silence_status(self, tmp_path, setup_test_db):
        storage = AudioObjectStorage(base_dir=str(tmp_path))
        mock_vad = MockVAD(intervals=[])
        mock_asr = MockASR(result=ASRResult(text="", language="en"))
        mock_diar = MockDiarization(result=DiarizationResult())

        service = TranscriptionService(
            storage=storage,
            vad_provider=mock_vad,
            asr_provider=mock_asr,
            diarization_provider=mock_diar
        )

        key = "test_meeting/source0/seg1.pcm"
        storage.put_object(key, b"\x00" * 3200)

        db_mock = AsyncMock()
        res = await service.process_audio_segment(
            db=db_mock,
            segment_id="seg-1",
            storage_key=key,
            meeting_id="meet-1",
            source_id=0
        )

        assert res["status"] == "silence"
        assert res["text"] == ""

    @pytest.mark.asyncio
    async def test_end_to_end_transcription_persists_all_entities(self, tmp_path):
        import app.database.session as app_session_mod

        storage = AudioObjectStorage(base_dir=str(tmp_path))
        key = "org1/meet1/s0/seg1.pcm"
        dummy_pcm = b"\x01\x00" * 16000
        storage.put_object(key, dummy_pcm)

        mock_vad = MockVAD(intervals=[SpeechInterval(0, 2000, 0.95)])

        words = [
            ASRWord("Hello", 100, 500, 0.96),
            ASRWord("team", 550, 950, 0.94),
        ]
        seg = ASRSegment(100, 950, "Hello team", 0.95, words)
        mock_asr = MockASR(result=ASRResult("Hello team", "en", [seg], 0.95))

        turns = [DiarizationSegment("speaker_user_me", 0, 2000, 0.99)]
        mock_diar = MockDiarization(result=DiarizationResult(turns=turns))

        mock_publisher = AsyncMock()
        mock_publisher.publish_event = AsyncMock()

        service = TranscriptionService(
            storage=storage,
            publisher=mock_publisher,
            vad_provider=mock_vad,
            asr_provider=mock_asr,
            diarization_provider=mock_diar
        )

        async with app_session_mod.AsyncSessionLocal() as db:
            # Create a meeting first
            user = User(
                id=str(uuid.uuid4()),
                email="host@fluentmeet.ai",
                hashed_password="test",
                full_name="Host User"
            )
            db.add(user)
            await db.flush()

            meeting = Meeting(
                id="meet-active-1",
                user_id=user.id,
                title="Sprint Review",
                platform="google_meet",
                status="in_progress"
            )
            db.add(meeting)
            await db.commit()

            res = await service.process_audio_segment(
                db=db,
                segment_id="seg-uuid-123",
                storage_key=key,
                meeting_id=meeting.id,
                source_id=0,
                segment_start_ms=0
            )

            assert res["status"] == "success"
            assert res["word_count"] == 2
            assert len(res["segments"]) == 1

            # Verify DB tables
            # 1. Speaker
            spk_stmt = select(MeetingSpeaker).where(MeetingSpeaker.meeting_id == meeting.id)
            speakers = (await db.execute(spk_stmt)).scalars().all()
            assert len(speakers) == 1
            assert speakers[0].speaker_label == "speaker_user_me"
            assert speakers[0].display_name == "You (Host)"

            # 2. TranscriptSegment
            seg_stmt = select(TranscriptSegment).where(TranscriptSegment.meeting_id == meeting.id)
            db_segments = (await db.execute(seg_stmt)).scalars().all()
            assert len(db_segments) == 1
            assert db_segments[0].text == "Hello team"
            assert db_segments[0].status == "final"
            assert db_segments[0].confidence_score == 0.95

            # 3. TranscriptWords
            word_stmt = select(TranscriptWord).where(TranscriptWord.meeting_id == meeting.id)
            db_words = (await db.execute(word_stmt)).scalars().all()
            assert len(db_words) == 2
            assert db_words[0].word == "Hello"
            assert db_words[1].word == "team"

            # 4. SpeakerTurns
            turn_stmt = select(SpeakerTurn).where(SpeakerTurn.meeting_id == meeting.id)
            db_turns = (await db.execute(turn_stmt)).scalars().all()
            assert len(db_turns) == 1

            # 5. Events published
            assert mock_publisher.publish_event.call_count >= 1
