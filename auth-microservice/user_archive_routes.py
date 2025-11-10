"""
User Archive Routes
Handles soft deletion (archival) and restoration of users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List
import logging

from awana_auth.core.dependencies import get_database
from awana_auth.core.config_manager import get_config
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.core.archive_models import (
    ArchiveUserRequest,
    ArchiveUserResponse,
    RestoreUserRequest,
    RestoreUserResponse,
    PurgeExpiredUsersResponse,
    RetentionConfigResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_retention_days(db: AsyncIOMotorDatabase) -> int:
    """
    Get retention days from database override or YAML config
    Priority: Database > YAML config
    """
    config = get_config()
    
    # Try to get from database first
    setting = await db.app_settings.find_one({"key": "security.user_retention_days"})
    if setting and setting.get("value"):
        return int(setting["value"])
    
    # Fallback to YAML config
    return config.get("security.user_retention.retention_days", 90)


# ==================== ARCHIVE USER ====================

@router.patch("/{user_id}/archive", response_model=ArchiveUserResponse)
async def archive_user(
    user_id: str,
    request: ArchiveUserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Archive a user (soft delete)
    - Sets status to 'archived'
    - Sets archived_at timestamp
    - Calculates deletion_scheduled_at based on retention period
    - Logs action in audit trail
    """
    # Find user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already archived
    if user.get("status") == "archived":
        raise HTTPException(status_code=400, detail="User is already archived")
    
    # Get retention period
    retention_days = await get_retention_days(db)
    
    # Calculate dates
    now = datetime.now(timezone.utc)
    deletion_date = now + timedelta(days=retention_days)
    
    # Update user
    update_data = {
        "status": "archived",
        "archived_at": now,
        "archived_by": current_user["id"],
        "deletion_scheduled_at": deletion_date,
        "archive_reason": request.reason,
        "updated_at": now
    }
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to archive user")
    
    # Log audit event
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "user.archive",
        "actor_id": current_user["id"],
        "actor_username": current_user.get("username"),
        "target_type": "user",
        "target_id": user_id,
        "payload": {
            "reason": request.reason,
            "retention_days": retention_days,
            "deletion_scheduled_at": deletion_date.isoformat()
        },
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"User {user_id} archived by {current_user['id']}, scheduled for deletion on {deletion_date.date()}")
    
    return ArchiveUserResponse(
        user_id=user_id,
        status="archived",
        archived_at=now.isoformat(),
        deletion_scheduled_at=deletion_date.isoformat(),
        retention_days=retention_days,
        message=f"User archived successfully. Permanent deletion scheduled in {retention_days} days."
    )


# ==================== RESTORE USER ====================

@router.patch("/{user_id}/restore", response_model=RestoreUserResponse)
async def restore_user(
    user_id: str,
    request: RestoreUserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Restore an archived user
    - Sets status back to 'active'
    - Clears archived_at, archived_by, deletion_scheduled_at
    - Logs action in audit trail
    """
    # Find user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is archived
    if user.get("status") != "archived":
        raise HTTPException(status_code=400, detail="User is not archived")
    
    # Update user
    now = datetime.now(timezone.utc)
    update_data = {
        "status": "active",
        "archived_at": None,
        "archived_by": None,
        "deletion_scheduled_at": None,
        "archive_reason": None,
        "updated_at": now
    }
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to restore user")
    
    # Log audit event
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "user.restore",
        "actor_id": current_user["id"],
        "actor_username": current_user.get("username"),
        "target_type": "user",
        "target_id": user_id,
        "payload": {
            "reason": request.reason,
            "previous_status": "archived"
        },
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"User {user_id} restored by {current_user['id']}")
    
    return RestoreUserResponse(
        user_id=user_id,
        status="active",
        restored_at=now.isoformat(),
        message="User restored successfully"
    )


# ==================== PURGE EXPIRED USERS ====================

@router.delete("/purge-expired", response_model=PurgeExpiredUsersResponse)
async def purge_expired_users(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Permanently delete users whose deletion_scheduled_at has passed
    This endpoint can be called manually or by a scheduled task
    """
    config = get_config()
    batch_size = config.get("security.user_retention.purge_batch_size", 100)
    
    now = datetime.now(timezone.utc)
    
    # Find expired users
    expired_users = await db.users.find({
        "status": "archived",
        "deletion_scheduled_at": {"$lte": now}
    }).limit(batch_size).to_list(length=batch_size)
    
    if not expired_users:
        return PurgeExpiredUsersResponse(
            purged_count=0,
            purged_user_ids=[],
            message="No expired users to purge"
        )
    
    user_ids = [user["id"] for user in expired_users]
    
    # Delete users permanently
    result = await db.users.delete_many({
        "id": {"$in": user_ids}
    })
    
    # Log audit event for batch deletion
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "user.purge_expired",
        "actor_id": current_user["id"],
        "actor_username": current_user.get("username"),
        "target_type": "user",
        "target_id": "batch",
        "payload": {
            "purged_count": result.deleted_count,
            "user_ids": user_ids
        },
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Purged {result.deleted_count} expired users by {current_user['id']}")
    
    return PurgeExpiredUsersResponse(
        purged_count=result.deleted_count,
        purged_user_ids=user_ids,
        message=f"Successfully purged {result.deleted_count} expired users"
    )


# ==================== GET RETENTION CONFIG ====================

@router.get("/retention-config", response_model=RetentionConfigResponse)
async def get_retention_config(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Get current retention configuration
    Shows if value comes from database or YAML
    """
    config = get_config()
    yaml_days = config.get("security.user_retention.retention_days", 90)
    
    # Check if database override exists
    setting = await db.app_settings.find_one({"key": "security.user_retention_days"})
    
    if setting and setting.get("value"):
        return RetentionConfigResponse(
            retention_days=int(setting["value"]),
            source="database",
            can_override=config.get("security.user_retention.allow_override", True)
        )
    
    return RetentionConfigResponse(
        retention_days=yaml_days,
        source="yaml",
        can_override=config.get("security.user_retention.allow_override", True)
    )


# ==================== UPDATE RETENTION CONFIG ====================

@router.put("/retention-config")
async def update_retention_config(
    retention_days: int,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.ADMIN_SETTINGS))
):
    """
    Update retention period (creates/updates database override)
    """
    config = get_config()
    
    if not config.get("security.user_retention.allow_override", True):
        raise HTTPException(
            status_code=403,
            detail="Retention period override is not allowed by configuration"
        )
    
    if retention_days < 1:
        raise HTTPException(status_code=400, detail="Retention days must be at least 1")
    
    if retention_days > 365:
        raise HTTPException(status_code=400, detail="Retention days cannot exceed 365")
    
    now = datetime.now(timezone.utc)
    
    # Upsert setting in database
    await db.app_settings.update_one(
        {"key": "security.user_retention_days"},
        {
            "$set": {
                "key": "security.user_retention_days",
                "value": retention_days,
                "updated_at": now,
                "updated_by": current_user["id"]
            }
        },
        upsert=True
    )
    
    # Log audit event
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "config.update_retention",
        "actor_id": current_user["id"],
        "actor_username": current_user.get("username"),
        "target_type": "setting",
        "target_id": "security.user_retention_days",
        "payload": {
            "new_value": retention_days
        },
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Retention period updated to {retention_days} days by {current_user['id']}")
    
    return {
        "message": "Retention period updated successfully",
        "retention_days": retention_days,
        "source": "database"
    }


import uuid
