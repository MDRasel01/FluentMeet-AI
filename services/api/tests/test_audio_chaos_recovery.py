"""
FluentMeet AI - Step 06 Test Suite: Chaos Engineering & Failure Recovery
Specification: Step 06 - Section 19 & 21 (REQ-ING-017)
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock
from app.audio.protocol import BinaryAudioProtocol, AudioPacket
from app.audio.service import AudioIngestionService
from app.workers.audio_worker import AudioStreamConsumer, STREAM_NAME, CONSUMER_GROUP

def make_packet(meeting_id: str, source_id: int, seq: int, ts: float, duration_ms: int = 500) -> bytes:
    sample_count = int(16000 * (duration_ms / 1000.0))
    pcm = np.zeros(sample_count, dtype=np.int16).tobytes()
    packet = AudioPacket(
        version=1,
        source_id=source_id,
        sequence_number=seq,
        session_relative_timestamp_ms=ts,
        sample_rate=16000,
        channels=1,
        encoding=1,
        sample_count=sample_count,
        meeting_id=meeting_id,
        pcm_payload=pcm,
    )
    return BinaryAudioProtocol.encode(packet)

class TestAudioChaosRecovery:
    @pytest.mark.asyncio
    async def test_duplicate_packet_chaos_rejection(self):
        service = AudioIngestionService()
        meeting_id = "chaos-meeting-dup"
        db_mock = AsyncMock()

        # Send chunk seq 1
        raw1 = make_packet(meeting_id, source_id=0, seq=1, ts=0.0)
        l1_ack1, _ = await service.ingest_binary_packet(raw1, meeting_id, "org1", db_mock)
        assert l1_ack1["status"] == "accepted"

        # Replay chunk seq 1 (simulated network replay)
        l1_ack_dup, l2_dup = await service.ingest_binary_packet(raw1, meeting_id, "org1", db_mock)
        assert l1_ack_dup["status"] == "duplicate_ignored"
        assert l2_dup is None

    @pytest.mark.asyncio
    async def test_consumer_stale_message_reclaim_via_xautoclaim(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()

        # Mock xautoclaim returning 1 reclaimed message
        claimed_msg_id = b"1700000000000-0"
        claimed_payload = {
            b"payload": b'{"segment_id": "seg-recovered", "storage_key": "dummy.pcm"}',
            b"retry_count": b"0",
        }
        mock_redis.xautoclaim = AsyncMock(return_value=("0-0", [(claimed_msg_id, claimed_payload)]))

        mock_storage = MagicMock()
        mock_storage.exists.return_value = True

        consumer = AudioStreamConsumer(
            redis_client=mock_redis,
            consumer_id="recovering-worker",
            storage_service=mock_storage
        )

        reclaimed_count = await consumer.claim_stale_pending_messages()
        assert reclaimed_count == 1
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1700000000000-0")
