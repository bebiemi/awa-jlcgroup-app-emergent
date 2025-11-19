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
        permissions.append(Permission(**perm))
    
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
        
        capability_bundle_ids = profile_data.get("capability_bundle_ids", [])
        if capability_bundle_ids:
            # Récupérer les permissions de tous les bundles
            bundle_perms = set()
            async for bundle in bundles_collection.find(
                {"id": {"$in": capability_bundle_ids}},
                {"_id": 0, "permission_ids": 1}
            ):
                bundle_perms.update(bundle.get("permission_ids", []))
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
    """
    profiles_collection = db.profiles
    
    profile = await profiles_collection.find_one({"id": profile_id}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Permissions directes
    direct_permission_ids = set(profile.get("permission_ids", []))
    
    # Permissions des bundles
    bundle_permission_ids = set()
    capability_bundle_ids = profile.get("capability_bundle_ids", [])
    
    if capability_bundle_ids:
        bundles_collection = db.capability_bundles
        async for bundle in bundles_collection.find(
            {"id": {"$in": capability_bundle_ids}},
            {"_id": 0, "permission_ids": 1}
        ):
            bundle_permission_ids.update(bundle.get("permission_ids", []))
    
    # Toutes les permissions effectives (union)
    all_permission_ids = direct_permission_ids | bundle_permission_ids
    
    # Récupérer les détails des permissions
    permissions_collection = db.permissions
    permissions = []
    if all_permission_ids:
        async for perm in permissions_collection.find(
            {"id": {"$in": list(all_permission_ids)}},
            {"_id": 0}
        ):
            permissions.append(perm)
    
    return {
        "profile_id": profile_id,
        "profile_code": profile.get("code"),
        "profile_name": profile.get("name"),
        "direct_permission_count": len(direct_permission_ids),
        "bundle_permission_count": len(bundle_permission_ids),
        "total_effective_permissions": len(all_permission_ids),
        "permissions": permissions,
        "capability_bundle_ids": capability_bundle_ids
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
    from bson import ObjectId
    groups_collection = db.groups
    profiles_collection = db.profiles
    
    # Verify group exists (groups use MongoDB _id, not custom id field)
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
    except:
        # If not valid ObjectId, try with code field
        group = await groups_collection.find_one({"code": group_id})
    
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
    
    # Assign profile to group (use iam_role_ids field as groups don't have profile_ids)
    result = await groups_collection.update_one(
        {"_id": group["_id"]},
        {"$addToSet": {"iam_role_ids": profile_id}}
    )
    
    logger.info(f"Profile {profile_id} assigned to group {group_id} by {current_user.username}")
    
    # Invalidate cache for all users in the group
    iam_service = IAMService(db)
    user_ids = group.get("user_ids", [])
    for user_id in user_ids:
        await iam_service.cache.invalidate_user(user_id)
    
    return {
        "success": True,
        "message": f"Profile '{profile['name']}' assigned to group '{group['name']}'",
        "users_affected": len(user_ids)
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
    
    # Verify group exists
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if protected
    if group.get("is_protected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify protected group"
        )
    
    # Remove profile from group
    result = await groups_collection.update_one(
        {"id": group_id},
        {"$pull": {"profile_ids": profile_id}}
    )
    
    logger.info(f"Profile {profile_id} removed from group {group_id} by {current_user.username}")
    
    # Invalidate cache for all users in the group
    iam_service = IAMService(db)
    user_ids = group.get("user_ids", [])
    for user_id in user_ids:
        await iam_service.cache.invalidate_user(user_id)
    
    return {
        "success": True,
        "message": "Profile removed from group",
        "users_affected": len(user_ids)
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


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all permissions for a user"""
    # Users can only see their own permissions unless admin
    if user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    iam_service = IAMService(db)
    return await iam_service.get_user_permissions(user_id)


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
