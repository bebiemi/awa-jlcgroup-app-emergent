"""
FastAPI decorators for role and permission-based authorization
"""
from functools import wraps
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from ..core.models import User
from ..core.exceptions import AuthorizationError


def require_role(*role_names: str):
    """
    Decorator to require specific roles
    
    Usage:
        @app.get("/admin/users")
        @require_role("admin", "super_admin")
        async def get_users(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has any of the required roles
            user_role_names = set(current_user.roles)
            required_role_names = set(role_names)
            
            if not user_role_names.intersection(required_role_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of these roles: {', '.join(role_names)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(*permissions: str, require_all: bool = True):
    """
    Decorator to require specific permissions
    
    Usage:
        @app.delete("/admin/users/{user_id}")
        @require_permission("users.delete")
        async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
            ...
    
    Args:
        permissions: Required permission names (e.g., "users:write", "content:delete")
        require_all: If True, user must have ALL permissions. If False, any permission is enough.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user and rbac_manager from kwargs
            current_user = kwargs.get("current_user")
            rbac_manager = kwargs.get("rbac_manager")
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not rbac_manager:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="RBAC manager not available"
                )
            
            try:
                await rbac_manager.check_authorization(
                    user=current_user,
                    required_permissions=list(permissions),
                    require_all_permissions=require_all
                )
            except AuthorizationError as e:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=str(e)
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_role(*role_names: str):
    """
    Decorator to require any of the specified roles
    Alias for require_role (which already checks for any role)
    """
    return require_role(*role_names)
