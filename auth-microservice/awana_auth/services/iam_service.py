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
    
    def __init__(self, db: AsyncIOMotorDatabase, cache_service=None):
        self.db = db
        self.permissions_collection = db.permissions
        self.profiles_collection = db.profiles
        self.groups_collection = db.groups
        self.users_collection = db.users
        self.bundles_collection = db.capability_bundles  # Support des bundles de capacités
        self.cache = cache_service  # Service de cache Redis (optionnel)
        logger.info(f"IAMService initialized with cache: {cache_service is not None}")
    
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
            
            # 3. Get all permissions from profiles (directes + bundles)
            profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
            all_permission_ids = set()
            async for profile in profiles_cursor:
                # Permissions directes
                all_permission_ids.update(profile.get("permission_ids", []))
                
                # Permissions des bundles
                bundle_ids = profile.get("capability_bundle_ids", [])
                if bundle_ids:
                    bundles_cursor = self.bundles_collection.find({"id": {"$in": bundle_ids}})
                    async for bundle in bundles_cursor:
                        all_permission_ids.update(bundle.get("permission_ids", []))
            
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
            # Tenter de récupérer depuis le cache
            if self.cache:
                cached_data = await self.cache.get_user_permissions(user_id)
                if cached_data:
                    logger.debug(f"🎯 Cache HIT pour permissions user {user_id}")
                    # Reconstruire les objets Pydantic depuis le cache JSON
                    return UserPermissionsResponse(
                        user_id=cached_data.get("user_id"),
                        direct_profiles=[Profile(**p) for p in cached_data.get("direct_profiles", [])],
                        group_profiles=[Profile(**p) for p in cached_data.get("group_profiles", [])],
                        all_permissions=[Permission(**p) for p in cached_data.get("all_permissions", [])],
                        groups=[Group(**g) for g in cached_data.get("groups", [])]
                    )
            
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
                    try:
                        # Remove MongoDB _id before creating Pydantic model
                        profile.pop("_id", None)
                        group_profiles.append(Profile(**profile))
                    except Exception as e:
                        logger.error(f"Error creating Profile model from group: {e}, profile data: {profile}")
            
            # Get all unique permissions (directes + bundles)
            all_profile_ids = set(direct_profile_ids) | group_profile_ids
            all_permission_ids = set()
            
            if all_profile_ids:
                profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
                async for profile in profiles_cursor:
                    # Permissions directes du profil
                    all_permission_ids.update(profile.get("permission_ids", []))
                    
                    # Permissions des bundles de capacités
                    bundle_ids = profile.get("capability_bundle_ids", [])
                    if bundle_ids:
                        bundles_cursor = self.bundles_collection.find({"id": {"$in": bundle_ids}})
                        async for bundle in bundles_cursor:
                            bundle_perms = bundle.get("permission_ids", [])
                            all_permission_ids.update(bundle_perms)
                            logger.debug(f"Added {len(bundle_perms)} permissions from bundle {bundle.get('code')}")
            
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
            
            response = UserPermissionsResponse(
                user_id=user_id,
                direct_profiles=direct_profiles,
                group_profiles=group_profiles,
                all_permissions=all_permissions,
                groups=groups
            )
            
            # Mettre en cache le résultat
            if self.cache:
                cache_data = {
                    "user_id": user_id,
                    "direct_profiles": [p.model_dump() for p in direct_profiles],
                    "group_profiles": [p.model_dump() for p in group_profiles],
                    "all_permissions": [p.model_dump() for p in all_permissions],
                    "groups": [g.model_dump() for g in groups]
                }
                await self.cache.set_user_permissions(user_id, cache_data)
                logger.debug(f"💾 Permissions user {user_id} mises en cache")
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return UserPermissionsResponse(user_id=user_id)
    
    async def assign_profiles_to_user(self, user_id: str, profile_ids: List[str]) -> bool:
        """Assign profiles directly to a user (additive - keeps existing profiles)"""
        try:
            # Use $addToSet to add profiles without duplicates (keeps existing ones)
            result = await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$addToSet": {"profile_ids": {"$each": profile_ids}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
            # Invalider le cache pour cet utilisateur
            if self.cache and result.modified_count > 0:
                await self.cache.invalidate_user_permissions(user_id)
                logger.info(f"🗑️  Cache invalidé pour user {user_id} après assignation de profil")
            
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            logger.error(f"Error assigning profiles to user: {e}")
            return False
    
    async def assign_groups_to_user(self, user_id: str, group_ids: List[str]) -> bool:
        """Assign user to groups (additive - keeps existing groups)"""
        try:
            # Use $addToSet to add groups without duplicates (keeps existing ones)
            result = await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$addToSet": {"group_ids": {"$each": group_ids}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
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
