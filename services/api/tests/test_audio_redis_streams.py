"""
FluentMeet AI - Step 06 Test Suite: Redis Streams Event Transport
Specification: Step 06 - Section 14 & 21 (REQ-ING-014, REQ-ING-015)
"""

import pytest
import json
from unittest.mock import AsyncMock
from app.events.publisher import EventPublisher

class TestRedisStreamsPublisher:
    @pytest.mark.asyncio
    async def test_publish_event_schema_and_call(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock(return_value="1700000000000-0")

        publisher = EventPublisher(redis_client=mock_redis)

        payload = {
            "segment_id": "seg-1234",
            "meeting_id": "meet-5678",
            "source_id": 0,
            "duration_ms": 3000,
            "checksum": "abc123def456"
        }

        msg_id = await publisher.publish_event(
            stream_name="audio:segment:created",
            event_type="audio_segment_created",
            aggregate_id="seg-1234",
            payload=payload
        )

        assert msg_id == "1700000000000-0"
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args[0]
        assert call_args[0] == "audio:segment:created"
        assert call_args[1]["event_type"] == "audio_segment_created"
        assert call_args[1]["aggregate_id"] == "seg-1234"
        assert json.loads(call_args[1]["payload"]) == payload

    @pytest.mark.asyncio
    async def test_publish_event_graceful_fallback_when_redis_offline(self):
        # When Redis fails, publish_event logs error and generates simulated id without crashing app
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock(side_effect=ConnectionError("Redis connection refused"))

        publisher = EventPublisher(redis_client=mock_redis)
        msg_id = await publisher.publish_event(
            stream_name="audio:segment:created",
            event_type="audio_segment_created",
            aggregate_id="seg-1234",
            payload={"test": "data"}
        )
        assert msg_id.startswith("simulated-")
