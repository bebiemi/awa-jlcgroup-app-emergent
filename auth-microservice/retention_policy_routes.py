"""
Retention Policy Routes - Two-Stage Deletion
Stage 1: Archived → Marked for Deletion (7 days)
Stage 2: Marked for Deletion → Permanently Deleted (3 days)
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import logging
import uuid

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/retention-policy", tags=["retention-policy"])


# ==================== MODELS ====================

class RetentionPolicyConfig(BaseModel):
    """Configuration for retention policy"""
    days_to_mark_for_deletion: int = 7  # Days after archival before marking for deletion
    days_to_permanent_delete: int = 3   # Days after marking before permanent deletion


class RetentionJobResult(BaseModel):
    """Result of a retention policy job execution"""
    marked_for_deletion_count: int
    marked_for_deletion_ids: List[str]
    permanently_deleted_count: int
    permanently_deleted_ids: List[str]
    execution_time: str
    message: str


class RetentionStats(BaseModel):
    """Statistics about users in retention pipeline"""
    archived_users: int
    marked_for_deletion_users: int
    eligible_for_marking: int  # Archived for 7+ days
    eligible_for_deletion: int  # Marked for 3+ days
    config: RetentionPolicyConfig


# ==================== HELPERS ====================

async def get_retention_config(db: AsyncIOMotorDatabase) -> RetentionPolicyConfig:
    """Get retention policy configuration from database or use defaults"""
    setting = await db.app_settings.find_one({"key": "retention_policy_config"})
    
    if setting and setting.get("value"):
        return RetentionPolicyConfig(**setting["value"])
    
    # Default configuration
    return RetentionPolicyConfig()


async def mark_users_for_deletion(db: AsyncIOMotorDatabase, days_threshold: int = 7) -> Dict:
    """
    Find archived users older than threshold and mark them for deletion
    """
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=days_threshold)
    
    # Find users archived for more than threshold days
    eligible_users = await db.users.find({
        "status": "archived",
        "archived_at": {"$lte": cutoff_date}
    }).to_list(length=None)
    
    if not eligible_users:
        return {"count": 0, "user_ids": []}
    
    user_ids = [user["id"] for user in eligible_users]
    
    # Update users to marked_for_deletion status
    result = await db.users.update_many(
        {"id": {"$in": user_ids}},
        {
            "$set": {
                "status": "marked_for_deletion",
                "marked_for_deletion_at": now,
                "deletion_scheduled_at": now + timedelta(days=3),
                "updated_at": now
            }
        }
    )
    
    logger.info(f"Marked {result.modified_count} users for deletion")
    
    return {
        "count": result.modified_count,
        "user_ids": user_ids
    }


async def permanently_delete_users(db: AsyncIOMotorDatabase, days_threshold: int = 3) -> Dict:
    """
    Permanently delete users marked for deletion for more than threshold days
    """
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=days_threshold)
    
    # Find users marked for deletion for more than threshold days
    eligible_users = await db.users.find({
        "status": "marked_for_deletion",
        "marked_for_deletion_at": {"$lte": cutoff_date}
    }).to_list(length=None)
    
    if not eligible_users:
        return {"count": 0, "user_ids": []}
    
    user_ids = [user["id"] for user in eligible_users]
    
    # Store user data for audit before deletion
    for user in eligible_users:
        await db.deleted_users_audit.insert_one({
            "id": str(uuid.uuid4()),
            "original_user_id": user["id"],
            "username": user.get("username"),
            "email": user.get("email"),
            "archived_at": user.get("archived_at"),
            "marked_for_deletion_at": user.get("marked_for_deletion_at"),
            "deletion_executed_at": now,
            "archive_reason": user.get("archive_reason"),
            "roles": user.get("roles", [])
        })
    
    # Permanently delete users
    result = await db.users.delete_many({"id": {"$in": user_ids}})
    
    logger.info(f"Permanently deleted {result.deleted_count} users")
    
    return {
        "count": result.deleted_count,
        "user_ids": user_ids
    }


# ==================== ROUTES ====================

@router.post("/execute", response_model=RetentionJobResult)
async def execute_retention_policy(
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Execute the two-stage retention policy:
    1. Mark archived users (7+ days) for deletion
    2. Permanently delete marked users (3+ days)
    
    Can be called manually or by a scheduled task
    """
    start_time = datetime.now(timezone.utc)
    config = await get_retention_config(db)
    
    # Stage 1: Mark for deletion
    marked_result = await mark_users_for_deletion(
        db, 
        config.days_to_mark_for_deletion
    )
    
    # Stage 2: Permanently delete
    deleted_result = await permanently_delete_users(
        db,
        config.days_to_permanent_delete
    )
    
    # Log audit event
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    actor_username = current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "username", "system")
    
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "retention_policy.execute",
        "actor_id": actor_id,
        "actor_username": actor_username,
        "target_type": "users",
        "target_id": "batch",
        "payload": {
            "marked_for_deletion": marked_result["count"],
            "permanently_deleted": deleted_result["count"],
            "execution_time": start_time.isoformat(),
            "config": config.dict()
        },
        "timestamp": start_time,
        "ip_address": None,
        "user_agent": None
    })
    
    execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    return RetentionJobResult(
        marked_for_deletion_count=marked_result["count"],
        marked_for_deletion_ids=marked_result["user_ids"],
        permanently_deleted_count=deleted_result["count"],
        permanently_deleted_ids=deleted_result["user_ids"],
        execution_time=f"{execution_time:.2f}s",
        message=f"Retention policy executed: {marked_result['count']} marked, {deleted_result['count']} deleted"
    )


