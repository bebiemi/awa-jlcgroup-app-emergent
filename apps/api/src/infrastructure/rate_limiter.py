"""Lightweight rate limiting with optional Redis backend."""
from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Tuple

try:
    from redis.asyncio import Redis
    import redis
except ImportError:  # pragma: no cover - redis is optional
    Redis = None  # type: ignore
    redis = None  # type: ignore


class RateLimiter:
    """Sliding window rate limiter with Redis fallback.

    If Redis is configured, counters are stored centrally. Otherwise, an
    in-memory dictionary keeps per-bucket counters for the process.
    """

    def __init__(
        self,
        *,
        limit: int,
        window_seconds: int,
        redis_url: Optional[str] = None,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.redis_url = redis_url
        self._redis_client: Optional[Redis] = None
        self._lock = asyncio.Lock()
        self._local_counters: Dict[str, Dict[int, int]] = {}

    async def initialize(self) -> None:
        """Initialize the Redis client when a URL is provided."""

        if self.redis_url and redis is not None:
            self._redis_client = redis.asyncio.from_url(self.redis_url)

    async def shutdown(self) -> None:
        if self._redis_client is not None:
            await self._redis_client.aclose()
            self._redis_client = None

    def _bucket(self, now: Optional[float] = None) -> int:
        current_time = now or time.time()
        return int(current_time // self.window_seconds)

    async def allow_request(self, key: str) -> Tuple[bool, int]:
        """Increment the counter and return (allowed, retry_after_seconds)."""

        bucket = self._bucket()
        retry_after = self.window_seconds - int(time.time() % self.window_seconds)

        if self._redis_client is not None:
            return await self._allow_with_redis(key, bucket, retry_after)
        return await self._allow_in_memory(key, bucket, retry_after)

    async def _allow_with_redis(
        self, key: str, bucket: int, retry_after: int
    ) -> Tuple[bool, int]:
        redis_key = f"rl:{key}:{bucket}"
        async with self._redis_client.pipeline() as pipe:  # type: ignore[union-attr]
            pipe.incr(redis_key)
            pipe.expire(redis_key, self.window_seconds)
            count, _ = await pipe.execute()

        allowed = int(count) <= self.limit
        return allowed, 0 if allowed else retry_after

    async def _allow_in_memory(
        self, key: str, bucket: int, retry_after: int
    ) -> Tuple[bool, int]:
        # key is not required for in-memory map because process scoped buckets
        async with self._lock:
            if key not in self._local_counters:
                self._local_counters[key] = {}

            # Clean up outdated buckets to avoid unbounded growth
            for bucket_key in list(self._local_counters[key].keys()):
                if bucket_key < bucket:
                    self._local_counters[key].pop(bucket_key, None)

            count = self._local_counters[key].get(bucket, 0) + 1
            self._local_counters[key][bucket] = count

        allowed = count <= self.limit
        return allowed, 0 if allowed else retry_after
