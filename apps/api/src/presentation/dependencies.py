"""Dependency injection for routes"""
from fastapi import Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
import httpx
import os
import logging


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000").rstrip("/")
AUTH_ME_ENDPOINT = "/api/auth/me"
AUTH_TIMEOUT = httpx.Timeout(5.0)

logger = logging.getLogger(__name__)


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    """Get database instance"""
    return request.app.state.db


async def get_current_user(request: Request, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get current authenticated user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.replace("Bearer ", "")

    # Verify token with auth-microservice
    try:
        async with httpx.AsyncClient(base_url=AUTH_SERVICE_URL, timeout=AUTH_TIMEOUT) as client:
            response = await client.get(
                AUTH_ME_ENDPOINT,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                logger.warning(
                    "Auth service responded with status %s for /me", response.status_code
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )

            user_data = response.json()
            return user_data

    except httpx.RequestError as e:
        logger.error(f"Failed to verify token with auth service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


async def require_role(required_roles: list[str]):
    """Dependency to require specific roles"""
    async def role_checker(current_user = Depends(get_current_user)):
        user_roles = current_user.get('roles', [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker


async def require_admin(current_user = Depends(get_current_user)):
    """Require admin role"""
    user_roles = current_user.get('roles', [])
    if 'admin' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user
