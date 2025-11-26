"""Lightweight response cache with optional Redis backend.

This cache is intentionally minimal and focuses on storing serialized
JSON responses for GET requests. It supports both Redis (when available)
and an in-memory fallback to keep the API resilient in offline modes.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, Optional, Tuple

try:
    from redis.asyncio import Redis
    import redis
except ImportError:  # pragma: no cover - redis is optional
    Redis = None  # type: ignore
    redis = None  # type: ignore


CacheEntry = Tuple[str, float]


class ResponseCache:
    """A tiny TTL cache to keep frequently accessed payloads warm."""

    def __init__(
        self,
        *,
        ttl_seconds: int,
        redis_url: Optional[str] = None,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.redis_url = redis_url
        self._redis_client: Optional[Redis] = None
        self._lock = asyncio.Lock()
        self._local_cache: Dict[str, CacheEntry] = {}

    async def initialize(self) -> None:
        if self.redis_url and redis is not None:
            self._redis_client = redis.asyncio.from_url(self.redis_url)

    async def shutdown(self) -> None:
        if self._redis_client is not None:
            await self._redis_client.aclose()
            self._redis_client = None
        async with self._lock:
            self._local_cache.clear()

    async def get(self, key: str) -> Optional[str]:
        """Return the cached payload when not expired."""

        if self._redis_client is not None:
            cached = await self._redis_client.get(key)
            return cached.decode("utf-8") if cached else None

        async with self._lock:
            entry = self._local_cache.get(key)
            if not entry:
                return None
            payload, expires_at = entry
            if expires_at < time.time():
                self._local_cache.pop(key, None)
                return None
            return payload

    async def set(self, key: str, payload: str, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds or self.ttl_seconds
        expires_at = time.time() + ttl

        if self._redis_client is not None:
            await self._redis_client.setex(key, ttl, payload)
            return

        async with self._lock:
            self._local_cache[key] = (payload, expires_at)

    @staticmethod
    def build_cache_key(namespace: str, url: str, params: Dict[str, str], auth_fingerprint: str | None) -> str:
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        auth_suffix = auth_fingerprint or "anon"
        return f"{namespace}:{url}:{sorted_params}:{auth_suffix}"

    @staticmethod
    def serialize_response(
        *,
        content: str,
        status_code: int,
        media_type: str,
        headers: Dict[str, str],
    ) -> str:
        return json.dumps(
            {
                "content": content,
                "status_code": status_code,
                "media_type": media_type,
                "headers": headers,
            }
        )

    @staticmethod
    def deserialize_response(payload: str) -> Tuple[str, int, str, Dict[str, str]]:
        data = json.loads(payload)
        return data["content"], data["status_code"], data["media_type"], data["headers"]
