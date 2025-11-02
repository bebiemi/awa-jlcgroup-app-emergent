"""
Rate limiting configuration for API endpoints
Protects against brute force, DoS, and resource exhaustion attacks
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors
    Returns a JSON response with clear error message
    """
    logger.warning(
        f"Rate limit exceeded for {request.client.host} on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "retry_after_seconds": exc.detail if hasattr(exc, 'detail') else 60
        },
        headers={"Retry-After": str(60)}
    )

# Initialize limiter with Redis storage for production
# Redis provides persistent, centralized rate limiting across instances
import os

REDIS_URL = os.getenv("REDIS_URL", "memory://")

# Force memory storage if Redis is not available
try:
    import redis
    # Test Redis connection
    r = redis.from_url(REDIS_URL if REDIS_URL != "memory://" else "redis://localhost:6379")
    r.ping()
    logger.info("Redis connection successful")
except Exception as e:
    logger.warning(f"Redis not available ({e}), falling back to memory storage")
    REDIS_URL = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],  # Global default limit
    storage_uri=REDIS_URL,
    headers_enabled=True,
)

logger.info(f"Rate limiter initialized with storage: {REDIS_URL}")

# Rate limit definitions for different endpoint categories
RATE_LIMITS = {
    "auth_login": "5/minute",           # Strict limit for login attempts
    "auth_register": "10/minute",       # Registration attempts
    "auth_token": "10/minute",          # EntraID token exchange
    "auth_refresh": "30/minute",        # Token refresh
    "upload": "10/hour",                # File uploads
    "contact": "3/minute",              # Contact form (spam protection)
    "admin_read": "120/minute",         # Admin GET requests
    "admin_write": "60/minute",         # Admin POST/PUT/DELETE
    "public_api": "60/minute",          # Public API endpoints
    "chatbot": "20/minute",             # Chatbot interactions
}

def get_rate_limit(category: str) -> str:
    """Get rate limit string for a category"""
    return RATE_LIMITS.get(category, "100/hour")