@router.get("/stats", response_model=RetentionStats)
async def get_retention_stats(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Get statistics about users in the retention pipeline
    """
    config = await get_retention_config(db)
    now = datetime.now(timezone.utc)
    
    # Count archived users
    archived_count = await db.users.count_documents({"status": "archived"})
    
    # Count marked for deletion users
    marked_count = await db.users.count_documents({"status": "marked_for_deletion"})
    
    # Count archived users eligible for marking (7+ days)
    mark_cutoff = now - timedelta(days=config.days_to_mark_for_deletion)
    eligible_for_marking = await db.users.count_documents({
        "status": "archived",
        "archived_at": {"$lte": mark_cutoff}
    })
    
    # Count marked users eligible for deletion (3+ days)
    delete_cutoff = now - timedelta(days=config.days_to_permanent_delete)
    eligible_for_deletion = await db.users.count_documents({
        "status": "marked_for_deletion",
        "marked_for_deletion_at": {"$lte": delete_cutoff}
    })
    
    return RetentionStats(
        archived_users=archived_count,
        marked_for_deletion_users=marked_count,
        eligible_for_marking=eligible_for_marking,
        eligible_for_deletion=eligible_for_deletion,
        config=config
    )


@router.put("/config", response_model=RetentionPolicyConfig)
async def update_retention_config(
    config: RetentionPolicyConfig,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Update retention policy configuration
    """
    # Validation
    if config.days_to_mark_for_deletion < 1:
        raise HTTPException(status_code=400, detail="Days to mark for deletion must be at least 1")
    
    if config.days_to_permanent_delete < 1:
        raise HTTPException(status_code=400, detail="Days to permanent delete must be at least 1")
    
    now = datetime.now(timezone.utc)
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    # Save configuration
    await db.app_settings.update_one(
        {"key": "retention_policy_config"},
        {
            "$set": {
                "key": "retention_policy_config",
                "value": config.dict(),
                "updated_at": now,
                "updated_by": actor_id
            }
        },
        upsert=True
    )
    
    # Log audit event
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "retention_policy.config_update",
        "actor_id": actor_id,
        "actor_username": current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "username", None),
        "target_type": "config",
        "target_id": "retention_policy",
        "payload": config.dict(),
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Retention policy config updated by {actor_id}")
    
    return config


@router.get("/config", response_model=RetentionPolicyConfig)
async def get_current_config(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Get current retention policy configuration
    """
    return await get_retention_config(db)


from fastapi import HTTPException
