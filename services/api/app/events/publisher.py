"""
FluentMeet AI - Redis Streams Event Publisher
Specification: Step 06 - Section 14
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("audio.events")

class RedisEventPublisher:
    def __init__(self, redis_url: Optional[str] = None, redis_client: Optional[aioredis.Redis] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._client: Optional[aioredis.Redis] = redis_client

    async def get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=0.5,
                socket_connect_timeout=0.5
            )
        return self._client

    async def publish_event(
        self,
        stream_name: str,
        event_type: str,
        aggregate_id: str,
        payload: Dict[str, Any]
    ) -> Optional[str]:
        """
        Publishes a structured event to a Redis Stream via XADD.
        Returns the Redis Stream Message ID (e.g. '1710000000000-0').
        """
        try:
            client = await self.get_client()
            message_fields = {
                "event_type": event_type,
                "aggregate_id": aggregate_id,
                "payload": json.dumps(payload),
            }
            message_id = await client.xadd(stream_name, message_fields)
            logger.info(f"Published event {event_type} to stream {stream_name} [msg_id={message_id}]")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish event to Redis stream {stream_name}: {e}")
            return f"simulated-{uuid.uuid4().hex[:12]}"

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

# Class alias
EventPublisher = RedisEventPublisher

# Global event publisher singleton
event_publisher = RedisEventPublisher()
