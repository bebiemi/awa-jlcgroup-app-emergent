"""
Security Proxy Routes
Proxies /api/security/* requests to auth-microservice
This ensures production compatibility where only backend (port 8001) is exposed
"""
from fastapi import APIRouter, Request, Response
import httpx
import os

router = APIRouter()

# Auth microservice URL (internal communication)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")


@router.api_route("/security/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_security_requests(path: str, request: Request):
    """
    Proxy all /api/security/* requests to auth-microservice
    Preserves headers, body, query params, and method
    """
    # Build target URL
    target_url = f"{AUTH_SERVICE_URL}/api/security/{path}"
    
    # Get query params
    query_params = dict(request.query_params)
    
    # Get headers (exclude host and connection headers)
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ["host", "connection", "content-length"]
    }
    
    # Get request body
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
