"""
FluentMeet AI - Central Audio Ingestion Service
Specification: Step 06 - Section 5, 8, 10, 12, 13 & 14
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.audio.protocol import BinaryAudioProtocol, AudioPacket, ProtocolValidationError
from app.audio.validator import AudioValidator, AudioValidationError
from app.audio.streams.sequence_manager import SequenceManager
from app.audio.streams.synchronizer import AudioSynchronizer
from app.audio.buffering.buffer_manager import AudioBufferManager, BufferOverflowError
from app.audio.buffering.segment_builder import CompletedSegment
from app.audio.storage.object_storage import object_storage
from app.events.publisher import event_publisher
from app.models.audio import (
    AudioStream,
    AudioSegment,
    AudioStreamGap,
    AudioQualityMetric,
    AudioOutboxEvent
)

logger = logging.getLogger("audio.ingestion")

class AudioIngestionService:
    def __init__(self, storage=None, publisher=None):
        self.storage = storage or object_storage
        self.publisher = publisher or event_publisher
        # meeting_id -> SequenceManager
        self.sequence_managers: Dict[str, SequenceManager] = {}
        # meeting_id -> AudioSynchronizer
        self.synchronizers: Dict[str, AudioSynchronizer] = {}
        # meeting_id -> AudioBufferManager
        self.buffer_managers: Dict[str, AudioBufferManager] = {}

    def get_or_create_components(self, meeting_id: str) -> Tuple[SequenceManager, AudioSynchronizer, AudioBufferManager]:
        if meeting_id not in self.sequence_managers:
            self.sequence_managers[meeting_id] = SequenceManager()
            self.synchronizers[meeting_id] = AudioSynchronizer()
            self.buffer_managers[meeting_id] = AudioBufferManager(target_segment_duration_ms=3000)

        return (
            self.sequence_managers[meeting_id],
            self.synchronizers[meeting_id],
            self.buffer_managers[meeting_id]
        )

    async def ingest_binary_packet(
        self,
        raw_bytes: bytes,
        session_id: str,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Processes an incoming binary audio packet.
        Returns a tuple of:
        (Level 1: audio_received ack, Level 2: Optional[audio_persisted ack])
        """
        # 1. Parse Binary Framing Protocol (Section 7)
        packet = BinaryAudioProtocol.decode(raw_bytes)

        # 2. Validate PCM format & parameters (Section 8)
        AudioValidator.validate_format(
            sample_rate=packet.sample_rate,
            channels=packet.channels,
            sample_count=packet.sample_count,
            pcm_bytes=packet.pcm_payload
        )

        seq_mgr, sync_mgr, buf_mgr = self.get_or_create_components(session_id)

        # 3. Check Sequence Numbers & Gap Detection (Section 10)
        seq_result = seq_mgr.check_sequence(packet.source_id, packet.sequence_number)
        if seq_result.is_duplicate:
            logger.warning(f"Duplicate chunk rejected: source={packet.source_id}, seq={packet.sequence_number}")
            return (
                {
                    "type": "audio_received",
                    "status": "duplicate_ignored",
                    "sourceId": packet.source_id,
                    "sequenceNumber": packet.sequence_number,
                },
                None
            )

        if seq_result.gap_range:
            gap_start, gap_end = seq_result.gap_range
            logger.warning(f"Audio sequence gap detected: source={packet.source_id}, range={gap_start}..{gap_end}")
            gap_record = AudioStreamGap(
                stream_id=f"stream-{packet.source_id}",
                source_id=packet.source_id,
                missing_sequence_start=gap_start,
                missing_sequence_end=gap_end,
                gap_resolved=False,
            )
            db.add(gap_record)

        # 4. Synchronize Timeline & Detect Clock Drift (Section 11)
        sync_diag = sync_mgr.track_chunk(packet.source_id, packet.session_relative_timestamp_ms, packet.sample_count)

        # Level 1 Received Acknowledgement (Section 16.3)
        level1_ack = {
            "type": "audio_received",
            "status": "accepted",
            "session_id": session_id,
            "sourceId": packet.source_id,
            "sequenceNumber": packet.sequence_number,
            "sampleCount": packet.sample_count,
            "clockDriftMs": sync_diag.clock_drift_ms,
            "receivedAt": datetime.now(timezone.utc).isoformat(),
        }

        # 5. Push to Bounded Source Buffer (Section 12)
        completed_segment = buf_mgr.push_chunk(packet)
        level2_ack = None

        if completed_segment:
            # Segment duration reached: Persist segment and commit metadata (Section 13)
            level2_ack = await self.persist_segment(completed_segment, organization_id, db)

        return level1_ack, level2_ack

    async def persist_segment(
        self,
        segment: CompletedSegment,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Persists completed audio segment to object storage, commits database metadata,
        and publishes Redis stream event.
        """
        # Step A: Generate deterministic storage key
        storage_key = self.storage.generate_storage_key(
            organization_id=organization_id or "default_org",
            meeting_id=segment.meeting_id,
            stream_id=segment.stream_id,
            source_id=segment.source_id,
            segment_id=segment.segment_id
        )

        # Step B: Upload to private durable object storage with SHA256 checksum
        actual_checksum = self.storage.put_object(
            storage_key=storage_key,
            data=segment.pcm_bytes,
            expected_checksum=segment.checksum
        )

        # Step C: Compute audio quality metrics (RMS, peak, clipping, silence)
        metrics = AudioValidator.calculate_metrics(segment.pcm_bytes, segment.sample_rate)

        # Step D: Persist segment metadata in PostgreSQL
        db_segment = AudioSegment(
            id=segment.segment_id,
            meeting_id=segment.meeting_id,
            organization_id=organization_id,
            stream_id=segment.stream_id,
            source_id=segment.source_id,
            start_timestamp=segment.start_timestamp,
            end_timestamp=segment.end_timestamp,
            first_sequence=segment.first_sequence,
            last_sequence=segment.last_sequence,
            sample_rate=segment.sample_rate,
            channels=segment.channels,
            encoding="pcm_s16le",
            sample_count=segment.sample_count,
            duration_ms=segment.duration_ms,
            checksum=actual_checksum,
            storage_key=storage_key,
            storage_status="persisted",
            processing_status="ready",
        )
        db.add(db_segment)

        # Step E: Persist quality metrics
        db_metrics = AudioQualityMetric(
            segment_id=segment.segment_id,
            rms_level=metrics.rms_level,
            peak_amplitude=metrics.peak_amplitude,
            clipping_ratio=metrics.clipping_ratio,
            silence_ratio=metrics.silence_ratio,
            invalid_sample_count=metrics.invalid_sample_count,
            duration_ms=metrics.duration_ms,
        )
        db.add(db_metrics)

        # Step F: Transactional Outbox Event
        event_payload = {
            "segment_id": segment.segment_id,
            "meeting_id": segment.meeting_id,
            "organization_id": organization_id,
            "stream_id": segment.stream_id,
            "source_id": segment.source_id,
            "storage_key": storage_key,
            "duration_ms": segment.duration_ms,
            "sample_count": segment.sample_count,
            "checksum": actual_checksum,
        }
        outbox_event = AudioOutboxEvent(
            event_type="audio_segment_created",
            aggregate_id=segment.segment_id,
            payload=event_payload,
        )
        db.add(outbox_event)
        await db.commit()

        # Step G: Publish event to Redis Stream (Section 14)
        redis_msg_id = await self.publisher.publish_event(
            stream_name="audio:segment:created",
            event_type="audio_segment_created",
            aggregate_id=segment.segment_id,
            payload=event_payload
        )

        return {
            "type": "audio_persisted",
            "session_id": segment.meeting_id,
            "segmentId": segment.segment_id,
            "sourceId": segment.source_id,
            "durationMs": segment.duration_ms,
            "sampleCount": segment.sample_count,
            "checksum": actual_checksum,
            "storageKey": storage_key,
            "redisMessageId": redis_msg_id,
        }

    async def flush_remaining_audio(
        self,
        session_id: str,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        buf_mgr = self.buffer_managers.get(session_id)
        if not buf_mgr:
            return []

        remaining_segments = buf_mgr.flush_all()
        persisted_acks = []
        for segment in remaining_segments:
            ack = await self.persist_segment(segment, organization_id, db)
            persisted_acks.append(ack)

        return persisted_acks

# Global ingestion service singleton
audio_ingestion_service = AudioIngestionService()
