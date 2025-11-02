"""
AWANA Authentication & Authorization System

A modular, extensible authentication system supporting multiple providers:
- EntraID OAuth 2.0 / OIDC
- WebAuthn / Passkeys (prepared)
- TOTP (prepared)
- Custom providers (extensible)

Features:
- Role-Based Access Control (RBAC)
- JWT Session Management
- Audit Logging
- Multi-provider support
"""

__version__ = "1.0.0"
__author__ = "AWANA GROUP"

from .core.config import AuthConfig
from .core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    UserNotFoundError,
)
from .rbac.decorators import require_role, require_permission

__all__ = [
    "AuthConfig",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidTokenError",
    "UserNotFoundError",
    "require_role",
    "require_permission",
]
