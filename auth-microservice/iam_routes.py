"""
IAM Routes - Identity and Access Management API
Complete CRUD for Permissions, Profiles, Groups, and Assignments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
import logging

from awana_auth.core.iam_models import (
    Permission, PermissionCreate,
    Profile, ProfileCreate, ProfileUpdate,
    Group, GroupCreate, GroupUpdate,
    UserProfileAssignment, UserGroupAssignment,
    PermissionCheckRequest, PermissionCheckResponse,
    UserPermissionsResponse
)
from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.dependencies.permission_dependencies import require_permission, require_any_permission
from awana_auth.core.models import User
from awana_auth.services.iam_service import IAMService
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iam", tags=["IAM"])


# ============================================================================
# Permissions Management
# ============================================================================

@router.get("/permissions", response_model=List[Permission])
async def list_permissions(
    current_user: User = Depends(require_permission("iam.permissions.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all permissions, optionally filtered by module"""
    permissions_collection = db.permissions
    permissions = []
    
    cursor = permissions_collection.find({}, {"_id": 0})
    async for perm in cursor:
        permissions.append(Permission.model_validate(perm))
    
    return permissions


@router.post("/permissions", response_model=Permission, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_permission("iam.permissions.create")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new permission (super admin only)"""
    permissions_collection = db.permissions
    
    # Check if permission code already exists
    existing = await permissions_collection.find_one({"code": permission_data.code})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission with code '{permission_data.code}' already exists"
        )
    
    # Create permission
    import uuid
    permission = Permission(
        id=str(uuid.uuid4()),
        **permission_data.dict(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    await permissions_collection.insert_one(permission.dict())
    logger.info(f"Permission created: {permission.code} by {current_user.username}")
    
    return permission


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: str,
    current_user: User = Depends(require_permission("iam.permissions.delete")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete permission (super admin only, not if system protected)"""
    permissions_collection = db.permissions
    
    # Check if permission exists
    permission = await permissions_collection.find_one({"id": permission_id})
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if protected
    if permission.get("is_system"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system permission"
        )
    
    # Remove from all profiles
    profiles_collection = db.profiles
    await profiles_collection.update_many(
        {"permission_ids": permission_id},
        {"$pull": {"permission_ids": permission_id}}
    )
    
    await permissions_collection.delete_one({"id": permission_id})
    logger.info(f"Permission deleted: {permission_id} by {current_user.username}")
    
    return {"success": True, "message": "Permission deleted"}


# ============================================================================
# Profiles Management
# ============================================================================

@router.get("/profiles", response_model=List[Profile])
async def list_profiles(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all profiles with effective permission counts"""
    profiles_collection = db.profiles
    bundles_collection = db.capability_bundles
    profiles = []
    
    cursor = profiles_collection.find({}, {"_id": 0})
    async for profile_data in cursor:
        # Calculer le count effectif (direct + bundles)
        direct_count = len(profile_data.get("permission_ids", []))
        bundle_count = 0
        
        bundle_refs = profile_data.get("capability_bundle_ids", []) or profile_data.get("bundles", [])
        if bundle_refs:
            # Récupérer les permissions de tous les bundles (deux collections)
            bundle_perms = set()
            
            # capability_bundles (nouveau)
            async for bundle in bundles_collection.find(
                {"$or": [{"id": {"$in": bundle_refs}}, {"code": {"$in": bundle_refs}}]},
                {"_id": 0, "permission_ids": 1, "permissions": 1}
            ):
                if "permission_ids" in bundle:
                    bundle_perms.update(bundle.get("permission_ids", []))
                elif "permissions" in bundle:
                    bundle_perms.update(bundle.get("permissions", []))
            
            # permission_bundles (config-driven)
            permission_bundles_collection = db.permission_bundles
            async for bundle in permission_bundles_collection.find(
                {"code": {"$in": bundle_refs}},
                {"_id": 0, "permissions": 1}
            ):
                bundle_perms.update(bundle.get("permissions", []))
            
            bundle_count = len(bundle_perms)
        
        # Ajouter les champs calculés
        profile_data["effective_permission_count"] = direct_count + bundle_count
        profile_data["bundle_permission_count"] = bundle_count
        
        profiles.append(Profile(**profile_data))
    
    return profiles


@router.get("/profiles/{profile_id}", response_model=Profile)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get profile details"""
    profiles_collection = db.profiles
    
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return Profile(**profile)


@router.get("/profiles/{profile_id}/effective-permissions")
async def get_profile_effective_permissions(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère toutes les permissions effectives d'un profil
    Inclut les permissions directes + permissions des bundles
    Supporte ancien format (codes) et nouveau format (IDs)
    """
    profiles_collection = db.profiles
    permissions_collection = db.permissions
    
    profile = await profiles_collection.find_one({"id": profile_id}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # === Support des deux formats ===
    # Nouveau format : permission_ids (UUIDs)
    # Ancien format : permissions (codes)
    
    direct_permission_codes = set()
    
    # Nouveau format avec IDs
    if "permission_ids" in profile and profile["permission_ids"]:
        direct_ids = profile["permission_ids"]
        async for perm in permissions_collection.find(
            {"id": {"$in": direct_ids}},
            {"_id": 0, "code": 1}
        ):
            direct_permission_codes.add(perm["code"])
    
    # Ancien format avec codes
    if "permissions" in profile and profile["permissions"]:
        legacy_perms = profile["permissions"]
        if legacy_perms == "*":  # Wildcard = toutes les permissions
            async for perm in permissions_collection.find({}, {"_id": 0, "code": 1}):
                direct_permission_codes.add(perm["code"])
        else:
            direct_permission_codes.update(legacy_perms)
    
    # Permissions des bundles
    bundle_permission_codes = set()
    
    # Support des deux formats pour les bundles
    bundle_refs = profile.get("capability_bundle_ids", []) or profile.get("bundles", [])
    
    if bundle_refs:
        # Chercher dans les deux collections de bundles
        bundles_collection_new = db.capability_bundles
        bundles_collection_old = db.permission_bundles
        
        # Chercher dans capability_bundles (nouveau format)
        async for bundle in bundles_collection_new.find(
            {"$or": [{"id": {"$in": bundle_refs}}, {"code": {"$in": bundle_refs}}]},
            {"_id": 0, "permission_ids": 1, "permissions": 1}
        ):
            # Nouveau format
            if "permission_ids" in bundle:
                async for perm in permissions_collection.find(
                    {"id": {"$in": bundle["permission_ids"]}},
                    {"_id": 0, "code": 1}
                ):
                    bundle_permission_codes.add(perm["code"])
            # Ancien format
            if "permissions" in bundle:
                bundle_permission_codes.update(bundle["permissions"])
        
        # Chercher dans permission_bundles (format config-driven)
        async for bundle in bundles_collection_old.find(
            {"code": {"$in": bundle_refs}},
            {"_id": 0, "permissions": 1}
        ):
            if "permissions" in bundle:
                bundle_permission_codes.update(bundle["permissions"])
    
    # Toutes les permissions effectives (union)
    all_permission_codes = direct_permission_codes | bundle_permission_codes
    
    # Récupérer les détails complets des permissions
    permissions = []
    if all_permission_codes:
        async for perm in permissions_collection.find(
            {"code": {"$in": list(all_permission_codes)}},
            {"_id": 0}
        ):
            permissions.append(perm)
    
    return {
        "profile_id": profile_id,
        "profile_code": profile.get("code"),
        "profile_name": profile.get("name"),
        "direct_permission_count": len(direct_permission_codes),
        "bundle_permission_count": len(bundle_permission_codes),
        "total_effective_permissions": len(all_permission_codes),
        "permissions": permissions,
        "capability_bundle_ids": bundle_refs,
        "direct_permissions": list(direct_permission_codes),
        "bundle_permissions": list(bundle_permission_codes)
    }


@router.post("/profiles", response_model=Profile, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(require_permission("iam.profiles.create")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new profile (admin only)"""
    profiles_collection = db.profiles
    
    # Check if profile code already exists
    existing = await profiles_collection.find_one({"code": profile_data.code})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile with code '{profile_data.code}' already exists"
        )
    
    # Validate permissions exist
    permissions_collection = db.permissions
    if profile_data.permission_ids:
        for perm_id in profile_data.permission_ids:
            perm = await permissions_collection.find_one({"id": perm_id})
            if not perm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission {perm_id} not found"
                )
    
    # Create profile
    import uuid
    profile = Profile(
        id=str(uuid.uuid4()),
        **profile_data.dict(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by=current_user.id
    )
    
    await profiles_collection.insert_one(profile.dict())
    logger.info(f"Profile created: {profile.code} by {current_user.username}")
    
    return profile


@router.put("/profiles/{profile_id}", response_model=Profile)
async def update_profile(
    profile_id: str,
    profile_data: ProfileUpdate,
    current_user: User = Depends(require_permission("iam.profiles.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update profile (admin only, not if protected)"""
    profiles_collection = db.profiles
    
    # Check if profile exists
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check if protected
    if profile.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify protected profile"
        )
    
    # Validate permissions if provided
    if profile_data.permission_ids is not None:
        permissions_collection = db.permissions
        for perm_id in profile_data.permission_ids:
            perm = await permissions_collection.find_one({"id": perm_id})
            if not perm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission {perm_id} not found"
                )
    
    # Update profile
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await profiles_collection.update_one(
        {"id": profile_id},
        {"$set": update_data}
    )
    
    # Get updated profile
    updated_profile = await profiles_collection.find_one({"id": profile_id})
    logger.info(f"Profile updated: {profile_id} by {current_user.username}")
    
    return Profile(**updated_profile)


@router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: str,
    force: bool = False,
    current_user: User = Depends(require_permission("iam.profiles.delete")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete profile (admin only, not if protected or in use)
    
    Args:
        profile_id: ID of profile to delete
        force: If True, removes profile from all users/groups before deletion
    """
    profiles_collection = db.profiles
    
    # Check if profile exists
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check if protected
    if profile.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete protected profile"
        )
    
    # Check if in use
    users_collection = db.users
    user_count = await users_collection.count_documents({"profile_ids": profile_id})
    
    groups_collection = db.groups
    group_count = await groups_collection.count_documents({"profile_ids": profile_id})
    
    if user_count > 0 or group_count > 0:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete profile: assigned to {user_count} users and {group_count} groups. Use force=true to remove assignments."
            )
        
        # Force mode: Remove profile from all users and groups
        await users_collection.update_many(
            {"profile_ids": profile_id},
            {"$pull": {"profile_ids": profile_id}}
        )
        
        await groups_collection.update_many(
            {"profile_ids": profile_id},
            {"$pull": {"profile_ids": profile_id}}
        )
        
        logger.info(f"Profile {profile_id} removed from {user_count} users and {group_count} groups")
    
    await profiles_collection.delete_one({"id": profile_id})
    logger.info(f"Profile deleted: {profile_id} by {current_user.username}")
    
    return {
        "success": True, 
        "message": "Profile deleted",
        "unassigned_users": user_count if force else 0,
        "unassigned_groups": group_count if force else 0
    }


# ============================================================================
# Groups Management
# ============================================================================

@router.get("/groups", response_model=List[Group])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all groups"""
    groups_collection = db.groups
    groups = []
    
    cursor = groups_collection.find({}, {"_id": 0})
    async for group in cursor:
        groups.append(Group(**group))
    
    return groups


@router.get("/groups/{group_id}", response_model=Group)
async def get_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get group details with members"""
    groups_collection = db.groups
    
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return Group(**group)


@router.post("/groups", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(require_permission("iam.groups.create")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new group (admin only)"""
    groups_collection = db.groups
    
    # Check if group code already exists
    existing = await groups_collection.find_one({"code": group_data.code})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Group with code '{group_data.code}' already exists"
        )
    
    # Validate profiles exist
    if group_data.profile_ids:
        profiles_collection = db.profiles
        for prof_id in group_data.profile_ids:
            prof = await profiles_collection.find_one({"id": prof_id})
            if not prof:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Profile {prof_id} not found"
                )
    
    # Create group
    import uuid
    group = Group(
        id=str(uuid.uuid4()),
        **group_data.dict(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by=current_user.id
    )
    
    await groups_collection.insert_one(group.dict())
    logger.info(f"Group created: {group.code} by {current_user.username}")
    
    return group


@router.put("/groups/{group_id}", response_model=Group)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_user: User = Depends(require_permission("iam.groups.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update group (admin only)"""
    groups_collection = db.groups
    
    # Check if group exists
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if protected
    if group.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify protected group"
        )
    
    # Update group
    update_data = {k: v for k, v in group_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await groups_collection.update_one(
        {"id": group_id},
        {"$set": update_data}
    )
    
    # Get updated group
    updated_group = await groups_collection.find_one({"id": group_id})
    logger.info(f"Group updated: {group_id} by {current_user.username}")
    
    return Group(**updated_group)


@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: str,
    current_user: User = Depends(require_permission("iam.groups.delete")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete group (admin only)"""
    groups_collection = db.groups
    
    # Check if group exists
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if protected
    if group.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete protected group"
        )
    
    # Remove group from all users
    users_collection = db.users
    await users_collection.update_many(
        {"group_ids": group_id},
        {"$pull": {"group_ids": group_id}}
    )
    
    await groups_collection.delete_one({"id": group_id})
    logger.info(f"Group deleted: {group_id} by {current_user.username}")
    
    return {"success": True, "message": "Group deleted"}


@router.post("/groups/{group_id}/profiles/{profile_id}")
async def assign_profile_to_group(
    group_id: str,
    profile_id: str,
    current_user: User = Depends(require_permission("iam.groups.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign a profile to a group"""
    groups_collection = db.groups
    profiles_collection = db.profiles
    
    # Verify group exists (search by id field, not _id)
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify profile exists (profiles use custom id field)
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check if protected
    if group.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify protected group"
        )
    
    # Check if profile already assigned
    if profile_id in group.get("profile_ids", []):
        return {
            "success": True,
            "message": f"Profile '{profile['name']}' already assigned to group '{group['name']}'",
            "group_code": group.get("code"),
            "already_assigned": True
        }
    
    # Assign profile to group (use id field to identify group)
    result = await groups_collection.update_one(
        {"id": group_id},
        {"$addToSet": {"profile_ids": profile_id}}
    )
    
    logger.info(f"Profile {profile_id} assigned to group {group_id} by {current_user.username}")
    
    # Invalidate cache for all users that have this group
    # Groups don't store user_ids, users store group codes in their 'roles' field
    iam_service = IAMService(db)
    group_code = group.get("code")
    if group_code:
        users_with_group = await db.users.find({"roles": group_code}).to_list(1000)
        for user in users_with_group:
            await iam_service.cache.invalidate_user(user["id"])
    
    return {
        "success": True,
        "message": f"Profile '{profile['name']}' assigned to group '{group['name']}'",
        "group_code": group_code
    }


@router.delete("/groups/{group_id}/profiles/{profile_id}")
async def remove_profile_from_group(
    group_id: str,
    profile_id: str,
    current_user: User = Depends(require_permission("iam.groups.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove a profile from a group"""
    groups_collection = db.groups
    
    # Verify group exists (search by id field, not _id)
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if protected
    if group.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify protected group"
        )
    
    # Remove profile from group (use id field to identify group)
    result = await groups_collection.update_one(
        {"id": group_id},
        {"$pull": {"profile_ids": profile_id}}
    )
    
    logger.info(f"Profile {profile_id} removed from group {group_id} by {current_user.username}")
    
    # Invalidate cache for all users that have this group
    iam_service = IAMService(db)
    group_code = group.get("code")
    if group_code:
        users_with_group = await db.users.find({"roles": group_code}).to_list(1000)
        for user in users_with_group:
            await iam_service.cache.invalidate_user(user["id"])
    
    return {
        "success": True,
        "message": "Profile removed from group",
        "group_code": group_code
    }


# ============================================================================
# User Assignments
# ============================================================================

@router.post("/users/{user_id}/profiles")
async def assign_profiles_to_user(
    user_id: str,
    assignment: UserProfileAssignment,
    current_user: User = Depends(require_permission("iam.users.assign")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign profiles directly to user"""
    iam_service = IAMService(db)
    
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Handle both single profile_id and multiple profile_ids
    profile_ids = []
    if assignment.profile_id:
        profile_ids = [assignment.profile_id]
    elif assignment.profile_ids:
        profile_ids = assignment.profile_ids
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either profile_id or profile_ids must be provided"
        )
    
    # Verify profiles exist
    for prof_id in profile_ids:
        prof = await db.profiles.find_one({"id": prof_id})
        if not prof:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Profile {prof_id} not found"
            )
    
    success = await iam_service.assign_profiles_to_user(user_id, profile_ids)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to assign profiles")
    
    logger.info(f"Profiles assigned to user {user_id} by {current_user.username}")
    return {"success": True, "message": "Profiles assigned"}


@router.post("/users/{user_id}/groups")
async def assign_groups_to_user(
    user_id: str,
    assignment: UserGroupAssignment,
    current_user: User = Depends(require_permission("iam.users.assign")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign user to groups"""
    iam_service = IAMService(db)
    
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Handle both single group_id and multiple group_ids
    group_ids = []
    if assignment.group_id:
        group_ids = [assignment.group_id]
    elif assignment.group_ids:
        group_ids = assignment.group_ids
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either group_id or group_ids must be provided"
        )
    
    # Verify groups exist
    for group_id in group_ids:
        group = await db.groups.find_one({"id": group_id})
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group {group_id} not found"
            )
    
    success = await iam_service.assign_groups_to_user(user_id, group_ids)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to assign groups")
    
    logger.info(f"Groups assigned to user {user_id} by {current_user.username}")
    return {"success": True, "message": "Groups assigned"}


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all permissions for a user with support for config-driven IAM
    Supports both old format (permission_ids) and new format (permissions codes)
    """
    # Users can only see their own permissions unless admin
    if user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get user
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Collect all permissions from user's profiles
    all_permission_codes = set()
    profile_permissions = []
    
    profile_ids = user.get("profile_ids", []) or user.get("profiles", [])
    
    if profile_ids:
        for profile_id in profile_ids:
            # Find profile by ID or code
            profile_doc = await db.profiles.find_one(
                {"$or": [{"id": profile_id}, {"code": profile_id}]},
                {"_id": 0}
            )
            
            if profile_doc:
                profile_perms = set()
                
                # Add direct permissions
                direct_perms = profile_doc.get("permissions", [])
                if direct_perms == "*":
                    # Wildcard - get all permissions
                    all_perms = await db.permissions.find({}, {"_id": 0, "code": 1}).to_list(1000)
                    profile_perms.update([p["code"] for p in all_perms])
                elif isinstance(direct_perms, list):
                    profile_perms.update(direct_perms)
                
                # Add permissions from bundles
                bundles = profile_doc.get("bundles", [])
                if bundles:
                    # Check permission_bundles collection (config-driven)
                    async for bundle in db.permission_bundles.find(
                        {"code": {"$in": bundles}},
                        {"_id": 0, "permissions": 1}
                    ):
                        bundle_perms = bundle.get("permissions", [])
                        profile_perms.update(bundle_perms)
                    
                    # Check capability_bundles collection (legacy)
                    async for bundle in db.capability_bundles.find(
                        {"$or": [{"id": {"$in": bundles}}, {"code": {"$in": bundles}}]},
                        {"_id": 0, "permissions": 1, "permission_ids": 1}
                    ):
                        if "permissions" in bundle:
                            profile_perms.update(bundle.get("permissions", []))
                        elif "permission_ids" in bundle:
                            # Resolve IDs to codes
                            perm_ids = bundle.get("permission_ids", [])
                            async for perm in db.permissions.find(
                                {"id": {"$in": perm_ids}},
                                {"_id": 0, "code": 1}
                            ):
                                profile_perms.add(perm["code"])
                
                all_permission_codes.update(profile_perms)
                profile_permissions.extend(list(profile_perms))
    
    # Get full permission details
    all_permissions = []
    if all_permission_codes:
        async for perm in db.permissions.find(
            {"code": {"$in": list(all_permission_codes)}},
            {"_id": 0}
        ):
            all_permissions.append(perm)
    
    return {
        "user_id": user_id,
        "total_permissions": len(all_permission_codes),
        "direct_permissions": [],  # Not tracking direct user permissions for now
        "profile_permissions": profile_permissions,
        "all_permissions": all_permissions
    }


@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_permission(
    request: PermissionCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Check if user has specific permission"""
    iam_service = IAMService(db)
    return await iam_service.user_has_permission(
        request.user_id,
        request.permission_code,
        request.resource_id
    )
