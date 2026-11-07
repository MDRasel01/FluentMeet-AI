"""
FluentMeet AI - Step 07 Worker Test Suite: Transcription Stream Consumer
Specification: Step 07 - Section 7 (Worker Architecture & Resiliency)
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.consumers.transcription_consumer import (
    TranscriptionStreamConsumer,
    STREAM_NAME,
    CONSUMER_GROUP,
    DEAD_LETTER_STREAM,
)

class TestTranscriptionWorkerConsumer:
    @pytest.mark.asyncio
    async def test_init_consumer_group(self):
        mock_redis = AsyncMock()
        mock_redis.xgroup_create = AsyncMock()

        consumer = TranscriptionStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-transcription-worker"
        )
        await consumer.init_consumer_group()
        mock_redis.xgroup_create.assert_called_once_with(
            STREAM_NAME,
            CONSUMER_GROUP,
            id="0",
            mkstream=True
        )

    @pytest.mark.asyncio
    async def test_process_single_message_success_and_ack(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()

        mock_storage = MagicMock()
        mock_storage.exists.return_value = True

        mock_service = AsyncMock()
        mock_service.process_audio_segment = AsyncMock()

        consumer = TranscriptionStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-transcription-worker",
            service=mock_service,
            storage_service=mock_storage
        )

        payload = {
            "segment_id": "seg-test-123",
            "storage_key": "org1/meet1/s0/seg-test-123.pcm",
            "meeting_id": "meet-1",
            "source_id": 0,
            "start_time_ms": 0,
        }
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"0",
        }

        mock_db = AsyncMock()
        success = await consumer.process_single_message("1001-0", msg_data, db_session=mock_db)

        assert success is True
        mock_service.process_audio_segment.assert_called_once()
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1001-0")

    @pytest.mark.asyncio
    async def test_max_retries_routes_to_dead_letter(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()
        mock_redis.xadd = AsyncMock()

        mock_storage = MagicMock()
        mock_storage.exists.side_effect = RuntimeError("Fatal disk failure")

        consumer = TranscriptionStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-transcription-worker",
            storage_service=mock_storage
        )

        payload = {
            "segment_id": "seg-fatal-1",
            "storage_key": "some/missing/key.pcm",
            "meeting_id": "meet-1"
        }
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"2",  # next is 3 = max retries
        }

        mock_db = AsyncMock()
        success = await consumer.process_single_message("1002-0", msg_data, db_session=mock_db)

        assert success is False
        call_args = mock_redis.xadd.call_args[0]
        assert call_args[0] == DEAD_LETTER_STREAM
        assert b"error_reason" in call_args[1]
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1002-0")

    @pytest.mark.asyncio
    async def test_claim_stale_messages(self):
        mock_redis = AsyncMock()
        stale_msg = (b"1003-0", {b"payload": b"{}", b"retry_count": b"0"})
        mock_redis.xautoclaim.return_value = ("0-0", [stale_msg], [])
        mock_redis.xack = AsyncMock()

        mock_storage = MagicMock()
        mock_storage.exists.return_value = True

        consumer = TranscriptionStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-transcription-worker",
            storage_service=mock_storage
        )

        claimed_count = await consumer.claim_stale_messages()
        assert claimed_count == 1

