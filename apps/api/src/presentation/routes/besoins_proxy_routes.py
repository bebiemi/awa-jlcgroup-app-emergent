"""
Besoins Proxy Routes
Proxies /api/besoins/* requests to auth-microservice
"""
from fastapi import APIRouter, Request, Response
import httpx

from src.infrastructure.config import get_settings
from src.infrastructure.http_client import get_async_client

router = APIRouter()

AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def proxy_besoins_requests(path: str, request: Request):
    """Proxy all /api/besoins/* requests to auth-microservice"""
    target_url = f"{AUTH_SERVICE_URL}/api/besoins/{path}" if path else f"{AUTH_SERVICE_URL}/api/besoins"
    
    query_params = dict(request.query_params)
    # Preserve ALL headers including Authorization
    headers = dict(request.headers)
    # Remove problematic headers
    headers.pop("host", None)
    headers.pop("connection", None)
    headers.pop("content-length", None)
    # Remove X-Forwarded headers to prevent SSL issues in internal communication
    headers.pop("x-forwarded-proto", None)
    headers.pop("x-forwarded-for", None)
    headers.pop("x-forwarded-host", None)
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
async def proxy_besoins_root(request: Request):
    """Proxy root /api/besoins requests"""
    return await proxy_besoins_requests("", request)
