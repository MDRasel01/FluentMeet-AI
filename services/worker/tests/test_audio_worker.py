"""
FluentMeet AI - Step 06 Test Suite: Background Audio Worker & Consumer Group
Specification: Step 06 - Section 15, 19 & 21 (REQ-ING-015, REQ-ING-016)
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.consumers.audio_stream_consumer import AudioStreamConsumer, STREAM_NAME, CONSUMER_GROUP, DEAD_LETTER_STREAM

class TestAudioWorkerConsumer:
    @pytest.mark.asyncio
    async def test_successful_segment_processing_and_xack(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()

        mock_storage = MagicMock()
        mock_storage.exists.return_value = True

        consumer = AudioStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-worker-1",
            storage_service=mock_storage
        )

        payload = {
            "segment_id": "seg-abc-123",
            "meeting_id": "meet-1",
            "storage_key": "organizations/org1/meetings/meet-1/streams/s1/sources/0/segments/seg-abc-123.pcm",
            "checksum": "valid_sha256_hash",
        }

        msg_data = {
            b"event_type": b"audio_segment_created",
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"0",
        }

        success = await consumer.process_single_message("1000-0", msg_data)

        assert success is True
        mock_storage.exists.assert_called_once_with(payload["storage_key"])
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1000-0")

    @pytest.mark.asyncio
    async def test_missing_storage_triggers_retry(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()
        mock_redis.xadd = AsyncMock()

        mock_storage = MagicMock()
        mock_storage.exists.return_value = False  # File missing

        consumer = AudioStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-worker-1",
            storage_service=mock_storage
        )

        payload = {
            "segment_id": "seg-missing",
            "storage_key": "missing/key.pcm",
        }
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"0",
        }

        success = await consumer.process_single_message("1001-0", msg_data)

        assert success is False
        # Should re-enqueue with retry_count = 1
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args[0]
        assert call_args[0] == STREAM_NAME
        assert call_args[1][b"retry_count"] == b"1"
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1001-0")

    @pytest.mark.asyncio
    async def test_max_retries_routes_to_dead_letter(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()
        mock_redis.xadd = AsyncMock()

        mock_storage = MagicMock()
        mock_storage.exists.side_effect = RuntimeError("Fatal disk failure")

        consumer = AudioStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-worker-1",
            storage_service=mock_storage
        )

        payload = {"segment_id": "seg-fatal"}
        # Already at 2 retries (so next attempt is 3rd = max retries)
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"2",
        }

        success = await consumer.process_single_message("1002-0", msg_data)

        assert success is False
        # Should route to dead letter stream
        call_args = mock_redis.xadd.call_args[0]
        assert call_args[0] == DEAD_LETTER_STREAM
        assert b"error_reason" in call_args[1]
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1002-0")
