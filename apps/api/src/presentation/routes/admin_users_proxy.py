"""
"""
Admin Users Proxy Routes
Proxies /api/admin/users/* requests to auth-microservice /api/admin/users/*
"""
from fastapi import APIRouter, Request, Response
import httpx

from src.infrastructure.config import get_settings
from src.infrastructure.http_client import get_async_client

router = APIRouter()

# Auth microservice URL (internal communication)
AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_admin_users_requests(path: str, request: Request):
    """
    Proxy all /api/admin/users/* requests to auth-microservice /api/admin/users/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/admin/users/{path}"
    return await _proxy_request(target_url, request)


async def _proxy_request(target_url: str, request: Request):
    """
    Common proxy logic for all admin users endpoints
    """
    # Get query params
    query_params = dict(request.query_params)
    
    # Get headers (exclude host and connection headers)
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ["host", "connection", "content-length", "x-forwarded-proto", "x-forwarded-for", "x-forwarded-host"]
    }
    
    # Get request body
    body = await request.body()
    
    try:
        async with get_async_client() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                params=query_params,
                headers=headers,
                content=body,
            )

            # Return response with same status code and content
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
    except httpx.RequestError as e:
        return Response(
            content=f'{{"detail": "Auth service unavailable: {str(e)}"}}',
            status_code=503,
            media_type="application/json",
        )
