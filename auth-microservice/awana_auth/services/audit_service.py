"""
Audit Service
Centralized service for logging all audit events
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from awana_auth.core.audit_models import (
    AuditAction,
    AuditSeverity,
    AuditEventCreate,
)


class AuditService:
    """Service for managing audit events"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.audit_events
    
    async def log_event(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        description: str,
        entity_label: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Log an audit event
        
        Args:
            action: Type of action performed
            entity_type: Type of entity (besoin, mission, user, etc.)
            entity_id: ID of the entity
            actor_id: ID of the user performing the action
            actor_name: Name of the actor
            actor_role: Role of the actor
            description: Human-readable description
            entity_label: Optional human-readable identifier
            severity: Severity level
            metadata: Additional context
            changes: Before/after values
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            ID of the created audit event
        """
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        event_doc = {
            "id": event_id,
            "action": action.value,
            "severity": severity.value,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_label": entity_label,
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_role": actor_role,
            "actor_type": "user",  # Could be "system" for automated actions
            "description": description,
            "metadata": metadata or {},
            "changes": changes,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now,
        }
        
        await self.collection.insert_one(event_doc)
        return event_id
    
    async def log_status_change(
        self,
        entity_type: str,
        entity_id: str,
        entity_label: str,
        from_status: Optional[str],
        to_status: str,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        comment: Optional[str] = None,
    ) -> str:
        """
        Log a status change (common pattern)
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            entity_label: Human-readable label
            from_status: Previous status
            to_status: New status
            actor_id: Actor ID
            actor_name: Actor name
            actor_role: Actor role
            comment: Optional comment
        
        Returns:
            Audit event ID
        """
        description = f"Statut changé: {from_status or 'Aucun'} → {to_status}"
        if comment:
            description += f" (Commentaire: {comment[:100]})"
        
        return await self.log_event(
            action=AuditAction.BESOIN_UPDATED if entity_type == "besoin" else AuditAction.MISSION_UPDATED,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_label=entity_label,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            description=description,
            metadata={
                "action_type": "status_change",
                "from_status": from_status,
                "to_status": to_status,
                "comment": comment,
            },
            changes={
                "status": {
                    "from": from_status,
                    "to": to_status,
                }
            },
        )
    
    async def get_entity_audit_trail(
        self,
        entity_type: str,
        entity_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Get audit trail for a specific entity
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            page: Page number
            page_size: Items per page
        
        Returns:
            Paginated audit events
        """
        query = {
            "entity_type": entity_type,
            "entity_id": entity_id,
        }
        
        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        events = await cursor.to_list(length=page_size)
        
        # Remove MongoDB _id
        for event in events:
            event.pop("_id", None)
        
        return {
            "items": events,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    
    async def search_audit_events(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Search audit events with filters
        
        Returns:
            Paginated audit events
        """
        query = {}
        
        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if actor_id:
            query["actor_id"] = actor_id
        if action:
            query["action"] = action
        if severity:
            query["severity"] = severity
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        events = await cursor.to_list(length=page_size)
        
        # Remove MongoDB _id
        for event in events:
            event.pop("_id", None)
        
        return {
            "items": events,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    
    async def ensure_indexes(self):
        """Create necessary indexes for audit_events collection"""
        await self.collection.create_index("entity_type")
        await self.collection.create_index("entity_id")
        await self.collection.create_index([("entity_type", 1), ("entity_id", 1)])
        await self.collection.create_index("actor_id")
        await self.collection.create_index("action")
        await self.collection.create_index("created_at")
        await self.collection.create_index([("entity_type", 1), ("created_at", -1)])
