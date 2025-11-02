"""
Custom exceptions for the authentication system
"""
from typing import Optional


class AuthError(Exception):
    """Base exception for all authentication errors"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AuthError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(AuthError):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions", details: Optional[dict] = None):
        super().__init__(message, status_code=403, details=details)


class InvalidTokenError(AuthError):
    """Raised when token is invalid or expired"""
    def __init__(self, message: str = "Invalid or expired token", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)


class UserNotFoundError(AuthError):
    """Raised when user is not found"""
    def __init__(self, message: str = "User not found", details: Optional[dict] = None):
        super().__init__(message, status_code=404, details=details)


class ProviderError(AuthError):
    """Raised when authentication provider encounters an error"""
    def __init__(self, provider: str, message: str, details: Optional[dict] = None):
        super().__init__(f"Provider '{provider}' error: {message}", status_code=500, details=details)


class RateLimitError(AuthError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        details = {"retry_after": retry_after}
        super().__init__(message, status_code=429, details=details)
