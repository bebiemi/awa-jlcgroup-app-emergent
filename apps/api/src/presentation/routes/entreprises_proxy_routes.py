"""Entreprises Proxy Routes."""
from fastapi import APIRouter, Request

from src.infrastructure.config import get_settings
from src.presentation.routes.proxy_helpers import proxy_request

router = APIRouter()

AUTH_SERVICE_URL = get_settings().auth_service_url


async def proxy_entreprises_requests(path: str, request: Request):
    """Proxy entreprises requests to auth-microservice"""
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/entreprises/{path}" if path else "/api/entreprises",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_namespace="entreprises",
        cache_enabled_for_get=True,
    )


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def proxy_entreprises(path: str, request: Request):
    """Proxy all /api/entreprises/* requests"""
    return await proxy_entreprises_requests(path, request)


@router.get("", include_in_schema=False)
@router.post("", include_in_schema=False)
@router.patch("", include_in_schema=False)
async def proxy_entreprises_root(request: Request):
    """Proxy root /api/entreprises requests"""
    return await proxy_entreprises_requests("", request)
