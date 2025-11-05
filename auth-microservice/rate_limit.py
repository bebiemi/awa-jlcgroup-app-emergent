"""
Rate limiting configuration for API endpoints
Protects against brute force, DoS, and resource exhaustion attacks
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from awana_auth.core.config_manager import get_config
import logging

logger = logging.getLogger(__name__)
config = get_config()

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

# Charger la configuration de rate limiting
rate_limit_enabled = config.get("security.rate_limit.enabled", default=True)
default_limit = config.get("security.rate_limit.default_limit", default=100)
default_period = config.get("security.rate_limit.default_period_seconds", default=60)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{default_limit}/{default_period} second"] if rate_limit_enabled else [],
    storage_uri=REDIS_URL,
    headers_enabled=True,
    enabled=rate_limit_enabled
)

logger.info(f"Rate limiter initialized (enabled={rate_limit_enabled}, storage={REDIS_URL})")

def get_rate_limit(category: str) -> str:
    """
    Get rate limit string for a category from configuration
    Falls back to default if not configured
    """
    if not rate_limit_enabled:
        return "1000/hour"  # Très permissif si désactivé
    
    # Essayer de récupérer depuis la config
    route_config = config.get(f"security.rate_limit.routes.{category}")
    if route_config:
        limit = route_config.get("limit", default_limit)
        period = route_config.get("period_seconds", default_period)
        return f"{limit}/{period} second"
    
    # Valeurs par défaut hardcodées pour compatibilité
    RATE_LIMITS = {
        "auth_login": f"{config.get('security.rate_limit.routes.login.limit', default=5)}/{config.get('security.rate_limit.routes.login.period_seconds', default=300)} second",
        "auth_register": f"{config.get('security.rate_limit.routes.register.limit', default=3)}/{config.get('security.rate_limit.routes.register.period_seconds', default=3600)} second",
        "password_reset": f"{config.get('security.rate_limit.routes.password_reset.limit', default=3)}/{config.get('security.rate_limit.routes.password_reset.period_seconds', default=3600)} second",
    }
    
    return RATE_LIMITS.get(category, f"{default_limit}/{default_period} second")
