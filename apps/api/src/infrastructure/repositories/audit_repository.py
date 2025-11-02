"""Audit trail repository"""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.domain.entities.audit import AuditTrail
from datetime import datetime


class AuditRepository:
    """Repository for audit trail operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.audit_trail

    async def create(self, audit: AuditTrail) -> AuditTrail:
        """Create a new audit entry"""
        audit_dict = audit.dict()
        audit_dict['created_at'] = audit.created_at.isoformat()
        await self.collection.insert_one(audit_dict)
        return audit

    async def list_by_entity(
        self,
        entity: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[AuditTrail]:
        """List audit entries for an entity"""
        cursor = self.collection.find(
            {"entity": entity, "entity_id": entity_id},
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        docs = await cursor.to_list(length=None)
        audits = []
        for doc in docs:
            if 'created_at' in doc and isinstance(doc['created_at'], str):
                doc['created_at'] = datetime.fromisoformat(doc['created_at'])
            audits.append(AuditTrail(**doc))
        
        return audits

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[AuditTrail]:
        """List audit entries by user"""
        cursor = self.collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        docs = await cursor.to_list(length=None)
        audits = []
        for doc in docs:
            if 'created_at' in doc and isinstance(doc['created_at'], str):
                doc['created_at'] = datetime.fromisoformat(doc['created_at'])
            audits.append(AuditTrail(**doc))
        
        return audits
