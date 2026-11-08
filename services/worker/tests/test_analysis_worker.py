"""
FluentMeet AI - Step 08 Worker Test Suite: Analysis Stream Consumer
Specification: Step 08 - Background Worker Architecture & Resiliency
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.consumers.analysis_consumer import (
    AnalysisStreamConsumer,
    STREAM_NAME,
    CONSUMER_GROUP,
    DEAD_LETTER_STREAM,
)


class TestAnalysisWorkerConsumer:
    @pytest.mark.asyncio
    async def test_init_consumer_group(self):
        mock_redis = AsyncMock()
        mock_redis.xgroup_create = AsyncMock()

        consumer = AnalysisStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-analysis-worker",
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
        mock_orchestrator.run_analysis = AsyncMock()

        mock_db = AsyncMock()

        consumer = AnalysisStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-analysis-worker",
            orchestrator=mock_orchestrator,
        )

        payload = {
            "meeting_id": "meet-100",
            "user_id": "usr-100",
            "tenant_id": "org-100",
            "session_id": "sess-100",
            "force_reanalyze": False,
        }
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"0",
        }

        success = await consumer.process_single_message(
            message_id="1710000000000-0",
            message_data=msg_data,
            db_session=mock_db,
        )

        assert success is True
        mock_orchestrator.run_analysis.assert_called_once_with(
            db=mock_db,
            meeting_id="meet-100",
            user_id="usr-100",
            tenant_id="org-100",
            session_id="sess-100",
            force_reanalyze=False,
        )
        mock_redis.xack.assert_called_once_with(
            STREAM_NAME, CONSUMER_GROUP, "1710000000000-0"
        )

    @pytest.mark.asyncio
    async def test_handle_failure_retry_routing(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock()
        mock_redis.xack = AsyncMock()

        consumer = AnalysisStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-analysis-worker",
        )

        msg_data = {
            b"payload": b'{"meeting_id": "meet-failed"}',
            b"retry_count": b"1",
        }

        await consumer.handle_failure("1710000000000-1", msg_data, "Timeout during Gemini API call")

        # Must increment retry_count to 2 and republish
        assert mock_redis.xadd.call_count == 1
        args = mock_redis.xadd.call_args[0]
        assert args[0] == STREAM_NAME
        assert args[1][b"retry_count"] == b"2"
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1710000000000-1")

    @pytest.mark.asyncio
    async def test_handle_failure_dlq_routing_on_max_retries(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock()
        mock_redis.xack = AsyncMock()

        consumer = AnalysisStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-analysis-worker",
        )

        msg_data = {
            b"payload": b'{"meeting_id": "meet-fatal"}',
            b"retry_count": b"2",  # 2 + 1 = 3 -> MAX_RETRIES
        }

        await consumer.handle_failure("1710000000000-2", msg_data, "Permanent failure")

        # Must route to DLQ
        assert mock_redis.xadd.call_count == 1
        args = mock_redis.xadd.call_args[0]
        assert args[0] == DEAD_LETTER_STREAM
        assert b"error_reason" in args[1]
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "1710000000000-2")

