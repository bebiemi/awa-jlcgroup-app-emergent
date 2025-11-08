"""
Security Management Routes - Permissions, Profiles, Groups
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
import secrets
import string

from awana_auth.core.models import (
    Permission, Profile, Group, 
    CreateUserRequest, CreateGroupRequest, CreateProfileRequest,
    User, UserStatus, AuthProvider
)
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.config import auth_config

security_router = APIRouter(prefix="/auth/security", tags=["security"])


# ===== Permissions Endpoints =====

@security_router.get("/permissions", response_model=List[Permission])
async def get_permissions(
    module: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Get all permissions, optionally filtered by module"""
    query = {}
    if module:
        query["module"] = module
    
    permissions = await db.permissions.find(query).to_list(length=None)
    return [Permission(**perm) for perm in permissions]


# ===== Profiles Endpoints =====

@security_router.get("/profiles", response_model=List[Profile])
async def get_profiles(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Get all profiles"""
    profiles = await db.profiles.find().to_list(length=None)
    return [Profile(**profile) for profile in profiles]


@security_router.get("/profiles/{profile_id}", response_model=Profile)
async def get_profile(
    profile_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Get a specific profile"""
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return Profile(**profile)


@security_router.post("/profiles", response_model=Profile)
async def create_profile(
    request: CreateProfileRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Create a new profile"""
    # Check if profile name already exists
    existing = await db.profiles.find_one({"name": request.name})
    if existing:
        raise HTTPException(status_code=400, detail="Profile name already exists")
    
    profile = Profile(
        name=request.name,
        description=request.description,
        permissions=request.permissions,
        is_system=False,
        created_by=current_user.id
    )
    
    await db.profiles.insert_one(profile.model_dump())
    return profile


@security_router.put("/profiles/{profile_id}", response_model=Profile)
async def update_profile(
    profile_id: str,
    request: CreateProfileRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Update a profile"""
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Cannot modify system profiles
    if profile.get("is_system"):
        raise HTTPException(status_code=403, detail="Cannot modify system profiles")
    
    update_data = {
        "name": request.name,
        "description": request.description,
        "permissions": request.permissions,
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.profiles.update_one({"id": profile_id}, {"$set": update_data})
    updated = await db.profiles.find_one({"id": profile_id})
    return Profile(**updated)


@security_router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Delete a profile"""
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Cannot delete system profiles
    if profile.get("is_system"):
        raise HTTPException(status_code=403, detail="Cannot delete system profiles")
    
    # Check if profile is assigned to any groups
    groups_with_profile = await db.groups.count_documents({"profile_id": profile_id})
    if groups_with_profile > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete profile: assigned to {groups_with_profile} group(s)"
        )
    
    await db.profiles.delete_one({"id": profile_id})
    return {"message": "Profile deleted successfully"}


# ===== Groups Endpoints =====

@security_router.get("/groups", response_model=List[Group])
async def get_groups(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Get all groups"""
    groups = await db.groups.find().to_list(length=None)
    return [Group(**group) for group in groups]


@security_router.get("/groups/{group_id}", response_model=Group)
async def get_group(
    group_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Get a specific group"""
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return Group(**group)


@security_router.post("/groups", response_model=Group)
async def create_group(
    request: CreateGroupRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Create a new group"""
    # Check if group name already exists
    existing = await db.groups.find_one({"name": request.name})
    if existing:
        raise HTTPException(status_code=400, detail="Group name already exists")
    
    # Verify profile exists if provided
    if request.profile_id:
        profile = await db.profiles.find_one({"id": request.profile_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    
    group = Group(
        name=request.name,
        description=request.description,
        profile_id=request.profile_id,
        member_ids=request.member_ids,
        created_by=current_user.id
    )
    
    await db.groups.insert_one(group.model_dump())
    return group


@security_router.put("/groups/{group_id}", response_model=Group)
async def update_group(
    group_id: str,
    request: CreateGroupRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Update a group"""
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify profile exists if provided
    if request.profile_id:
        profile = await db.profiles.find_one({"id": request.profile_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = {
        "name": request.name,
        "description": request.description,
        "profile_id": request.profile_id,
        "member_ids": request.member_ids,
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.groups.update_one({"id": group_id}, {"$set": update_data})
    updated = await db.groups.find_one({"id": group_id})
    return Group(**updated)


@security_router.delete("/groups/{group_id}")
async def delete_group(
    group_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Delete a group"""
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    await db.groups.delete_one({"id": group_id})
    return {"message": "Group deleted successfully"}


@security_router.post("/groups/{group_id}/members/{user_id}")
async def add_member_to_group(
    group_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Add a user to a group"""
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add user to group if not already member
    if user_id not in group.get("member_ids", []):
        await db.groups.update_one(
            {"id": group_id},
            {"$addToSet": {"member_ids": user_id}, "$set": {"updated_at": datetime.now(timezone.utc)}}
        )
    
    return {"message": "User added to group successfully"}


@security_router.delete("/groups/{group_id}/members/{user_id}")
async def remove_member_from_group(
    group_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Remove a user from a group"""
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    await db.groups.update_one(
        {"id": group_id},
        {"$pull": {"member_ids": user_id}, "$set": {"updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "User removed from group successfully"}


# ===== User Creation Endpoint =====

def generate_password(length: int = 12) -> str:
    """Generate a random secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@security_router.post("/users", response_model=User)
async def create_user(
    request: CreateUserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("users.manage"))
):
    """Create a new user"""
    from awana_auth.security.password import PasswordManager
    
    # Check if email already exists
    existing = await db.users.find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate username from email if not provided
    username = request.username or request.email.split('@')[0]
    
    # Check if username already exists
    existing_username = await db.users.find_one({"username": username})
    if existing_username:
        # Append random suffix
        username = f"{username}_{secrets.token_hex(3)}"
    
    # Generate password if not provided
    password = request.password or generate_password()
    hasher = PasswordManager(auth_config)
    hashed_password = hasher.hash_password(password)
    
    # Create user
    new_user = User(
        username=username,
        email=request.email,
        full_name=request.full_name,
        provider=AuthProvider.LOCAL,
        status=UserStatus.ACTIVE,
        is_verified=True,
        roles=request.roles
    )
    
    user_data = new_user.model_dump()
    user_data["password_hash"] = hashed_password
    user_data["group_ids"] = request.group_ids
    user_data["profile_id"] = request.profile_id
    
    await db.users.insert_one(user_data)
    
    # TODO: Send email with credentials if send_invitation is True
    # For now, we'll just return the user
    # In production, integrate with email service
    
    return new_user
