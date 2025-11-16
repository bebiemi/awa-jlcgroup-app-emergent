"""
Background Jobs - Scheduled Tasks
Includes retention policy execution
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)


async def execute_retention_policy_job(db: AsyncIOMotorDatabase):
    """
    Background job to execute retention policy
    Runs daily at 2:00 AM
    """
    try:
        logger.info("🔄 Starting scheduled retention policy execution...")
        start_time = datetime.now(timezone.utc)
        
        # Import the functions from retention_policy_routes
        from retention_policy_routes import (
            mark_users_for_deletion,
            permanently_delete_users,
            get_retention_config
        )
        
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
        await db.audit_events.insert_one({
            "id": str(uuid.uuid4()),
            "action": "retention_policy.scheduled_execution",
            "actor_id": "system",
            "actor_username": "background_job",
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
            "user_agent": "scheduler"
        })
        
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        logger.info(
            f"✅ Retention policy completed: "
            f"{marked_result['count']} marked, "
            f"{deleted_result['count']} deleted "
            f"(took {execution_time:.2f}s)"
        )
        
    except Exception as e:
        logger.error(f"❌ Error executing retention policy: {str(e)}", exc_info=True)


def setup_background_jobs(db: AsyncIOMotorDatabase):
    """
    Setup and start background jobs scheduler
    """
    scheduler = AsyncIOScheduler()
    
    # Schedule retention policy to run daily at 2:00 AM
    scheduler.add_job(
        execute_retention_policy_job,
        CronTrigger(hour=2, minute=0),  # Run at 2:00 AM every day
        args=[db],
        id="retention_policy_job",
        name="Retention Policy Execution",
        replace_existing=True
    )
    
    logger.info("📅 Background jobs scheduled:")
    logger.info("   - Retention Policy: Daily at 2:00 AM")
    
    scheduler.start()
    
    return scheduler
