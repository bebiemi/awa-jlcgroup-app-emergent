"""
Session Storage - MongoDB implementation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.models import Session, User
from ..core.config import AuthConfig
import logging

logger = logging.getLogger(__name__)


def ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (UTC)"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def parse_session_from_mongo(session_doc: dict) -> Session:
    """Parse session document from MongoDB, ensuring datetime fields are timezone-aware"""
    # Convert ISO string datetimes to timezone-aware datetime objects
    if isinstance(session_doc.get('created_at'), str):
        session_doc['created_at'] = datetime.fromisoformat(session_doc['created_at'].replace('Z', '+00:00'))
    if isinstance(session_doc.get('expires_at'), str):
        session_doc['expires_at'] = datetime.fromisoformat(session_doc['expires_at'].replace('Z', '+00:00'))
    if isinstance(session_doc.get('last_activity_at'), str):
        session_doc['last_activity_at'] = datetime.fromisoformat(session_doc['last_activity_at'].replace('Z', '+00:00'))
    
    # Ensure all datetime fields are timezone-aware
    if 'created_at' in session_doc and session_doc['created_at']:
        session_doc['created_at'] = ensure_timezone_aware(session_doc['created_at'])
    if 'expires_at' in session_doc and session_doc['expires_at']:
        session_doc['expires_at'] = ensure_timezone_aware(session_doc['expires_at'])
    if 'last_activity_at' in session_doc and session_doc['last_activity_at']:
        session_doc['last_activity_at'] = ensure_timezone_aware(session_doc['last_activity_at'])
    
    return Session(**session_doc)


class SessionStorage:
    """Manages user sessions in MongoDB"""
    
    def __init__(self, db: AsyncIOMotorDatabase, config: AuthConfig):
        self.db = db
        self.config = config
        self.sessions_collection = db.sessions
        self.max_age = timedelta(seconds=config.session_max_age_seconds)
    
    async def create_session(
        self,
        user: User,
        access_token: str,
        refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session"""
        session = Session(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + self.max_age,
            data=metadata or {}
        )
        
        await self.sessions_collection.insert_one(session.model_dump())
        logger.info(f"Created session {session.id} for user {user.id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        session_doc = await self.sessions_collection.find_one({"id": session_id})
        
        if not session_doc:
            return None
        
        session = Session(**session_doc)
        
        # Check if expired
        if session.is_expired:
            await self.delete_session(session_id)
            logger.info(f"Session {session_id} expired and deleted")
            return None
        
        return session
    
    async def get_session_by_token(self, access_token: str) -> Optional[Session]:
        """Get a session by access token"""
        session_doc = await self.sessions_collection.find_one({"access_token": access_token})
        
        if not session_doc:
            return None
        
        try:
            session = parse_session_from_mongo(session_doc)
            
            if session.is_expired:
                await self.delete_session(session.id)
                return None
            
            return session
        except Exception as e:
            logger.error(f"Error parsing session from MongoDB: {e}")
            return None
    
    async def update_session(
        self,
        session_id: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Update session tokens and data"""
        update_data = {
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        }
        
        if access_token:
            update_data["access_token"] = access_token
        
        if refresh_token:
            update_data["refresh_token"] = refresh_token
        
        if data:
            update_data["data"] = data
        
        await self.sessions_collection.update_one(
            {"id": session_id},
            {"$set": update_data}
        )
        
        logger.info(f"Updated session {session_id}")
    
    async def update_session_tokens(
        self,
        session_id: str,
        access_token: str,
        refresh_token: str
    ):
        """Update session with new tokens"""
        update_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.sessions_collection.update_one(
            {"id": session_id},
            {"$set": update_data}
        )
        
        logger.info(f"Updated session tokens for session {session_id}")
    
    async def delete_session(self, session_id: str):
        """Delete a session"""
        result = await self.sessions_collection.delete_one({"id": session_id})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted session {session_id}")
        else:
            logger.warning(f"Session {session_id} not found")
    
    async def delete_user_sessions(self, user_id: str):
        """Delete all sessions for a user"""
        result = await self.sessions_collection.delete_many({"user_id": user_id})
        logger.info(f"Deleted {result.deleted_count} sessions for user {user_id}")
    
    async def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        now = datetime.now(timezone.utc)
        result = await self.sessions_collection.delete_many({
            "expires_at": {"$lt": now.isoformat()}
        })
        
        if result.deleted_count > 0:
            logger.info(f"Cleaned up {result.deleted_count} expired sessions")
    
    async def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user"""
        sessions_docs = await self.sessions_collection.find({"user_id": user_id}).to_list(length=None)
        sessions = []
        for doc in sessions_docs:
            try:
                session = parse_session_from_mongo(doc)
                if not session.is_expired:
                    sessions.append(session)
            except Exception as e:
                logger.error(f"Error parsing session from MongoDB: {e}")
        return sessions
