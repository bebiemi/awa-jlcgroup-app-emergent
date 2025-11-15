"""
Auth Endpoints Proxy Routes
Proxies /api/auth/*, /api/users/*, /api/profiles/* requests to auth-microservice
This ensures all auth endpoints are accessible via /api prefix (required for ingress)
"""
from fastapi import APIRouter, Request, Response
import httpx
import os

router = APIRouter()

# Auth microservice URL (internal communication)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")


@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth_requests(path: str, request: Request):
    """
    Proxy all /api/auth/* requests to auth-microservice /api/auth/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/auth/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_users_requests(path: str, request: Request):
    """
    Proxy all /api/users/* requests to auth-microservice /api/users/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/users/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/profiles/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_profiles_requests(path: str, request: Request):
    """
    Proxy all /api/profiles/* requests to auth-microservice /api/profiles/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/profiles/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/locations/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_locations_requests(path: str, request: Request):
    """
    Proxy all /api/locations/* requests to auth-microservice /api/locations/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/locations/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/email-settings/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_email_settings_requests(path: str, request: Request):
    """
    Proxy all /api/email-settings/* requests to auth-microservice /api/email-settings/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/email-settings/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/email-templates/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_email_templates_requests(path: str, request: Request):
    """
    Proxy all /api/email-templates/* requests to auth-microservice /api/email-templates/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/email-templates/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/email-history/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_email_history_requests(path: str, request: Request):
    """
    Proxy all /api/email-history/* requests to auth-microservice /api/email-history/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/email-history/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/contracts/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_contracts_requests(path: str, request: Request):
    """
    Proxy all /api/contracts/* requests to auth-microservice /api/contracts/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/contracts/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/applications/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_applications_requests(path: str, request: Request):
    """
    Proxy all /api/applications/* requests to auth-microservice /api/applications/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/applications/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/feature-flags", methods=["GET", "POST"])
@router.api_route("/feature-flags/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_feature_flags_requests(path: str = "", request: Request = None):
    """
    Proxy all /api/feature-flags/* requests to auth-microservice /api/feature-flags/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/feature-flags/{path}" if path else f"{AUTH_SERVICE_URL}/api/feature-flags"
    return await _proxy_request(target_url, request)


@router.api_route("/versions/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_versions_requests(path: str, request: Request):
    """
    Proxy all /api/versions/* requests to auth-microservice /api/versions/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/versions/{path}"
    return await _proxy_request(target_url, request)


@router.api_route("/validations", methods=["GET", "POST"])
@router.api_route("/validations/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_validations_requests(path: str = "", request: Request = None):
    """
    Proxy all /api/validations/* requests to auth-microservice /api/validations/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/validations/{path}" if path else f"{AUTH_SERVICE_URL}/api/validations"
    return await _proxy_request(target_url, request)


@router.api_route("/missions", methods=["GET", "POST"])
@router.api_route("/missions/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_missions_requests(path: str = "", request: Request = None):
    """
    Proxy all /api/missions/* requests to auth-microservice /api/missions/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/missions/{path}" if path else f"{AUTH_SERVICE_URL}/api/missions"
    return await _proxy_request(target_url, request)


@router.api_route("/emails/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_emails_requests(path: str, request: Request):
    """
    Proxy all /api/emails/* requests to auth-microservice /api/emails/*
    """
    target_url = f"{AUTH_SERVICE_URL}/api/emails/{path}"
    return await _proxy_request(target_url, request)


async def _proxy_request(target_url: str, request: Request):
    """
    Common proxy logic for all auth endpoints
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
