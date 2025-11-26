"""Dependency injection for routes"""
from fastapi import Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable
import yaml


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000").rstrip("/")
AUTH_ME_ENDPOINT = "/api/auth/me"
AUTH_TIMEOUT = httpx.Timeout(5.0)

logger = logging.getLogger(__name__)

DEFAULT_VALIDATOR_ROLES = ["admin", "super_admin", "commercial"]


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    """Get database instance"""
    return request.app.state.db


def _read_config_file(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        logger.warning("Validation config file not found at %s", config_path)
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:  # pragma: no cover - defensive fallback
        logger.exception("Failed to read validation configuration")
        return {}


def _get_nested(config: dict[str, Any], keys: Iterable[str]) -> list[str] | None:
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    if isinstance(current, list):
        return current
    return None


@lru_cache()
def get_validator_roles_from_config() -> list[str]:
    """Read validator roles from configuration (workflows.validation.permissions.validator_roles)."""
    config_path = Path(os.getenv("AUTH_CONFIG_PATH", "/app/auth-microservice/config/base.yaml"))
    config = _read_config_file(config_path)
    roles = _get_nested(config, ["workflows", "validation", "permissions", "validator_roles"])
    if roles:
        return roles

    logger.warning(
        "Using default validator roles because config is missing the path workflows.validation.permissions.validator_roles"
    )
    return DEFAULT_VALIDATOR_ROLES


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
                response_body = response.text
                if len(response_body) > 500:
                    response_body = response_body[:500] + "...(truncated)"
                logger.warning(
                    "Auth service responded with status %s for /me: %s",
                    response.status_code,
                    response_body,
                )
                if 500 <= response.status_code < 600:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Authentication service unavailable (upstream error)",
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )

            user_data = response.json()
            return user_data

    except httpx.RequestError as e:
        logger.error(f"Failed to verify token with auth service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
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
            detail="Admin role required",
        )
    return current_user


async def require_validator(current_user = Depends(get_current_user)):
    """Require validator roles from configuration."""
    validator_roles = get_validator_roles_from_config()
    user_roles = current_user.get("roles", [])
    if not any(role in user_roles for role in validator_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Validator role required",
        )
    return current_user
