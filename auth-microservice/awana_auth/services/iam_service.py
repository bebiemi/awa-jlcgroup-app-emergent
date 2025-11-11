"""
IAM Service - Identity and Access Management
Implements permission checking, inheritance, and RBAC logic
"""
from typing import List, Optional, Set
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging

from awana_auth.core.iam_models import (
    Permission, Profile, Group,
    PermissionCheckResponse, UserPermissionsResponse
)

logger = logging.getLogger(__name__)


class IAMService:
    """
    Core IAM service implementing RBAC with inheritance
    
    Permission Resolution Order:
    1. Direct user profiles
    2. Group profiles (all groups user belongs to)
    3. Most permissive wins in case of conflict
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.permissions_collection = db.permissions
        self.profiles_collection = db.profiles
        self.groups_collection = db.groups
        self.users_collection = db.users
    
    async def user_has_permission(
        self, 
        user_id: str, 
        permission_code: str,
        resource_id: Optional[str] = None
    ) -> PermissionCheckResponse:
        """
        Check if user has a specific permission
        
        Args:
            user_id: User ID to check
            permission_code: Permission code (e.g., "missions.create")
            resource_id: Optional resource ID for scope checking
        
        Returns:
            PermissionCheckResponse with result and reasoning
        """
        try:
            # Get user data
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return PermissionCheckResponse(
                    has_permission=False,
                    reason="User not found"
                )
            
            # SuperAdmin bypass - has all permissions
            if "super_admin" in user.get("roles", []):
                return PermissionCheckResponse(
                    has_permission=True,
                    granted_by=["SuperAdmin Role"],
                    reason="SuperAdmin has all permissions"
                )
            
            # Get all user's profiles (direct + from groups)
            all_profile_ids = set()
            granted_by = []
            
            # 1. Direct profiles
            direct_profile_ids = user.get("profile_ids", [])
            all_profile_ids.update(direct_profile_ids)
            if direct_profile_ids:
                granted_by.append("Direct assignment")
            
            # 2. Profiles from groups
            user_group_ids = user.get("group_ids", [])
            if user_group_ids:
                groups_cursor = self.groups_collection.find({"id": {"$in": user_group_ids}})
                async for group in groups_cursor:
                    group_profile_ids = group.get("profile_ids", [])
                    all_profile_ids.update(group_profile_ids)
                    if group_profile_ids:
                        granted_by.append(f"Group: {group.get('name')}")
            
            if not all_profile_ids:
                return PermissionCheckResponse(
                    has_permission=False,
                    reason="User has no profiles assigned"
                )
            
            # 3. Get all permissions from profiles
            profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
            all_permission_ids = set()
            async for profile in profiles_cursor:
                all_permission_ids.update(profile.get("permission_ids", []))
            
            # 4. Check if permission exists in user's permissions
            permission = await self.permissions_collection.find_one({"code": permission_code})
            if not permission:
                return PermissionCheckResponse(
                    has_permission=False,
                    reason=f"Permission '{permission_code}' not found"
                )
            
            has_perm = permission["id"] in all_permission_ids
            
            return PermissionCheckResponse(
                has_permission=has_perm,
                granted_by=granted_by if has_perm else [],
                reason="Permission granted" if has_perm else "Permission not in user's profiles"
            )
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return PermissionCheckResponse(
                has_permission=False,
                reason=f"Error: {str(e)}"
            )
    
    async def get_user_permissions(self, user_id: str) -> UserPermissionsResponse:
        """
        Get all permissions for a user with full details
        
        Returns:
            Complete permission structure with profiles, groups, and permissions
        """
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return UserPermissionsResponse(user_id=user_id)
            
            # Get direct profiles
            direct_profile_ids = user.get("profile_ids", [])
            direct_profiles = []
            logger.info(f"Looking for profiles with IDs: {direct_profile_ids}")
            if direct_profile_ids:
                profiles_cursor = self.profiles_collection.find({"id": {"$in": direct_profile_ids}})
                async for profile in profiles_cursor:
                    try:
                        # Remove MongoDB _id before creating Pydantic model
                        profile.pop("_id", None)
                        direct_profiles.append(Profile(**profile))
                        logger.info(f"Added profile: {profile.get('name')}")
                    except Exception as e:
                        logger.error(f"Error creating Profile model: {e}, profile data: {profile}")
            
            # Get groups and their profiles
            user_group_ids = user.get("group_ids", [])
            groups = []
            group_profile_ids = set()
            
            if user_group_ids:
                groups_cursor = self.groups_collection.find({"id": {"$in": user_group_ids}})
                async for group_doc in groups_cursor:
                    try:
                        # Remove MongoDB _id before creating Pydantic model
                        group_doc.pop("_id", None)
                        groups.append(Group(**group_doc))
                        group_profile_ids.update(group_doc.get("profile_ids", []))
                    except Exception as e:
                        logger.error(f"Error creating Group model: {e}, group data: {group_doc}")
            
            group_profiles = []
            if group_profile_ids:
                profiles_cursor = self.profiles_collection.find({"id": {"$in": list(group_profile_ids)}})
                async for profile in profiles_cursor:
                    group_profiles.append(Profile(**profile))
            
            # Get all unique permissions
            all_profile_ids = set(direct_profile_ids) | group_profile_ids
            all_permission_ids = set()
            
            if all_profile_ids:
                profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
                async for profile in profiles_cursor:
                    all_permission_ids.update(profile.get("permission_ids", []))
            
            all_permissions = []
            if all_permission_ids:
                perms_cursor = self.permissions_collection.find({"id": {"$in": list(all_permission_ids)}})
                async for perm in perms_cursor:
                    try:
                        # Remove MongoDB _id before creating Pydantic model
                        perm.pop("_id", None)
                        all_permissions.append(Permission(**perm))
                    except Exception as e:
                        logger.error(f"Error creating Permission model: {e}, permission data: {perm}")
            
            return UserPermissionsResponse(
                user_id=user_id,
                direct_profiles=direct_profiles,
                group_profiles=group_profiles,
                all_permissions=all_permissions,
                groups=groups
            )
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return UserPermissionsResponse(user_id=user_id)
    
    async def assign_profiles_to_user(self, user_id: str, profile_ids: List[str]) -> bool:
        """Assign profiles directly to a user"""
        try:
            result = await self.users_collection.update_one(
                {"id": user_id},
                {"$set": {
                    "profile_ids": profile_ids,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error assigning profiles to user: {e}")
            return False
    
    async def assign_groups_to_user(self, user_id: str, group_ids: List[str]) -> bool:
        """Assign user to groups"""
        try:
            # Update user's groups
            result = await self.users_collection.update_one(
                {"id": user_id},
                {"$set": {
                    "group_ids": group_ids,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            # Update each group's user list
            for group_id in group_ids:
                await self.groups_collection.update_one(
                    {"id": group_id},
                    {"$addToSet": {"user_ids": user_id}}
                )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error assigning groups to user: {e}")
            return False
