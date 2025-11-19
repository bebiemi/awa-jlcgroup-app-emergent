"""
User Detail Routes
Extended user management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone
import os

from awana_auth.core.user_detail_models import (
    UserDocument,
    UserDocumentCreate,
    UserActivity,
    UserDetailResponse,
    GroupAssignment,
    ProfileAssignment,
    NotificationRequest,
    ActivityResponse,
)
from awana_auth.core.models import User
from awana_auth.core.dependencies import get_database
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.dependencies.permission_dependencies import require_permission

router = APIRouter()


# Helper function to convert datetime to ISO string
def datetime_to_str(value):
    """Convert datetime object to ISO format string"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return str(value)


# ==================== USER DETAIL ====================

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """Get detailed user information"""
    # Find user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user groups
    groups = []
    if user.get("group_ids"):
        groups_cursor = db.groups.find({"id": {"$in": user.get("group_ids", [])}})
        groups_raw = await groups_cursor.to_list(length=None)
        # Remove MongoDB _id field
        for group in groups_raw:
            if "_id" in group:
                del group["_id"]
        groups = groups_raw
    
    # Get user profiles
    profiles = []
    if user.get("profile_ids"):
        profiles_cursor = db.profiles.find({"id": {"$in": user.get("profile_ids", [])}})
        profiles_raw = await profiles_cursor.to_list(length=None)
        # Remove MongoDB _id field
        for profile in profiles_raw:
            if "_id" in profile:
                del profile["_id"]
        profiles = profiles_raw
    
    # Get user permissions (from profiles)
    permissions = set()
    for profile in profiles:
        permissions.update(profile.get("permission_ids", []))
    
    # Get permission codes
    permission_codes = []
    if permissions:
        perms_cursor = db.permissions.find({"id": {"$in": list(permissions)}})
        perms_list = await perms_cursor.to_list(length=None)
        permission_codes = [p.get("code") for p in perms_list if p.get("code")]
    
    return UserDetailResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        provider=user.get("provider", "local"),
        status=user.get("status", "active"),
        roles=user.get("roles", []),
        groups=groups,
        profiles=profiles,
        permissions=permission_codes,
        mfa_enabled=user.get("mfa_enabled", False),
        mfa_method=user.get("mfa_method"),
        is_verified=user.get("is_verified", False),  # Email verification status
        phone=user.get("phone"),
        location=user.get("location"),
        location_label=user.get("location_label"),
        created_at=datetime_to_str(user.get("created_at")) or datetime.now(timezone.utc).isoformat(),
        updated_at=datetime_to_str(user.get("updated_at")) or datetime.now(timezone.utc).isoformat(),
        last_login_at=datetime_to_str(user.get("last_login_at")),
        last_activity_at=datetime_to_str(user.get("last_activity_at")),
        login_count=user.get("login_count", 0),
        failed_login_attempts=user.get("failed_login_attempts", 0),
        metadata=user.get("metadata", {})
    )


# ==================== DOCUMENTS ====================

