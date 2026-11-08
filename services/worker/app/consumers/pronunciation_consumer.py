"""
FluentMeet AI - Pronunciation & IELTS Assessment Stream Consumer Worker
Specification: Step 09 - Background Worker Architecture & Job Processing
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("worker.pronunciation_consumer")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM_NAME = "pronunciation:jobs"
CONSUMER_GROUP = "pronunciation_workers"
DEAD_LETTER_STREAM = "pronunciation:jobs:dlq"
MAX_RETRIES = 3
IDLE_RECLAIM_TIME_MS = 60000  # 60s idle before reclaim


class PronunciationStreamConsumer:
    """
    Consumes asynchronous Pronunciation and IELTS assessment jobs from Redis Streams.
    Coordinates acoustic scoring, prosody analysis, and IELTS practice estimation.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_client: Optional[aioredis.Redis] = None,
        consumer_id: Optional[str] = None,
        orchestrator: Optional[Any] = None,
    ):
        self.redis_url = redis_url or REDIS_URL
        self.redis_client = redis_client
        self.consumer_id = consumer_id or f"pronunciation-worker-{uuid.uuid4().hex[:8]}"
        self.orchestrator = orchestrator
        self.is_running = False

    async def get_redis(self) -> aioredis.Redis:
        if self.redis_client is None:
            self.redis_client = aioredis.from_url(self.redis_url, decode_responses=False)
        return self.redis_client

    async def init_consumer_group(self):
        r = await self.get_redis()
        try:
            await r.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="0", mkstream=True)
            logger.info(f"Created Redis stream consumer group {CONSUMER_GROUP} on {STREAM_NAME}")
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group {CONSUMER_GROUP} already exists on {STREAM_NAME}")
            else:
                logger.error(f"Error creating consumer group: {e}")

    async def process_single_message(
        self,
        message_id: str,
        message_data: Dict[bytes, bytes],
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        r = await self.get_redis()
        try:
            payload_raw = message_data.get(b"payload", b"{}")
            if isinstance(payload_raw, bytes):
                payload = json.loads(payload_raw.decode("utf-8"))
            else:
                payload = json.loads(payload_raw)

            meeting_id = payload.get("meeting_id")
            user_id = payload.get("user_id")
            speaker_id = payload.get("speaker_id")
            participant_id = payload.get("participant_id")
            tenant_id = payload.get("tenant_id")
            force_reassess = bool(payload.get("force_reassess", False))

            logger.info(f"Pronunciation worker processing meeting {meeting_id} (speaker {speaker_id})")

            if self.orchestrator and db_session:
                await self.orchestrator.run_assessment(
                    db=db_session,
                    meeting_id=meeting_id,
                    user_id=user_id,
                    speaker_id=speaker_id,
                    participant_id=participant_id,
                    tenant_id=tenant_id,
                    force_reassess=force_reassess,
                )

            # Acknowledge processed message
            await r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
            logger.info(f"Successfully processed pronunciation message {message_id}")
            return True

        except Exception as err:
            logger.error(f"Failed to process pronunciation message {message_id}: {err}")
            await self.handle_failure(message_id, message_data, str(err))
            return False

    async def handle_failure(
        self, message_id: str, message_data: Dict[bytes, bytes], error_reason: str
    ):
        r = await self.get_redis()
        current_retries = int(message_data.get(b"retry_count", b"0")) + 1

        if current_retries >= MAX_RETRIES:
            logger.warning(f"Max retries reached for pronunciation message {message_id}. Moving to DLQ.")
            dlq_payload = dict(message_data)
            dlq_payload[b"error_reason"] = error_reason.encode("utf-8")
            dlq_payload[b"failed_at"] = str(uuid.uuid4()).encode("utf-8")
            dlq_payload[b"original_message_id"] = message_id.encode("utf-8")
            await r.xadd(DEAD_LETTER_STREAM, dlq_payload)
            await r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
        else:
            updated = dict(message_data)
            updated[b"retry_count"] = str(current_retries).encode("utf-8")
            await r.xadd(STREAM_NAME, updated)
            await r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)

    async def claim_stale_messages(self) -> int:
        r = await self.get_redis()
        try:
            claim_result = await r.xautoclaim(
                name=STREAM_NAME,
                groupname=CONSUMER_GROUP,
                consumername=self.consumer_id,
                min_idle_time=IDLE_RECLAIM_TIME_MS,
                start_id="0-0",
                count=10,
            )
            if claim_result and len(claim_result) >= 2:
                claimed_messages = claim_result[1]
                logger.info(f"Reclaimed {len(claimed_messages)} stale pronunciation messages")
                for msg_id, msg_data in claimed_messages:
                    str_id = msg_id.decode("utf-8") if isinstance(msg_id, bytes) else str(msg_id)
                    await self.process_single_message(str_id, msg_data)
                return len(claimed_messages)
            return 0
        except Exception as e:
            logger.error(f"Error claiming stale pronunciation messages: {e}")
            return 0

