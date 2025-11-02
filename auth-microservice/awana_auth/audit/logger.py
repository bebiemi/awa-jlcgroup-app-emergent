"""
Audit logger implementation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from .models import AuditLog, AuditAction
from ..core.config import AuthConfig
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """Manages audit logging"""
    
    def __init__(self, db: AsyncIOMotorDatabase, config: AuthConfig):
        self.db = db
        self.config = config
        self.audit_logs_collection = db.audit_logs
        self.enabled = config.audit_log_enabled
    
    async def log(
        self,
        action: AuditAction,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        target_id: Optional[str] = None,
        target_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an audit event"""
        if not self.enabled:
            return
        
        audit_log = AuditLog(
            action=action,
            actor_id=actor_id,
            actor_email=actor_email,
            target_id=target_id,
            target_email=target_email,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        try:
            await self.audit_logs_collection.insert_one(audit_log.model_dump())
            logger.debug(f"Audit log created: {action.value} by {actor_email or 'system'}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    async def get_logs(
        self,
        limit: int = 100,
        skip: int = 0,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Query audit logs with filters"""
        query = {}
        
        if actor_id:
            query["actor_id"] = actor_id
        
        if target_id:
            query["target_id"] = target_id
        
        if action:
            query["action"] = action.value
        
        if resource_type:
            query["resource_type"] = resource_type
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date.isoformat()
            if end_date:
                query["timestamp"]["$lte"] = end_date.isoformat()
        
        logs_docs = await self.audit_logs_collection.find(query) \
            .sort("timestamp", -1) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=None)
        
        return [AuditLog(**doc) for doc in logs_docs]
    
    async def cleanup_old_logs(self):
        """Remove old audit logs based on retention policy"""
        if not self.enabled:
            return
        
        retention_days = self.config.audit_log_retention_days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        result = await self.audit_logs_collection.delete_many({
            "timestamp": {"$lt": cutoff_date.isoformat()}
        })
        
        if result.deleted_count > 0:
            logger.info(f"Cleaned up {result.deleted_count} old audit logs")
