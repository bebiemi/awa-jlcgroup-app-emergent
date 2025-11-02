"""Notification repository"""
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.domain.entities.notification import Notification, NotificationChannel
from datetime import datetime


class NotificationRepository:
    """Repository for notification operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.notifications

    async def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        notification_dict = notification.dict()
        notification_dict['created_at'] = notification.created_at.isoformat()
        if notification.read_at:
            notification_dict['read_at'] = notification.read_at.isoformat()
        
        await self.collection.insert_one(notification_dict)
        return notification

    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        doc = await self.collection.find_one({"id": notification_id}, {"_id": 0})
        if not doc:
            return None
        
        if 'created_at' in doc and isinstance(doc['created_at'], str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if 'read_at' in doc and doc['read_at'] and isinstance(doc['read_at'], str):
            doc['read_at'] = datetime.fromisoformat(doc['read_at'])
        
        return Notification(**doc)

    async def list_by_user(
        self,
        user_id: str,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Notification], int, int]:
        """List notifications for a user"""
        query = {"user_id": user_id}
        if is_read is not None:
            query["is_read"] = is_read
        
        # Get total and unread count
        total = await self.collection.count_documents({"user_id": user_id})
        unread_count = await self.collection.count_documents({"user_id": user_id, "is_read": False})
        
        # Get paginated results
        cursor = self.collection.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=None)
        
        notifications = []
        for doc in docs:
            if 'created_at' in doc and isinstance(doc['created_at'], str):
                doc['created_at'] = datetime.fromisoformat(doc['created_at'])
            if 'read_at' in doc and doc['read_at'] and isinstance(doc['read_at'], str):
                doc['read_at'] = datetime.fromisoformat(doc['read_at'])
            notifications.append(Notification(**doc))
        
        return notifications, total, unread_count

    async def mark_as_read(self, notification_ids: List[str]) -> int:
        """Mark notifications as read"""
        result = await self.collection.update_many(
            {"id": {"$in": notification_ids}},
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.utcnow().isoformat()
                }
            }
        )
        return result.modified_count

    async def delete_old(
        self,
        user_id: str,
        days: int = 30
    ) -> int:
        """Delete old read notifications"""
        cutoff_date = datetime.utcnow()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        result = await self.collection.delete_many({
            "user_id": user_id,
            "is_read": True,
            "created_at": {"$lt": cutoff_date.isoformat()}
        })
        return result.deleted_count
