"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..core.config import auth_config
from ..core.models import User
from ..core.exceptions import InvalidTokenError, UserNotFoundError
from ..session.jwt import JWTManager
from ..session.storage import SessionStorage
from ..rbac.manager import RBACManager
from .config_manager import get_config
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)

# Global instances (will be initialized)
_jwt_manager: Optional[JWTManager] = None
_session_storage: Optional[SessionStorage] = None
_rbac_manager: Optional[RBACManager] = None
_db: Optional[AsyncIOMotorDatabase] = None
_iam_service: Optional['IAMService'] = None
_cache_service = None


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance from ConfigManager"""
    global _db
    
    if _db is None:
        config = get_config()
        mongo_url = config.get_secret("MONGO_URL", required=True)
        database_name = config.get("database.name", required=True)
        pool_size = config.get("database.pool_size", default=10)
        
        client = AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=pool_size,
            minPoolSize=config.get("database.min_pool_size", default=5)
        )
        _db = client[database_name]
        logger.info(f"✅ Database initialized: {database_name} (pool={pool_size})")
    
    return _db


# Alias for compatibility
get_db = get_database


def get_configuration():
    """Dependency to inject ConfigManager in routes"""
    return get_config()


def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance"""
    global _jwt_manager
    
    if _jwt_manager is None:
        _jwt_manager = JWTManager(auth_config)
        logger.info("JWT Manager initialized")
    
    return _jwt_manager


def get_session_storage(db: AsyncIOMotorDatabase = Depends(get_database)) -> SessionStorage:
    """Get session storage instance"""
    global _session_storage
    
    if _session_storage is None:
        _session_storage = SessionStorage(db, auth_config)
        logger.info("Session Storage initialized")
    
    return _session_storage


def get_rbac_manager(db: AsyncIOMotorDatabase = Depends(get_database)) -> RBACManager:
    """Get RBAC manager instance"""
    global _rbac_manager
    
    if _rbac_manager is None:
        _rbac_manager = RBACManager(db)
        logger.info("RBAC Manager initialized")
    
    return _rbac_manager


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify JWT token
        token_payload = jwt_manager.verify_token(token, token_type="access")
        
        # Get session
        session = await session_storage.get_session(token_payload.session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user_doc = await db.users.find_one({"id": token_payload.sub}, {"_id": 0})
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_doc)
        
        # Check if user is active
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User account is {user.status}"
            )
        
        return user
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    Useful for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, jwt_manager, session_storage, db)
    except HTTPException:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
) -> User:
    """
    DEPRECATED: Use require_permission from permission_dependencies instead
    
    Require user to have admin or super_admin role
    This function is kept for backward compatibility only.
    """
    import warnings
    warnings.warn(
        "require_admin is deprecated. Use require_permission('users.manage') instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Check roles directly from the user object (works for both local and OAuth users)
    user_roles = set(current_user.roles) if current_user.roles else set()
    admin_roles = {"admin", "super_admin"}
    
    if not user_roles.intersection(admin_roles):
        # Fallback to RBAC manager for legacy users
        has_role = await rbac_manager.has_any_role(current_user.id, ["admin", "super_admin"])
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
    
    return current_user


async def require_super_admin(
    current_user: User = Depends(get_current_user),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
) -> User:
    """
    DEPRECATED: Use require_permission from permission_dependencies instead
    
    Require user to have super_admin role
    This function is kept for backward compatibility only.
    """
    import warnings
    warnings.warn(
        "require_super_admin is deprecated. Use require_permission('admin.access') instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Check role directly from the user object (works for both local and OAuth users)
    user_roles = set(current_user.roles) if current_user.roles else set()
    
    if "super_admin" not in user_roles:
        # Fallback to RBAC manager for legacy users
        has_role = await rbac_manager.has_role(current_user.id, "super_admin")
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin privileges required"
            )
    
    return current_user
