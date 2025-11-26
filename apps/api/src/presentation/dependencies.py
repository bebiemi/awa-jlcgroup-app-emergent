"""Dependency injection for routes"""
from fastapi import Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable
from src.domain.entities.profile import ProfileType
from src.domain.entities.validation import ValidationStatus, ValidationType
import yaml


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000").rstrip("/")
AUTH_ME_ENDPOINT = "/api/auth/me"
AUTH_TIMEOUT = httpx.Timeout(5.0)

logger = logging.getLogger(__name__)

DEFAULT_SECURITY_ROLES = {
    "admin": "admin",
    "super_admin": "super_admin",
    "company": "company",
    "interim": "interim",
    "agency": "agency",
    "commercial": "commercial",
    "validator": "validator",
}

DEFAULT_VALIDATOR_ROLES = [
    DEFAULT_SECURITY_ROLES["admin"],
    DEFAULT_SECURITY_ROLES["super_admin"],
    DEFAULT_SECURITY_ROLES["commercial"],
]
DEFAULT_VALIDATION_STATUSES = {
    "pending": ValidationStatus.PENDING.value,
    "approved": ValidationStatus.APPROVED.value,
    "rejected": ValidationStatus.REJECTED.value,
}

DEFAULT_VALIDATION_TYPES = {
    "company": ValidationType.COMPANY.value,
    "interim": ValidationType.INTERIM.value,
}

DEFAULT_VALIDATION_TRANSITIONS = {
    "approve": {"from": [DEFAULT_VALIDATION_STATUSES["pending"]], "to": DEFAULT_VALIDATION_STATUSES["approved"]},
    "reject": {"from": [DEFAULT_VALIDATION_STATUSES["pending"]], "to": DEFAULT_VALIDATION_STATUSES["rejected"]},
}
DEFAULT_PROFILE_TYPES = {
    "admin": ProfileType.ADMIN.value,
    "agency": ProfileType.AGENCY.value,
    "company": ProfileType.COMPANY.value,
    "interim": ProfileType.INTERIM.value,
}


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


def _get_nested(config: dict[str, Any], keys: Iterable[str]) -> Any:
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _get_list(config: dict[str, Any], keys: Iterable[str]) -> list[str] | None:
    value = _get_nested(config, keys)
    return value if isinstance(value, list) else None


def _get_dict(config: dict[str, Any], keys: Iterable[str]) -> dict[str, Any] | None:
    value = _get_nested(config, keys)
    return value if isinstance(value, dict) else None


@lru_cache()
def get_security_roles_from_config() -> dict[str, str]:
    """Read security roles from configuration (security.roles)."""
    config_path = Path(
        os.getenv(
            "AUTH_CONFIG_PATH",
            Path(__file__).resolve().parents[4] / "auth-microservice/config/base.yaml",
        )
    )

    config = _read_config_file(config_path)
    roles = _get_dict(config, ["security", "roles"]) or {}
    return {**DEFAULT_SECURITY_ROLES, **{k: v for k, v in roles.items() if isinstance(v, str)}}


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped


@lru_cache()
def get_admin_roles_from_config() -> list[str]:
    """Return admin and super admin roles from configuration (with defaults)."""
    roles = get_security_roles_from_config()
    return _dedupe_preserve_order(
        [
            roles.get("admin", DEFAULT_SECURITY_ROLES["admin"]),
            roles.get("super_admin", DEFAULT_SECURITY_ROLES["super_admin"]),
        ]
    )


@lru_cache()
def get_validator_roles_from_config() -> list[str]:
    """Read validator roles from configuration (workflows.validation.permissions.validator_roles)."""
    config_path = Path(
        os.getenv(
            "AUTH_CONFIG_PATH",
            Path(__file__).resolve().parents[4] / "auth-microservice/config/base.yaml",
        )
    )

    config = _read_config_file(config_path)
    roles = _get_list(config, ["workflows", "validation", "permissions", "validator_roles"])
    if roles:
        return roles

    security_roles = get_security_roles_from_config()
    default_roles = _dedupe_preserve_order(
        [
            security_roles.get("admin", DEFAULT_SECURITY_ROLES["admin"]),
            security_roles.get("super_admin", DEFAULT_SECURITY_ROLES["super_admin"]),
            security_roles.get("commercial", DEFAULT_SECURITY_ROLES["commercial"]),
        ]
    )

    logger.warning(
        "Using default validator roles because config is missing the path workflows.validation.permissions.validator_roles"
    )
    return default_roles


@lru_cache()
def get_validation_workflow_config() -> dict[str, Any]:
    """Read validation workflow statuses, types and transitions from configuration."""
    config_path = Path(
        os.getenv(
            "AUTH_CONFIG_PATH",
            Path(__file__).resolve().parents[4] / "auth-microservice/config/base.yaml",
        )
    )
    config = _read_config_file(config_path)

    statuses = _get_dict(config, ["workflows", "validation", "statuses"]) or {}
    types = _get_dict(config, ["workflows", "validation", "types"]) or {}
    transitions = _get_dict(config, ["workflows", "validation", "transitions"]) or {}

    approve_transition = transitions.get("approve", {}) if isinstance(transitions, dict) else {}
    reject_transition = transitions.get("reject", {}) if isinstance(transitions, dict) else {}

    def _sanitize_from(value: Any, default: list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        return default

    return {
        "statuses": {**DEFAULT_VALIDATION_STATUSES, **{k: v for k, v in statuses.items() if isinstance(v, str)}},
        "types": {**DEFAULT_VALIDATION_TYPES, **{k: v for k, v in types.items() if isinstance(v, str)}},
        "transitions": {
            "approve": {
                "from": _sanitize_from(
                    approve_transition.get("from"),
                    DEFAULT_VALIDATION_TRANSITIONS["approve"]["from"],
                ),
                "to": approve_transition.get("to", DEFAULT_VALIDATION_TRANSITIONS["approve"]["to"]),
            },
            "reject": {
                "from": _sanitize_from(
                    reject_transition.get("from"),
                    DEFAULT_VALIDATION_TRANSITIONS["reject"]["from"],
                ),
                "to": reject_transition.get("to", DEFAULT_VALIDATION_TRANSITIONS["reject"]["to"]),
            },
        },
    }


@lru_cache()
def get_profile_types_from_config() -> dict[str, str]:
    """Read profile types from configuration (profiles.types)."""
    config_path = Path(
        os.getenv(
            "AUTH_CONFIG_PATH",
            Path(__file__).resolve().parents[4] / "auth-microservice/config/base.yaml",
        )
    )
    config = _read_config_file(config_path)
    configured_types = _get_dict(config, ["profiles", "types"]) or {}
    return {**DEFAULT_PROFILE_TYPES, **{k: v for k, v in configured_types.items() if isinstance(v, str)}}


@lru_cache()
def get_all_profile_type_values() -> list[str]:
    """Return the configured profile codes including explicit lists."""
    config_path = Path(
        os.getenv(
            "AUTH_CONFIG_PATH",
            Path(__file__).resolve().parents[4] / "auth-microservice/config/base.yaml",
        )
    )
    config = _read_config_file(config_path)
    configured_types = _get_dict(config, ["profiles", "types"]) or {}
    explicit_all = _get_list(config, ["profiles", "types", "all"]) or []

    merged = _dedupe_preserve_order(list(configured_types.values()) + explicit_all)
    fallback = _dedupe_preserve_order(list(DEFAULT_PROFILE_TYPES.values()))
    return merged or fallback


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
    admin_roles = get_admin_roles_from_config()
    user_roles = current_user.get('roles', [])
    if not any(role in admin_roles for role in user_roles):
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
