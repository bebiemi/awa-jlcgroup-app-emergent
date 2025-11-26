"""
Config Proxy Routes
Forwards /api/config/* requests to auth-microservice
"""
import logging

from fastapi import APIRouter, HTTPException, Request, Response
import httpx

from src.infrastructure.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

AUTH_SERVICE_URL = get_settings().auth_service_url


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
        async with httpx.AsyncClient(follow_redirects=True) as client:
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


@router.api_route("/countries", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_countries_base(request: Request):
    """Proxy /api/config/countries requests to auth-microservice"""
    return await proxy_config_request("countries", request)


@router.api_route("/countries/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_countries_with_path(path: str, request: Request):
    """Proxy all /api/config/countries/* requests to auth-microservice"""
    return await proxy_config_request(f"countries/{path}", request)


@router.api_route("/forms", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_forms_base(request: Request):
    """Proxy /api/config/forms requests to auth-microservice"""
    return await proxy_config_request("forms", request)


@router.api_route("/forms/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_forms_with_path(path: str, request: Request):
    """Proxy all /api/config/forms/* requests to auth-microservice"""
    return await proxy_config_request(f"forms/{path}", request)


@router.api_route("/workflows", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_workflows_base(request: Request):
    """Proxy /api/config/workflows requests to auth-microservice"""
    return await proxy_config_request("workflows", request)


@router.api_route("/workflows/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_workflows_with_path(path: str, request: Request):
    """Proxy all /api/config/workflows/* requests to auth-microservice"""
    return await proxy_config_request(f"workflows/{path}", request)


@router.api_route("/references", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_references_base(request: Request):
    """Proxy /api/config/references requests to auth-microservice"""
    return await proxy_config_request("references", request)


@router.api_route("/references/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_config_references_with_path(path: str, request: Request):
    """Proxy all /api/config/references/* requests to auth-microservice"""
    return await proxy_config_request(f"references/{path}", request)

# Config global (all)
@router.api_route("/all", methods=["GET"])
async def proxy_config_all(request: Request):
    """Proxy /api/config/all requests to auth-microservice"""
    return await proxy_config_request("all", request)

# Config public minimal
@router.api_route("/public", methods=["GET"])
async def proxy_config_public(request: Request):
    """Proxy /api/config/public requests to auth-microservice"""
    return await proxy_config_request("public", request)


# App Configuration routes
@router.api_route("/app", methods=["GET", "POST"])
async def proxy_config_app_base(request: Request):
    """Proxy /api/config/app requests to auth-microservice"""
    return await proxy_config_request("app", request)


@router.api_route("/app/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def proxy_config_app_with_path(path: str, request: Request):
    """Proxy all /api/config/app/* requests to auth-microservice"""
    return await proxy_config_request(f"app/{path}", request)
