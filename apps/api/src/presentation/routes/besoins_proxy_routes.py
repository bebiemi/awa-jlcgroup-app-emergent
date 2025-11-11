"""
Besoins Proxy Routes
Proxies /api/besoins/* requests to auth-microservice
"""
from fastapi import APIRouter, Request, Response
import httpx
import os

router = APIRouter()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def proxy_besoins_requests(path: str, request: Request):
    """Proxy all /api/besoins/* requests to auth-microservice"""
    target_url = f"{AUTH_SERVICE_URL}/api/besoins/{path}" if path else f"{AUTH_SERVICE_URL}/api/besoins"
    
    query_params = dict(request.query_params)
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ["host", "connection", "content-length"]
    }
    body = await request.body()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
