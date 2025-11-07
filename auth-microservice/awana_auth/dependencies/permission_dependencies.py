"""
FastAPI Dependencies for Permission-Based Access Control
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.models import User
from awana_auth.dependencies.auth import get_current_user
from awana_auth.services.permission_checker import PermissionChecker
from awana_auth.core.dependencies import get_database

class PermissionDependency:
    """
    Dependency to check user permissions
    Usage: 
        @router.get("/", dependencies=[Depends(require_permission("users.read"))])
        or
        user: User = Depends(require_permission("users.manage"))
    """
    
    def __init__(
        self, 
        permission_code: str,
        require_all: bool = True,
        resource_id_param: Optional[str] = None
    ):
        self.permission_code = permission_code
        self.require_all = require_all
        self.resource_id_param = resource_id_param
    
    async def __call__(
        self, 
        current_user: User = Depends(get_current_user),
        db: AsyncIOMotorDatabase = Depends(get_database)
    ) -> User:
        """Check if user has required permission"""
        checker = PermissionChecker(db)
        
        # SuperAdmin bypass
        if "super_admin" in current_user.roles:
            return current_user
        
        # Check permission
        has_permission = await checker.user_has_permission(
            current_user.id, 
            self.permission_code
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {self.permission_code}"
            )
        
        return current_user


class MultiPermissionDependency:
    """
    Dependency to check multiple permissions
    Usage: 
        @router.get("/", dependencies=[Depends(require_any_permission(["users.read", "users.manage"]))])
    """
    
    def __init__(
        self, 
        permission_codes: List[str],
        require_all: bool = False  # False = ANY, True = ALL
    ):
        self.permission_codes = permission_codes
        self.require_all = require_all
    
    async def __call__(
        self, 
        current_user: User = Depends(get_current_user),
        db: AsyncIOMotorDatabase = Depends(get_database)
    ) -> User:
        """Check if user has required permissions"""
        checker = PermissionChecker(db)
        
        # SuperAdmin bypass
        if "super_admin" in current_user.roles:
            return current_user
        
        # Check permissions
        if self.require_all:
            has_permission = await checker.user_has_all_permissions(
                current_user.id, 
                self.permission_codes
            )
            error_msg = f"All permissions required: {', '.join(self.permission_codes)}"
        else:
            has_permission = await checker.user_has_any_permission(
                current_user.id, 
                self.permission_codes
            )
            error_msg = f"At least one permission required: {', '.join(self.permission_codes)}"
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. {error_msg}"
            )
        
        return current_user


# Convenience functions
def require_permission(permission_code: str) -> PermissionDependency:
    """
    Require a specific permission
    Usage: @router.get("/", dependencies=[Depends(require_permission("users.read"))])
    """
    return PermissionDependency(permission_code)


def require_any_permission(permission_codes: List[str]) -> MultiPermissionDependency:
    """
    Require ANY of the specified permissions
    Usage: @router.get("/", dependencies=[Depends(require_any_permission(["users.read", "users.manage"]))])
    """
    return MultiPermissionDependency(permission_codes, require_all=False)


def require_all_permissions(permission_codes: List[str]) -> MultiPermissionDependency:
    """
    Require ALL of the specified permissions
    Usage: @router.get("/", dependencies=[Depends(require_all_permissions(["users.read", "users.manage"]))])
    """
    return MultiPermissionDependency(permission_codes, require_all=True)


# Legacy role-based dependency (deprecated)
class RoleDependency:
    """
    DEPRECATED: Use PermissionDependency instead
    Legacy dependency for role-based access control
    """
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    async def __call__(
        self, 
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Check if user has required role"""
        user_roles = set(current_user.roles)
        required_roles = set(self.required_roles)
        
        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.required_roles)}"
            )
        
        return current_user


def require_role(roles: List[str]) -> RoleDependency:
    """
    DEPRECATED: Use require_permission instead
    Legacy function for role-based access
    """
    return RoleDependency(roles)
