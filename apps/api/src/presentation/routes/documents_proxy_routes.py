"""Documents & Support Proxy Routes with normalized behaviors."""
from __future__ import annotations

from fastapi import APIRouter, Request

from src.infrastructure.config import get_settings
from src.presentation.routes.proxy_helpers import proxy_request

router = APIRouter()

# Auth microservice URL (internal communication)
AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/entreprises/form-config/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_entreprise_form_config_requests(path: str, request: Request):
    """Proxy all /api/entreprises/form-config/* requests to auth-microservice"""
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/entreprises/form-config/{path}",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_namespace="entreprises-form-config",
        cache_enabled_for_get=True,
        follow_redirects=True,
    )


@router.api_route("/documents/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_documents_requests(path: str, request: Request):
    """Proxy all /api/documents/* requests to auth-microservice"""
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/documents/{path}",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_namespace="documents",
        cache_enabled_for_get=False,
        follow_redirects=True,
    )


@router.api_route("/invitations/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_invitations_requests(path: str, request: Request):
    """Proxy all /api/invitations/* requests to auth-microservice"""
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/invitations/{path}",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_namespace="invitations",
        cache_enabled_for_get=False,
        follow_redirects=True,
    )


@router.api_route("/support/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_support_requests(path: str, request: Request):
    """Proxy all /api/support/* requests to auth-microservice"""
    return await proxy_request(
        request=request,
        target_base_url=AUTH_SERVICE_URL,
        target_path=f"/api/support/{path}",
        cache=request.app.state.response_cache if hasattr(request.app.state, "response_cache") else None,
        cache_namespace="support",
        cache_enabled_for_get=True,
        follow_redirects=True,
    )
