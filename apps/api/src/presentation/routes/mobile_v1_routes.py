"""Mobile-friendly, versioned API surface (v1)."""
from __future__ import annotations

import json
from typing import Dict, Tuple

import httpx
from fastapi import APIRouter, Request, Response

from src.infrastructure.config import get_settings
from src.infrastructure.http_client import get_async_client
from src.presentation.responses import enrich_json_payload, normalized_error

router = APIRouter()
settings = get_settings()
AUTH_SERVICE_URL = settings.auth_service_url
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _pagination_params(request: Request) -> Tuple[int, int]:
    page = max(1, int(request.query_params.get("page", 1)))
    requested_size = int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE))
    page_size = min(MAX_PAGE_SIZE, max(1, requested_size))
    return page, page_size


def _copy_headers(request: Request) -> Dict[str, str]:
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("connection", None)
    headers.pop("content-length", None)
    headers.pop("x-forwarded-proto", None)
    headers.pop("x-forwarded-for", None)
    headers.pop("x-forwarded-host", None)
    return headers


async def _proxy_request(
    *,
    request: Request,
    method: str,
    target_path: str,
    apply_pagination: bool = False,
) -> Response:
    target_url = f"{AUTH_SERVICE_URL}/api/{target_path.lstrip('/') }"
    headers = _copy_headers(request)
    query_params = dict(request.query_params)
    pagination_meta = None

    if apply_pagination:
        page, page_size = _pagination_params(request)
        query_params.update({
            "limit": page_size,
            "skip": (page - 1) * page_size,
        })
        pagination_meta = {"page": page, "page_size": page_size}

    body = await request.body()

    try:
        async with get_async_client() as client:
            upstream_response = await client.request(
                method=method,
                url=target_url,
                params=query_params,
                headers=headers,
                content=body,
            )
    except httpx.TimeoutException:
        return normalized_error(
            code="UPSTREAM_TIMEOUT",
            message="Le service d'authentification a expiré avant de répondre.",
            status_code=504,
        )
    except httpx.RequestError as exc:
        return normalized_error(
            code="UPSTREAM_UNAVAILABLE",
            message=f"Service d'authentification indisponible: {exc}",
            status_code=503,
        )

    content_type = upstream_response.headers.get("content-type", "")
    filtered_headers = {k: v for k, v in upstream_response.headers.items() if k.lower() not in {"content-length", "transfer-encoding"}}

    if "application/json" in content_type:
        data = upstream_response.json()
        meta_kwargs = {"pagination": pagination_meta} if pagination_meta else {}
        data = enrich_json_payload(data, **meta_kwargs)
        return Response(
            content=json.dumps(data).encode("utf-8"),
            status_code=upstream_response.status_code,
            media_type="application/json",
            headers=filtered_headers,
        )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        media_type=content_type or "application/octet-stream",
        headers=filtered_headers,
    )


@router.post("/auth/login", summary="Connexion mobile v1")
async def mobile_login(request: Request):
    return await _proxy_request(request=request, method="POST", target_path="auth/login")


@router.post("/auth/refresh", summary="Rafraîchir le token")
async def mobile_refresh(request: Request):
    return await _proxy_request(request=request, method="POST", target_path="auth/refresh")


@router.get("/profiles/me", summary="Profil utilisateur v1")
async def mobile_profile(request: Request):
    return await _proxy_request(request=request, method="GET", target_path="profiles/me")


@router.get("/entreprises", summary="Liste des entreprises (v1)")
async def mobile_entreprises(request: Request):
    return await _proxy_request(
        request=request,
        method="GET",
        target_path="entreprises",
        apply_pagination=True,
    )


@router.get("/besoins", summary="Liste des besoins (v1)")
async def mobile_besoins(request: Request):
    return await _proxy_request(
        request=request,
        method="GET",
        target_path="besoins",
        apply_pagination=True,
    )
