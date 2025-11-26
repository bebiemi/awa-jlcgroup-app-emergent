"""Shared HTTP client helpers for outbound calls."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import httpx

from src.infrastructure.config import get_settings


settings = get_settings()


@asynccontextmanager
async def get_async_client(
    *,
    timeout_seconds: Optional[float] = None,
    connect_timeout_seconds: Optional[float] = None,
    follow_redirects: bool = True,
) -> AsyncIterator[httpx.AsyncClient]:
    """Provide a configured AsyncClient with consistent timeouts.

    Timeouts are aligned across all proxies to avoid uneven resilience behaviors.
    """

    timeout = httpx.Timeout(
        timeout_seconds or settings.api_client_timeout_seconds,
        connect=connect_timeout_seconds or settings.api_client_connect_timeout_seconds,
    )
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=follow_redirects) as client:
        yield client
