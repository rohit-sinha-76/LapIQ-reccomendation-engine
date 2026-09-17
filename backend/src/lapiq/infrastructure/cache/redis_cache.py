"""Redis async cache client wrapper implementing invalidation strategies."""

import json
import logging
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import RedisError

from lapiq.core.config import settings

logger = logging.getLogger(__name__)


class RedisCacheManager:
    """
    Async Redis cache wrapper for session, retrieval, price, and request caches.

    Cache Key Strategies:
    - session:{id}     - Preference state (TTL: 86400s / 24h)
    - retrieval:{hash} - Candidate retrieval results (Invalidation: worker price event)
    - price:{id}       - Latest price snapshot (Invalidation: worker price event)
    - request:{id}     - SSE streaming explanation state (TTL: 3600s / 1h)

    NOTE: Recommendation engine output is NEVER cached in Redis.
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or settings.redis_url
        self._client: aioredis.Redis | None = None

    async def get_client(self) -> aioredis.Redis:
        """Get or initialize async Redis client connection."""
        if self._client is None:
            self._client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set JSON payload in Redis with optional TTL and graceful failure."""
        try:
            client = await self.get_client()
            serialized = json.dumps(value)
            if ttl_seconds:
                await client.setex(key, ttl_seconds, serialized)
            else:
                await client.set(key, serialized)
        except (RedisError, OSError) as exc:
            logger.warning("Redis cache write failed for key '%s': %s", key, exc)

    async def get_json(self, key: str) -> Any | None:
        """Retrieve and parse JSON payload from Redis with graceful failure."""
        try:
            client = await self.get_client()
            data = await client.get(key)
            if data is None:
                return None
            return json.loads(data)
        except (RedisError, OSError) as exc:
            logger.warning("Redis cache read failed for key '%s': %s", key, exc)
            return None

    async def invalidate(self, pattern: str) -> int:
        """Invalidate keys matching pattern (used by worker price update events)."""
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except (RedisError, OSError) as exc:
            logger.warning("Redis cache invalidation failed for pattern '%s': %s", pattern, exc)
            return 0

    async def close(self) -> None:
        """Close Redis client connection."""
        if self._client:
            try:
                await self._client.close()
            except (RedisError, OSError):
                pass
            self._client = None
