"""
IAM Proxy Routes
Forwards /api/iam/* requests to auth-microservice
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
import httpx
import logging

from src.infrastructure.config import get_settings
from src.infrastructure.http_client import get_async_client

logger = logging.getLogger(__name__)

router = APIRouter()

AUTH_SERVICE_URL = get_settings().auth_service_url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_iam_requests(path: str, request: Request):
    """
    Proxy all /api/iam/* requests to auth-microservice
    """
    # Build target URL
    target_url = f"{AUTH_SERVICE_URL}/api/iam/{path}"
    
    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Forward headers (especially Authorization)
    headers = dict(request.headers)
    # Remove host header to avoid conflicts
    headers.pop('host', None)
    
    try:
        async with get_async_client() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )
            
            # Return the response from auth-microservice
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get('content-type')
            )
    
    except httpx.TimeoutException:
        logger.error(f"Timeout while proxying to auth-microservice: {target_url}")
        raise HTTPException(status_code=504, detail="Auth service timeout")
    except Exception as e:
        logger.error(f"Error proxying to auth-microservice: {str(e)}")
        raise HTTPException(status_code=502, detail="Auth service unavailable")
