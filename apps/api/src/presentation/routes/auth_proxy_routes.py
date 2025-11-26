"""
Auth Proxy Routes
Proxies /api/auth/* requests to auth-microservice
"""
from fastapi import APIRouter, Request, Response
import httpx

from src.infrastructure.config import get_settings
from src.infrastructure.http_client import get_async_client

router = APIRouter()

AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def proxy_auth_requests(path: str, request: Request):
    """Proxy all /api/auth/* requests to auth-microservice"""
    target_url = f"{AUTH_SERVICE_URL}/api/auth/{path}" if path else f"{AUTH_SERVICE_URL}/api/auth"
    
    query_params = dict(request.query_params)
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ["host", "connection", "content-length", "x-forwarded-proto", "x-forwarded-for", "x-forwarded-host"]
    }
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


@router.get("", include_in_schema=False)
@router.post("", include_in_schema=False)
async def proxy_auth_root(request: Request):
    """Proxy root /api/auth requests"""
    return await proxy_auth_requests("", request)
