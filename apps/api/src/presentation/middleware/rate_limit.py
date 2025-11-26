"""Rate limiting middleware using the shared RateLimiter."""
from __future__ import annotations

import time

from fastapi import Request
from fastapi.responses import Response

from src.infrastructure.rate_limiter import RateLimiter
from src.presentation.responses import normalized_error


async def rate_limit_middleware(request: Request, call_next):
    limiter: RateLimiter = request.app.state.rate_limiter  # type: ignore[attr-defined]

    client_id = request.headers.get("x-client-id") or request.client.host or "anonymous"
    allowed, retry_after = await limiter.allow_request(client_id)

    if not allowed:
        return normalized_error(
            code="RATE_LIMIT_EXCEEDED",
            message="Trop de requêtes, merci de réessayer ultérieurement.",
            status_code=429,
            retry_after=retry_after,
        )

    response: Response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limiter.limit)
    response.headers["X-RateLimit-Window"] = str(limiter.window_seconds)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + retry_after))
    return response
