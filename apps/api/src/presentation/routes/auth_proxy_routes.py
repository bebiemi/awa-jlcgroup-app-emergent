"""Auth Proxy Routes forwarding to auth-microservice."""
from fastapi import APIRouter, Request

from src.infrastructure.config import get_settings
from src.presentation.routes.proxy_helpers import proxy_request

router = APIRouter()

AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def proxy_auth_requests(path: str, request: Request):
    """Proxy all /api/auth/* requests to auth-microservice"""
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/auth/{path}" if path else "/api/auth",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_enabled_for_get=False,
    )


@router.get("", include_in_schema=False)
@router.post("", include_in_schema=False)
async def proxy_auth_root(request: Request):
    """Proxy root /api/auth requests"""
    return await proxy_auth_requests("", request)
