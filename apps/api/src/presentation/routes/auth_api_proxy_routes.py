"""
Auth API Proxy Routes
Proxies /auth-api/* requests to auth-microservice /api/*
This ensures production compatibility where only backend (port 8001) is exposed
"""
from fastapi import APIRouter, Request, Response
import httpx

from src.infrastructure.config import get_settings

router = APIRouter()

# Auth microservice URL (internal communication)
AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth_api_requests(path: str, request: Request):
    """
    Proxy all /auth-api/* requests to auth-microservice /api/*
    Rewrites path from /auth-api/xxx to /api/xxx
    Preserves headers, body, query params, and method
    """
    # Rewrite path: /auth-api/auth/local/login -> /api/auth/local/login
    target_path = f"/api/{path}"
    target_url = f"{AUTH_SERVICE_URL}{target_path}"
    
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
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
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
