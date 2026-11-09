"""
FluentMeet AI - Step 10 Worker Test Suite: Report Generation Stream Consumer
Specification: Step 10 - Background Worker Architecture & Resiliency
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.consumers.report_consumer import (
    ReportStreamConsumer,
    STREAM_NAME,
    CONSUMER_GROUP,
    DEAD_LETTER_STREAM,
)


class TestReportWorkerConsumer:
    @pytest.mark.asyncio
    async def test_init_consumer_group(self):
        mock_redis = AsyncMock()
        mock_redis.xgroup_create = AsyncMock()

        consumer = ReportStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-report-worker",
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
        mock_orchestrator.generate_meeting_reports = AsyncMock()

        mock_db = AsyncMock()

        consumer = ReportStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-report-worker",
            orchestrator=mock_orchestrator,
        )

        payload = {
            "meeting_id": "meet-rep-100",
            "user_id": "usr-rep-100",
            "tenant_id": "org-rep-100",
            "force_regenerate": False,
            "scoring_rubric_version": "1.0",
        }
        msg_data = {
            b"payload": json.dumps(payload).encode("utf-8"),
            b"retry_count": b"0",
        }

        success = await consumer.process_single_message(
            message_id="msg-rep-001",
            message_data=msg_data,
            db_session=mock_db,
        )

        assert success is True
        mock_orchestrator.generate_meeting_reports.assert_called_once_with(
            db=mock_db,
            meeting_id="meet-rep-100",
            user_id="usr-rep-100",
            tenant_id="org-rep-100",
            force_regenerate=False,
            scoring_rubric_version="1.0",
        )
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "msg-rep-001")

    @pytest.mark.asyncio
    async def test_handle_failure_retry(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock()
        mock_redis.xack = AsyncMock()

        mock_orchestrator = AsyncMock()
        mock_orchestrator.generate_meeting_reports = AsyncMock(side_effect=Exception("Database lock timeout"))

        consumer = ReportStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-report-worker",
            orchestrator=mock_orchestrator,
        )

        msg_data = {
            b"payload": b'{"meeting_id": "meet-fail-1"}',
            b"retry_count": b"1",
        }

        success = await consumer.process_single_message(
            message_id="msg-rep-fail-1",
            message_data=msg_data,
            db_session=AsyncMock(),
        )

        assert success is False
        # Should republish with incremented retry count
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == STREAM_NAME
        assert call_args[0][1][b"retry_count"] == b"2"
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "msg-rep-fail-1")

    @pytest.mark.asyncio
    async def test_handle_failure_dlq_on_max_retries(self):
        mock_redis = AsyncMock()
        mock_redis.xadd = AsyncMock()
        mock_redis.xack = AsyncMock()

        mock_orchestrator = AsyncMock()
        mock_orchestrator.generate_meeting_reports = AsyncMock(side_effect=Exception("Fatal corrupted payload"))

        consumer = ReportStreamConsumer(
            redis_client=mock_redis,
            consumer_id="test-report-worker",
            orchestrator=mock_orchestrator,
        )

        msg_data = {
            b"payload": b'{"meeting_id": "meet-fatal-dlq"}',
            b"retry_count": b"2",  # next retry is 3 => max reached
        }

        success = await consumer.process_single_message(
            message_id="msg-rep-dlq-1",
            message_data=msg_data,
            db_session=AsyncMock(),
        )

        assert success is False
        # Should publish to DEAD_LETTER_STREAM
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == DEAD_LETTER_STREAM
        assert b"error_reason" in call_args[0][1]
        mock_redis.xack.assert_called_once_with(STREAM_NAME, CONSUMER_GROUP, "msg-rep-dlq-1")

