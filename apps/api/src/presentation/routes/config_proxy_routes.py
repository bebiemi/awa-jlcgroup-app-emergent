"""
Config Proxy Routes
Forwards /api/config/* requests to auth-microservice
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8000')


async def proxy_config_request(endpoint_path: str, request: Request):
    """
    Generic proxy function for config requests
    """
    # Build target URL
    target_url = f"{AUTH_SERVICE_URL}/api/config/{endpoint_path}"
    
    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Forward headers (especially Authorization)
    headers = dict(request.headers)
    headers.pop('host', None)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
                timeout=30.0
            )
            
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


@router.api_route("/countries/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_countries(path: str, request: Request):
    """Proxy all /api/config/countries/* requests to auth-microservice"""
    return await proxy_config_request(f"countries/{path}", request)


@router.api_route("/forms/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_forms(path: str, request: Request):
    """Proxy all /api/config/forms/* requests to auth-microservice"""
    return await proxy_config_request(f"forms/{path}", request)


@router.api_route("/workflows/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_workflows(path: str, request: Request):
    """Proxy all /api/config/workflows/* requests to auth-microservice"""
    return await proxy_config_request(f"workflows/{path}", request)


@router.api_route("/references/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_references(path: str, request: Request):
    """Proxy all /api/config/references/* requests to auth-microservice"""
    return await proxy_config_request(f"references/{path}", request)
