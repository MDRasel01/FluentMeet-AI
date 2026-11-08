"""
FluentMeet AI - Step 09 Worker Test Suite: Pronunciation Stream Consumer
Specification: Step 09 - Background Worker Architecture & Resiliency
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.consumers.pronunciation_consumer import (
    PronunciationStreamConsumer,
    STREAM_NAME,
    CONSUMER_GROUP,
    DEAD_LETTER_STREAM,
)


class TestPronunciationWorkerConsumer:
    @pytest.mark.asyncio
    async def test_init_consumer_group(self):
        mock_redis = AsyncMock()
        mock_redis.xgroup_create = AsyncMock()

        consumer = PronunciationStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-pronunciation-worker",
        )
        await consumer.init_consumer_group()
        mock_redis.xgroup_create.assert_called_once_with(
            STREAM_NAME,
            CONSUMER_GROUP,
            id="0",
            mkstream=True,
        )

    @pytest.mark.asyncio
    async def test_process_single_message_success_and_ack(self):
        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock()

        mock_orchestrator = AsyncMock()
        mock_orchestrator.run_assessment = AsyncMock()

        mock_db = AsyncMock()

        consumer = PronunciationStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-pronunciation-worker",
            orchestrator=mock_orchestrator,
        )

        payload = {
            "meeting_id": "meet-200",
            "user_id": "usr-200",
            "speaker_id": "spk-200",
            "participant_id": "part-200",
            "tenant_id": "org-200",
            "force_reassess": False,
        }
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"0",
        }

        success = await consumer.process_single_message("1001-0", msg_data, db_session=mock_db)

        assert success is True
        mock_orchestrator.run_assessment.assert_called_once_with(
            db=mock_db,
            meeting_id="meet-200",
            user_id="usr-200",
            speaker_id="spk-200",
            participant_id="part-200",
            tenant_id="org-200",
            force_reassess=False,
        )
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1001-0")

    @pytest.mark.asyncio
    async def test_handle_failure_retry_increment(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock()
        mock_redis.xack = AsyncMock()

        consumer = PronunciationStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-pronunciation-worker",
        )

        msg_data = {
            b"payload": b'{"meeting_id": "meet-300"}',
            b"retry_count": b"0",
        }

        await consumer.handle_failure("1002-0", msg_data, "Database connection timeout")

        # Verify added back to STREAM_NAME with retry_count 1
        mock_redis.xadd.assert_called_once()
        args = mock_redis.xadd.call_args[0]
        assert args[0] == STREAM_NAME
        assert args[1][b"retry_count"] == b"1"
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1002-0")

    @pytest.mark.asyncio
    async def test_handle_failure_moves_to_dlq_after_max_retries(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock()
        mock_redis.xack = AsyncMock()

        consumer = PronunciationStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-pronunciation-worker",
        )

        msg_data = {
            b"payload": b'{"meeting_id": "meet-400"}',
            b"retry_count": b"2",  # Current is 2, next will be 3 (MAX_RETRIES)
        }

        await consumer.handle_failure("1003-0", msg_data, "Fatal acoustic corruption")

        mock_redis.xadd.assert_called_once()
        args = mock_redis.xadd.call_args[0]
        assert args[0] == DEAD_LETTER_STREAM
        assert b"error_reason" in args[1]
        assert b"Fatal acoustic corruption" in args[1][b"error_reason"]
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1003-0")

    @pytest.mark.asyncio
    async def test_claim_stale_messages(self):
        mock_redis = AsyncMock()
        mock_redis.xautoclaim = AsyncMock(
            return_value=(
                "0-0",
                [("1004-0", {b"payload": b'{"meeting_id": "meet-500"}', b"retry_count": b"0"})],
                [],
            )
        )
        mock_redis.xack = AsyncMock()

        consumer = PronunciationStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-pronunciation-worker",
        )

        reclaimed = await consumer.claim_stale_messages()
        assert reclaimed == 1
        mock_redis.xautoclaim.assert_called_once()

