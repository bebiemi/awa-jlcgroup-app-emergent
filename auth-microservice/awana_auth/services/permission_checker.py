"""
Permission Checker Service for IAM
Provides utilities to check user permissions based on profiles and groups
"""
from typing import List, Optional, Set
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

class PermissionChecker:
    """Service to check user permissions with caching"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)
    
    def _get_cache_key(self, user_id: str) -> str:
        """Generate cache key for user permissions"""
        return f"user_permissions:{user_id}"
    
    def _get_cached_permissions(self, user_id: str) -> Optional[Set[str]]:
        """Get cached permissions if not expired"""
        cache_key = self._get_cache_key(user_id)
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                return cached_data
        return None
    
    def _set_cached_permissions(self, user_id: str, permissions: Set[str]):
        """Cache user permissions"""
        cache_key = self._get_cache_key(user_id)
        self._cache[cache_key] = (permissions, datetime.utcnow())
    
    def clear_cache(self, user_id: Optional[str] = None):
        """Clear permission cache for user or all users"""
        if user_id:
            cache_key = self._get_cache_key(user_id)
            self._cache.pop(cache_key, None)
        else:
            self._cache.clear()
    
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """
        Get all effective permissions for a user
        Includes permissions from:
        1. Direct profile assignments
        2. Group profile assignments
        3. Built-in system roles
        """
        # Check cache first
        cached = self._get_cached_permissions(user_id)
        if cached is not None:
            return cached
        
        permission_codes = set()
        
        # Get user data
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return permission_codes
        
        # SuperAdmin has ALL permissions
        if "super_admin" in user.get("roles", []):
            # Get all permission codes
            all_permissions = await self.db.permissions.find({}, {"code": 1}).to_list(length=None)
            permission_codes = {p["code"] for p in all_permissions}
            self._set_cached_permissions(user_id, permission_codes)
            return permission_codes
        
        # Get direct profile IDs
        profile_ids = user.get("profile_ids", [])
        
        # Get group IDs and their profile IDs
        group_ids = user.get("group_ids", [])
        if group_ids:
            groups = await self.db.groups.find({"id": {"$in": group_ids}}).to_list(length=None)
            for group in groups:
                profile_ids.extend(group.get("profile_ids", []))
        
        # Remove duplicates
        profile_ids = list(set(profile_ids))
        
        if not profile_ids:
            self._set_cached_permissions(user_id, permission_codes)
            return permission_codes
        
        # Get all permission IDs from profiles
        profiles = await self.db.profiles.find({"id": {"$in": profile_ids}}).to_list(length=None)
        permission_ids = []
        for profile in profiles:
            permission_ids.extend(profile.get("permission_ids", []))
        
        # Remove duplicates
        permission_ids = list(set(permission_ids))
        
        if not permission_ids:
            self._set_cached_permissions(user_id, permission_codes)
            return permission_codes
        
        # Get permission codes
        permissions = await self.db.permissions.find(
            {"id": {"$in": permission_ids}},
            {"code": 1}
        ).to_list(length=None)
        permission_codes = {p["code"] for p in permissions}
        
        # Cache the result
        self._set_cached_permissions(user_id, permission_codes)
        
        return permission_codes
    
    async def user_has_permission(
        self, 
        user_id: str, 
        permission_code: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user_id: User ID to check
            permission_code: Permission code (e.g., "users.manage")
            resource_id: Optional resource ID for scope checking
        
        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = await self.get_user_permissions(user_id)
        
        # Direct match
        if permission_code in user_permissions:
            return True
        
        # Wildcard matching (e.g., "users.*" matches "users.manage")
        parts = permission_code.split(".")
        for i in range(len(parts)):
            wildcard = ".".join(parts[:i+1]) + ".*"
            if wildcard in user_permissions:
                return True
        
        return False
    
    def user_has_any_permission(
        self, 
        user_id: str, 
        permission_codes: List[str]
    ) -> bool:
        """Check if user has ANY of the specified permissions"""
        for code in permission_codes:
            if self.user_has_permission(user_id, code):
                return True
        return False
    
    def user_has_all_permissions(
        self, 
        user_id: str, 
        permission_codes: List[str]
    ) -> bool:
        """Check if user has ALL of the specified permissions"""
        for code in permission_codes:
            if not self.user_has_permission(user_id, code):
                return False
        return True
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get user's system roles (legacy support)
        Returns list of role names
        """
        user = self.db.users.find_one({"id": user_id})
        if not user:
            return []
        return user.get("roles", [])
    
    def user_has_role(self, user_id: str, role: str) -> bool:
        """
        Check if user has a specific role (legacy support)
        DEPRECATED: Use user_has_permission instead
        """
        roles = self.get_user_roles(user_id)
        return role in roles


# Singleton instance
_permission_checker_instance = None

def get_permission_checker(db: Database) -> PermissionChecker:
    """Get or create PermissionChecker singleton instance"""
    global _permission_checker_instance
    if _permission_checker_instance is None:
        _permission_checker_instance = PermissionChecker(db)
    return _permission_checker_instance
