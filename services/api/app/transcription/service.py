"""
FluentMeet AI - Master Transcription & Diarization Orchestrator Service
Specification: Step 07 - Processing Pipeline & Event Distribution
"""

import json
import logging
import uuid
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.audio.storage.object_storage import ObjectStorageService, object_storage
from app.events.publisher import RedisEventPublisher, event_publisher
from app.models.audio import AudioSegment
from app.models.transcript import (
    MeetingSpeaker,
    TranscriptSegment,
    TranscriptWord,
    SpeakerTurn,
    SpeechOverlap,
    TranscriptEvent,
)
from app.websocket.manager import manager
from app.transcription.vad.base import BaseVADProvider
from app.transcription.vad.silero import SileroVADProvider
from app.transcription.asr.base import BaseASRProvider, ASRResult
from app.transcription.asr.faster_whisper import FasterWhisperASRProvider
from app.transcription.diarization.base import BaseDiarizationProvider, DiarizationResult
from app.transcription.diarization.pyannote import PyannoteDiarizationProvider
from app.transcription.alignment.aligner import SpeakerTranscriptAligner, AlignmentOutput

logger = logging.getLogger("transcription.service")

class TranscriptionService:
    def __init__(
        self,
        storage: Optional[ObjectStorageService] = None,
        publisher: Optional[RedisEventPublisher] = None,
        vad_provider: Optional[BaseVADProvider] = None,
        asr_provider: Optional[BaseASRProvider] = None,
        diarization_provider: Optional[BaseDiarizationProvider] = None,
    ):
        self.storage = storage or object_storage
        self.publisher = publisher or event_publisher
        self.vad = vad_provider or SileroVADProvider()
        self.asr = asr_provider or FasterWhisperASRProvider()
        self.diarization = diarization_provider or PyannoteDiarizationProvider()

    async def process_audio_segment(
        self,
        db: AsyncSession,
        segment_id: str,
        storage_key: str,
        meeting_id: str,
        source_id: int,
        segment_start_ms: int = 0,
        expected_checksum: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End-to-end processing pipeline for a single audio segment.
        VAD -> ASR -> Diarization -> Alignment -> Multi-Tenant DB Storage -> Real-time WS Events.
        """
        logger.info(f"Processing audio segment: {segment_id} for meeting: {meeting_id} (source {source_id})")

        # 1. Fetch PCM bytes from durable object storage
        pcm_bytes = self.storage.get_object(storage_key)
        if not pcm_bytes:
            logger.warning(f"Empty audio for segment {segment_id}")
            return {"status": "empty", "segment_id": segment_id}

        # 2. VAD: Detect speech boundaries
        speech_intervals = self.vad.detect_speech(pcm_bytes, sample_rate=16000)
        if not speech_intervals:
            logger.info(f"Segment {segment_id} is pure silence. Skipping ASR.")
            return {"status": "silence", "segment_id": segment_id, "text": ""}

        # 3. ASR: Speech-to-Text with word timestamps
        asr_result: ASRResult = self.asr.transcribe(pcm_bytes, sample_rate=16000, language="en")
        if not asr_result.text.strip():
            logger.info(f"No speech transcribed for segment {segment_id}")
            return {"status": "no_speech", "segment_id": segment_id, "text": ""}

        # 4. Diarization: Speaker turns and overlaps
        diar_result: DiarizationResult = self.diarization.diarize(
            pcm_bytes,
            sample_rate=16000,
            source_id=source_id
        )

        # 5. Alignment: Map words to speaker turns
        alignment: AlignmentOutput = SpeakerTranscriptAligner.align(
            asr_result=asr_result,
            diarization_result=diar_result,
            default_speaker_label="speaker_user_me" if source_id == 0 else "speaker_001"
        )

        # 6. Database Persistence
        # 6a. Ensure MeetingSpeaker records exist
        speaker_map: Dict[str, MeetingSpeaker] = {}
        for aligned_seg in alignment.segments:
            label = aligned_seg.speaker_label
            if label not in speaker_map:
                spk = await self._get_or_create_speaker(db, meeting_id, label, source_id)
                speaker_map[label] = spk

        # 6b. Persist Speaker Turns
        for turn in diar_result.turns:
            spk = speaker_map.get(turn.speaker_label)
            spk_id = spk.id if spk else None
            db_turn = SpeakerTurn(
                id=str(uuid.uuid4()),
                meeting_id=meeting_id,
                speaker_id=spk_id,
                source_id=source_id,
                start_time_ms=segment_start_ms + turn.start_ms,
                end_time_ms=segment_start_ms + turn.end_ms,
                duration_ms=turn.duration_ms,
                turn_index=0
            )
            db.add(db_turn)

        # 6c. Persist Speech Overlaps
        for ov in alignment.overlaps:
            db_overlap = SpeechOverlap(
                id=str(uuid.uuid4()),
                meeting_id=meeting_id,
                start_time_ms=segment_start_ms + ov.start_ms,
                end_time_ms=segment_start_ms + ov.end_ms,
                duration_ms=ov.duration_ms,
                overlapping_speaker_ids=ov.overlapping_speakers,
                confidence_score=ov.confidence
            )
            db.add(db_overlap)

            # Publish speaker.overlap event
            await self._publish_event(
                meeting_id=meeting_id,
                event_type="speaker.overlap",
                payload={
                    "meeting_id": meeting_id,
                    "start_time_ms": segment_start_ms + ov.start_ms,
                    "end_time_ms": segment_start_ms + ov.end_ms,
                    "overlapping_speakers": ov.overlapping_speakers,
                    "confidence_score": ov.confidence
                },
                db=db
            )

        # 6d. Persist Transcript Segments & Granular Words
        persisted_segments: List[Dict[str, Any]] = []

        for aligned_seg in alignment.segments:
            spk = speaker_map.get(aligned_seg.speaker_label)
            spk_id = spk.id if spk else None

            seg_id = str(uuid.uuid4())
            abs_start = segment_start_ms + aligned_seg.start_time_ms
            abs_end = segment_start_ms + aligned_seg.end_time_ms

            words_data = [
                {
                    "word": w.word,
                    "start_time_ms": segment_start_ms + w.start_ms,
                    "end_time_ms": segment_start_ms + w.end_ms,
                    "confidence_score": w.confidence,
                    "is_overlapping": w.is_overlapping,
                }
                for w in aligned_seg.words
            ]

            db_segment = TranscriptSegment(
                id=seg_id,
                meeting_id=meeting_id,
                speaker_id=spk_id,
                source_id=source_id,
                start_time_ms=abs_start,
                end_time_ms=abs_end,
                duration_ms=max(0, abs_end - abs_start),
                text=aligned_seg.text,
                language="en",
                confidence_score=aligned_seg.confidence_score,
                status="final",
                revision_number=1,
                audio_segment_id=segment_id,
                words_json=words_data
            )
            db.add(db_segment)

            # Insert words into transcript_words table
            for idx, w in enumerate(aligned_seg.words):
                w_id = str(uuid.uuid4())
                db_word = TranscriptWord(
                    id=w_id,
                    transcript_segment_id=seg_id,
                    meeting_id=meeting_id,
                    speaker_id=spk_id,
                    word=w.word,
                    start_time_ms=segment_start_ms + w.start_ms,
                    end_time_ms=segment_start_ms + w.end_ms,
                    confidence_score=w.confidence,
                    word_index=idx
                )
                db.add(db_word)

            seg_payload = {
                "id": seg_id,
                "meeting_id": meeting_id,
                "speaker_id": spk_id,
                "speaker_label": aligned_seg.speaker_label,
                "display_name": spk.display_name if spk else aligned_seg.speaker_label,
                "source_id": source_id,
                "start_time_ms": abs_start,
                "end_time_ms": abs_end,
                "text": aligned_seg.text,
                "confidence_score": aligned_seg.confidence_score,
                "status": "final",
                "words": words_data
            }
            persisted_segments.append(seg_payload)

            # Publish transcript.final event
            await self._publish_event(
                meeting_id=meeting_id,
                event_type="transcript.final",
                payload=seg_payload,
                db=db
            )

        await db.commit()

        return {
            "status": "success",
            "segment_id": segment_id,
            "meeting_id": meeting_id,
            "segments": persisted_segments,
            "word_count": alignment.word_count
        }

    async def _get_or_create_speaker(
        self,
        db: AsyncSession,
        meeting_id: str,
        speaker_label: str,
        source_id: int
    ) -> MeetingSpeaker:
        stmt = select(MeetingSpeaker).where(
            and_(
                MeetingSpeaker.meeting_id == meeting_id,
                MeetingSpeaker.speaker_label == speaker_label
            )
        )
        res = await db.execute(stmt)
        speaker = res.scalar_one_or_none()

        if not speaker:
            display_name = "You (Host)" if speaker_label == "speaker_user_me" else speaker_label.replace("_", " ").title()
            speaker = MeetingSpeaker(
                id=str(uuid.uuid4()),
                meeting_id=meeting_id,
                speaker_label=speaker_label,
                display_name=display_name,
                source_id=source_id,
                is_identified=(speaker_label == "speaker_user_me"),
                confidence_score=0.99 if speaker_label == "speaker_user_me" else 0.88
            )
            db.add(speaker)
            await db.flush()

            # Publish speaker.detected event
            await self._publish_event(
                meeting_id=meeting_id,
                event_type="speaker.detected",
                payload={
                    "meeting_id": meeting_id,
                    "speaker_id": speaker.id,
                    "speaker_label": speaker.speaker_label,
                    "display_name": speaker.display_name,
                    "source_id": source_id
                },
                db=db
            )

        return speaker

    async def _publish_event(
        self,
        meeting_id: str,
        event_type: str,
        payload: Dict[str, Any],
        db: Optional[AsyncSession] = None
    ) -> None:
        # 1. Persist to transcript_events table if DB session provided
        if db:
            db_event = TranscriptEvent(
                id=str(uuid.uuid4()),
                meeting_id=meeting_id,
                event_type=event_type,
                payload=payload
            )
            db.add(db_event)

        # 2. Local in-process WebSocket broadcast to active meeting sessions
        try:
            from datetime import datetime, timezone
            await manager.broadcast(
                {
                    "type": event_type,
                    "meeting_id": meeting_id,
                    "payload": payload,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                session_id=meeting_id
            )
        except Exception as e:
            logger.debug(f"Direct WebSocket broadcast skipped or failed: {e}")

        # 3. Publish to Redis Stream for multi-node / distributed workers
        stream_name = f"meeting:{meeting_id}:events"
        try:
            payload["meeting_id"] = meeting_id
            await self.publisher.publish_event(
                stream_name=stream_name,
                event_type=event_type,
                aggregate_id=meeting_id,
                payload=payload
            )
        except Exception as e:
            logger.error(f"Failed to publish event {event_type} to stream {stream_name}: {e}")

# Global singleton
transcription_service = TranscriptionService()
