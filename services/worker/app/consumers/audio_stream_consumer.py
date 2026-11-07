"""
FluentMeet AI - Redis Streams Audio Segment Consumer Worker
Specification: Step 06 - Section 14, 15 & 19
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

logger = logging.getLogger("worker.audio_consumer")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
STREAM_NAME = "audio:segment:created"
CONSUMER_GROUP = "audio_workers"
DEAD_LETTER_STREAM = "audio:dead-letter"
MAX_RETRIES = 3
IDLE_RECLAIM_TIME_MS = 60000  # 60 seconds

class AudioStreamConsumer:
    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        consumer_id: Optional[str] = None,
        db_session_factory: Optional[async_sessionmaker] = None,
        storage_service = None,
    ):
        self.redis = redis_client
        self.consumer_id = consumer_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.db_session_factory = db_session_factory
        self.storage = storage_service
        self._running = False

    async def get_redis(self) -> aioredis.Redis:
        if self.redis is None:
            self.redis = aioredis.from_url(REDIS_URL, decode_responses=False)
        return self.redis

    async def init_consumer_group(self):
        r = await self.get_redis()
        try:
            await r.xgroup_create(
                name=STREAM_NAME,
                groupname=CONSUMER_GROUP,
                id="$",
                mkstream=True
            )
            logger.info(f"Created Redis Stream Consumer Group: {CONSUMER_GROUP} on {STREAM_NAME}")
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.debug(f"Consumer group {CONSUMER_GROUP} already exists.")
            else:
                logger.error(f"Error creating consumer group: {e}")
                raise

    async def process_single_message(
        self,
        message_id: str,
        message_data: Dict[bytes, bytes],
        db_session: Optional[AsyncSession] = None
    ) -> bool:
        """
        Idempotently processes one audio segment event.
        Returns True if successful and acknowledged, False if processing failed.
        """
        r = await self.get_redis()
        try:
            # Decode payload
            payload_raw = message_data.get(b"payload", b"{}")
            if isinstance(payload_raw, bytes):
                payload = json.loads(payload_raw.decode("utf-8"))
            else:
                payload = json.loads(payload_raw)

            retry_count = int(message_data.get(b"retry_count", b"0"))
            segment_id = payload.get("segment_id")
            storage_key = payload.get("storage_key")
            expected_checksum = payload.get("checksum")

            logger.info(f"Processing audio segment: id={segment_id}, retry={retry_count}")

            # Verify storage and checksum if storage service injected
            if self.storage and storage_key:
                exists = self.storage.exists(storage_key)
                if not exists:
                    raise FileNotFoundError(f"Segment data missing in storage for key: {storage_key}")

            # Update DB segment processing status to 'ready' or 'completed'
            if db_session and segment_id:
                # Local or dynamic model import to prevent circular dependency
                from app.models.audio import AudioSegment
                stmt = select(AudioSegment).where(AudioSegment.id == segment_id)
                res = await db_session.execute(stmt)
                seg = res.scalar_one_or_none()
                if seg:
                    seg.processing_status = "ready_for_transcription"
                    await db_session.commit()

            # Acknowledge message in Redis Stream
            await r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
            logger.info(f"Successfully processed and acknowledged message {message_id} (segment: {segment_id})")
            return True

        except Exception as err:
            logger.error(f"Failed to process message {message_id}: {err}")
            await self.handle_failure(message_id, message_data, str(err))
            return False

    async def handle_failure(self, message_id: str, message_data: Dict[bytes, bytes], error_reason: str):
        r = await self.get_redis()
        current_retries = int(message_data.get(b"retry_count", b"0")) + 1

        if current_retries >= MAX_RETRIES:
            logger.warning(
                f"Max retries ({MAX_RETRIES}) reached for message {message_id}. Moving to Dead-Letter stream."
            )
            # Route to dead-letter stream
            dlq_payload = dict(message_data)
            dlq_payload[b"error_reason"] = error_reason.encode("utf-8")
            dlq_payload[b"failed_at"] = str(uuid.uuid4()).encode("utf-8")
            dlq_payload[b"original_message_id"] = message_id.encode("utf-8")
            await r.xadd(DEAD_LETTER_STREAM, dlq_payload)

            # Ack from main stream so it does not block the pipeline
            await r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
        else:
            # Re-enqueue with incremented retry count
            updated = dict(message_data)
            updated[b"retry_count"] = str(current_retries).encode("utf-8")
            await r.xadd(STREAM_NAME, updated)
            await r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)

    async def claim_stale_pending_messages(self) -> int:
        """
        Recovers messages that were delivered to a consumer that crashed or stalled.
        Uses XAUTOCLAIM / XPENDING.
        """
        r = await self.get_redis()
        try:
            # XAUTOCLAIM stream group consumer min_idle_time start_id [COUNT count]
            claim_result = await r.xautoclaim(
                name=STREAM_NAME,
                groupname=CONSUMER_GROUP,
                consumername=self.consumer_id,
                min_idle_time=IDLE_RECLAIM_TIME_MS,
                start_id="0-0",
                count=10
            )
            # Returns (next_start_id, messages, [deleted_ids])
            if claim_result and len(claim_result) >= 2:
                claimed_messages = claim_result[1]
                logger.info(f"Reclaimed {len(claimed_messages)} stale messages for consumer {self.consumer_id}")
                for msg_id, msg_data in claimed_messages:
                    await self.process_single_message(msg_id.decode("utf-8") if isinstance(msg_id, bytes) else str(msg_id), msg_data)
                return len(claimed_messages)
        except Exception as e:
            logger.error(f"Error executing xautoclaim: {e}")
        return 0

    async def run_worker_loop(self, poll_interval_ms: int = 1000, max_iterations: Optional[int] = None):
        """
        Continuous worker loop for consuming new audio segments.
        """
        r = await self.get_redis()
        await self.init_consumer_group()
        self._running = True
        iterations = 0

        logger.info(f"AudioStreamConsumer {self.consumer_id} started listening on {STREAM_NAME}...")

        while self._running:
            try:
                # 1. Periodic stale message reclaim
                if iterations % 30 == 0:
                    await self.claim_stale_pending_messages()

                # 2. Read new messages
                events = await r.xreadgroup(
                    groupname=CONSUMER_GROUP,
                    consumername=self.consumer_id,
                    streams={STREAM_NAME: ">"},
                    count=10,
                    block=poll_interval_ms
                )

                if events:
                    for stream_name, messages in events:
                        for msg_id, msg_data in messages:
                            mid_str = msg_id.decode("utf-8") if isinstance(msg_id, bytes) else str(msg_id)
                            if self.db_session_factory:
                                async with self.db_session_factory() as session:
                                    await self.process_single_message(mid_str, msg_data, db_session=session)
                            else:
                                await self.process_single_message(mid_str, msg_data)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                await asyncio.sleep(1)

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break

    def stop(self):
        self._running = False