@router.get("/{user_id}/documents", response_model=List[UserDocument])
async def list_user_documents(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """List user documents"""
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get documents
    cursor = db.user_documents.find({"user_id": user_id})
    documents = await cursor.to_list(length=None)
    
    return [UserDocument(**doc) for doc in documents]


@router.patch("/{user_id}/documents/{doc_id}/verify")
async def verify_document(
    user_id: str,
    doc_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Verify a user document"""
    # Find document
    doc = await db.user_documents.find_one({"id": doc_id, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update document
    await db.user_documents.update_one(
        {"id": doc_id},
        {
            "$set": {
                "verified": True,
                "verified_by": current_user.id if hasattr(current_user, "id") else current_user.get("id", "unknown"),
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="document_verified",
        resource_type="document",
        resource_id=doc_id,
        metadata={"verified_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "Document verified successfully"}


@router.delete("/{user_id}/documents/{doc_id}")
async def delete_document(
    user_id: str,
    doc_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Delete a user document"""
    # Find document
    doc = await db.user_documents.find_one({"id": doc_id, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete document
    await db.user_documents.delete_one({"id": doc_id})
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="document_deleted",
        resource_type="document",
        resource_id=doc_id,
        metadata={"deleted_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown"), "document_type": doc.get("type")}
    )
    
    return {"success": True, "message": "Document deleted successfully"}


@router.post("/{user_id}/documents", response_model=UserDocument)
async def upload_document(
    user_id: str,
    file: UploadFile = File(...),
    document_type: str = "other",
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Upload a document for user"""
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create document record (for now, just store metadata - file storage to be implemented)
    doc_id = str(uuid.uuid4())
    document = {
        "id": doc_id,
        "user_id": user_id,
        "type": document_type,
        "name": file.filename,
        "file_name": file.filename,
        "file_size": 0,  # TODO: Get actual file size
        "mime_type": file.content_type or "application/octet-stream",
        "url": f"/documents/{doc_id}",  # TODO: Actual file storage
        "verified": False,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {"uploaded_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    }
    
    await db.user_documents.insert_one(document)
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="document_uploaded",
        resource_type="document",
        resource_id=doc_id,
        metadata={"document_type": document_type, "file_name": file.filename}
    )
    
    return UserDocument(**document)


# ==================== GROUPS ====================

@router.get("/{user_id}/groups")
async def get_user_groups(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """Get user groups"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    group_ids = user.get("group_ids", [])
    if not group_ids:
        return []
    
    cursor = db.groups.find({"id": {"$in": group_ids}})
    groups = await cursor.to_list(length=None)
    
    # Remove MongoDB _id field from each group
    for group in groups:
        if "_id" in group:
            del group["_id"]
    
    return groups


@router.post("/{user_id}/groups")
async def assign_group(
    user_id: str,
    assignment: GroupAssignment,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Assign a group to user"""
    # Verify user and group exist
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    group = await db.groups.find_one({"id": assignment.group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Add group to user
    current_groups = user.get("group_ids", [])
    if assignment.group_id not in current_groups:
        current_groups.append(assignment.group_id)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"group_ids": current_groups, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="group_assigned",
        resource_type="group",
        resource_id=assignment.group_id,
        metadata={"group_name": group.get("name"), "assigned_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "Group assigned successfully"}


@router.delete("/{user_id}/groups/{group_id}")
async def remove_group(
    user_id: str,
    group_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Remove a group from user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove group from user
    current_groups = user.get("group_ids", [])
    if group_id in current_groups:
        current_groups.remove(group_id)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"group_ids": current_groups, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="group_removed",
        resource_type="group",
        resource_id=group_id,
        metadata={"removed_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "Group removed successfully"}


# ==================== PROFILES ====================

@router.get("/{user_id}/profiles")
async def get_user_profiles(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """Get user profiles"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_ids = user.get("profile_ids", [])
    if not profile_ids:
        return []
    
    cursor = db.profiles.find({"id": {"$in": profile_ids}})
    profiles = await cursor.to_list(length=None)
    
    # Remove MongoDB _id field from each profile
    for profile in profiles:
        if "_id" in profile:
            del profile["_id"]
    
    return profiles


@router.post("/{user_id}/profiles")
async def assign_profile(
    user_id: str,
    assignment: ProfileAssignment,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Assign a profile to user"""
    # Verify user and profile exist
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = await db.profiles.find_one({"id": assignment.profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Add profile to user
    current_profiles = user.get("profile_ids", [])
    if assignment.profile_id not in current_profiles:
        current_profiles.append(assignment.profile_id)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"profile_ids": current_profiles, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="profile_assigned",
        resource_type="profile",
        resource_id=assignment.profile_id,
        metadata={"profile_name": profile.get("name"), "assigned_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "Profile assigned successfully"}


@router.delete("/{user_id}/profiles/{profile_id}")
async def remove_profile(
    user_id: str,
    profile_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Remove a profile from user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove profile from user
    current_profiles = user.get("profile_ids", [])
    if profile_id in current_profiles:
        current_profiles.remove(profile_id)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"profile_ids": current_profiles, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="profile_removed",
        resource_type="profile",
        resource_id=profile_id,
        metadata={"removed_by": current_user.username if hasattr(current_user, 'username') else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "Profile removed successfully"}


# ==================== ACTIVITY ====================

@router.get("/{user_id}/activity", response_model=ActivityResponse)
async def get_user_activity(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """Get user activity log"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get total count
    total = await db.user_activity.count_documents({"user_id": user_id})
    
    # Get paginated activities
    skip = (page - 1) * page_size
    cursor = db.user_activity.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(page_size)
    activities = await cursor.to_list(length=page_size)
    
    return ActivityResponse(
        activities=[UserActivity(**act) for act in activities],
        total=total,
        page=page,
        page_size=page_size
    )


# ==================== ACTIONS ====================

@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Reset user password"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # TODO: Implement password reset logic (send email, generate temp password, etc.)
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="password_reset",
        metadata={"reset_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "Password reset initiated"}


class AdminPasswordUpdateRequest(BaseModel):
    """Request model for admin password update"""
    new_password: str
    confirm_password: str


@router.post("/{user_id}/password/admin-update")
async def admin_update_password(
    user_id: str,
    password_data: AdminPasswordUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission(IAMPermissions.USERS_PASSWORD_UPDATE))
):
    """
    Admin/SuperAdmin updates user password
    
    Security checks:
    - Requires users.password.update permission
    - Prevents privilege escalation
    - Logs all password changes for audit
    """
    import bcrypt
    from datetime import datetime, timezone
    
    # Validate passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les mots de passe ne correspondent pas"
        )
    
    # Validate password strength
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins 8 caractères"
        )
    
    # Get target user
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Security: Prevent privilege escalation
    # Check if target user has higher privileges than current user
    target_roles = set(target_user.get("roles", []))
    current_roles = set(current_user.roles)
    
    # Define role hierarchy (higher value = higher privilege)
    role_hierarchy = {
        "super_admin": 100,
        "admin": 50,
        "company": 10,
        "interim": 5,
        "candidat": 5,
        "collaborator": 5,
    }
    
    # Get max privilege level for both users
    target_max_level = max([role_hierarchy.get(r, 0) for r in target_roles], default=0)
    current_max_level = max([role_hierarchy.get(r, 0) for r in current_roles], default=0)
    
    # Prevent changing password of user with equal or higher privilege
    if target_max_level >= current_max_level and target_user["id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas modifier le mot de passe d'un utilisateur avec des privilèges égaux ou supérieurs"
        )
    
    # Hash new password
    password_hash = bcrypt.hashpw(
        password_data.new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Update password
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "password_hash": password_hash,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log activity for audit
    await log_activity(
        db,
        user_id=user_id,
        action="admin_password_update",
        metadata={
            "updated_by": current_user.username,
            "updated_by_id": current_user.id,
            "target_user": target_user.get("username"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    return {
        "success": True,
        "message": f"Mot de passe mis à jour avec succès pour {target_user.get('username')}"
    }


@router.post("/{user_id}/reset-mfa")
async def reset_mfa(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Reset user MFA"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Disable MFA
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "mfa_enabled": False,
                "mfa_secret": None,
                "mfa_method": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="mfa_reset",
        metadata={"reset_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown")}
    )
    
    return {"success": True, "message": "MFA reset successfully"}


@router.post("/{user_id}/notify")
async def send_notification(
    user_id: str,
    notification: NotificationRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """Send notification to user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # TODO: Implement notification sending (email, in-app, etc.)
    
    # Log activity
    await log_activity(
        db,
        user_id=user_id,
        action="notification_sent",
        metadata={
            "sent_by": current_user.username if hasattr(current_user, "username") else current_user.get("username", "unknown"),
            "title": notification.title,
            "type": notification.type
        }
    )
    
    return {"success": True, "message": "Notification sent successfully"}


# ==================== HELPER FUNCTIONS ====================

async def log_activity(
    db: AsyncIOMotorDatabase,
    user_id: str,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """Log user activity"""
    activity = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_activity.insert_one(activity)
