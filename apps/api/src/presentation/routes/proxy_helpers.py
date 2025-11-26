"""Shared helpers to normalize proxy routes and responses."""
from __future__ import annotations

import json
import hashlib
from typing import Dict, Optional

import httpx
from fastapi import Request, Response

from src.infrastructure.cache import ResponseCache
from src.infrastructure.http_client import get_async_client
from src.presentation.responses import enrich_json_payload, normalized_error

STRIP_HEADERS = {
    "host",
    "connection",
    "content-length",
    "x-forwarded-proto",
    "x-forwarded-for",
    "x-forwarded-host",
    "transfer-encoding",
}


def sanitize_headers(request: Request) -> Dict[str, str]:
    return {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in STRIP_HEADERS
    }


def _auth_fingerprint(headers: Dict[str, str]) -> Optional[str]:
    token = headers.get("authorization") or headers.get("Authorization")
    if not token:
        return None
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def proxy_request(
    *,
    request: Request,
    target_base_url: str,
    target_path: str,
    cache: Optional[ResponseCache] = None,
    cache_namespace: str = "proxy",
    cache_enabled_for_get: bool = False,
    follow_redirects: bool = True,
) -> Response:
    """Forward a request to an upstream service with consistent behaviors."""

    target_url = f"{target_base_url.rstrip('/')}/{target_path.lstrip('/') }"
    query_params = dict(request.query_params)
    headers = sanitize_headers(request)
    body = await request.body()

    cache_key: Optional[str] = None
    if cache and cache_enabled_for_get and request.method.upper() == "GET":
        cache_key = ResponseCache.build_cache_key(
            cache_namespace,
            target_url,
            query_params,
            _auth_fingerprint(headers),
        )
        cached_payload = await cache.get(cache_key)
        if cached_payload:
            content, status_code, media_type, cached_headers = ResponseCache.deserialize_response(
                cached_payload
            )
            return Response(
                content=content.encode("utf-8"),
                status_code=status_code,
                media_type=media_type,
                headers=cached_headers,
            )

    try:
        async with get_async_client(follow_redirects=follow_redirects) as client:
            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                params=query_params,
                headers=headers,
                content=body,
            )
    except httpx.TimeoutException:
        return normalized_error(
            code="UPSTREAM_TIMEOUT",
            message="Le service amont a expiré avant de répondre.",
            status_code=504,
        )
    except httpx.RequestError as exc:
        return normalized_error(
            code="UPSTREAM_UNAVAILABLE",
            message=f"Service amont indisponible: {exc}",
            status_code=503,
        )

    content_type = upstream_response.headers.get("content-type", "")
    filtered_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in STRIP_HEADERS
    }

    if "application/json" in content_type:
        payload = enrich_json_payload(upstream_response.json())
        content = json.dumps(payload)
        if cache and cache_key:
            await cache.set(
                cache_key,
                ResponseCache.serialize_response(
                    content=content,
                    status_code=upstream_response.status_code,
                    media_type=content_type or "application/json",
                    headers=filtered_headers,
                ),
            )
        return Response(
            content=content.encode("utf-8"),
            status_code=upstream_response.status_code,
            media_type=content_type or "application/json",
            headers=filtered_headers,
        )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        media_type=content_type or "application/octet-stream",
        headers=filtered_headers,
    )
