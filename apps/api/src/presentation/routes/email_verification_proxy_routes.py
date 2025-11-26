"""Email Verification Proxy Routes."""
from fastapi import APIRouter, Request

from src.infrastructure.config import get_settings
from src.presentation.routes.proxy_helpers import proxy_request

router = APIRouter()

# Auth microservice URL (internal communication)
AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_email_verification_requests(path: str, request: Request):
    """
    Proxy all /email-verification/* requests to auth-microservice
    Preserves headers, body, query params, and method
    """
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/email-verification/{path}" if path else "/api/email-verification",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_namespace="email-verification",
        cache_enabled_for_get=True,
        follow_redirects=True,
    )
