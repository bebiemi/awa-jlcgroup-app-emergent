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


async def execute_retention_workflow_job(db: AsyncIOMotorDatabase):
    """
    Background job to execute retention workflow
    Runs daily at 2:00 AM
    Gère tout le cycle de vie: J-7, J-3, J, J+3
    """
    try:
        from awana_auth.services.retention_workflow_service import RetentionWorkflowService
        
        workflow_service = RetentionWorkflowService(db)
        results = await workflow_service.execute_full_workflow()
        
        if results.get("status") == "success":
            summary = results.get("summary", {})
            logger.info(
                f"✅ Scheduled retention workflow completed: "
                f"{summary.get('total_users_processed', 0)} processed, "
                f"{summary.get('total_notifications_sent', 0)} notifications sent, "
                f"{summary.get('total_permanently_deleted', 0)} permanently deleted"
            )
        else:
            logger.error(f"❌ Retention workflow failed: {results.get('error')}")
        
    except Exception as e:
        logger.error(f"❌ Error executing retention workflow: {str(e)}", exc_info=True)


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
