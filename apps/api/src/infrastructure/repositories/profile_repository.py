"""Profile repository"""
from typing import Optional, List, Union
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.domain.entities.profile import Profile, ProfileType, AgencyProfile, CompanyProfile, InterimProfile
from datetime import datetime


class ProfileRepository:
    """Repository for profile operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.profiles

    async def create(self, profile: Profile) -> Profile:
        """Create a new profile"""
        profile_dict = profile.dict()
        profile_dict['created_at'] = profile.created_at.isoformat()
        profile_dict['updated_at'] = profile.updated_at.isoformat()
        await self.collection.insert_one(profile_dict)
        return profile

    async def get_by_user_id(self, user_id: str) -> Optional[Profile]:
        """Get profile by user ID"""
        doc = await self.collection.find_one({"user_id": user_id}, {"_id": 0})
        if not doc:
            return None
        
        # Convert datetime strings back to datetime objects
        if 'created_at' in doc and isinstance(doc['created_at'], str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if 'updated_at' in doc and isinstance(doc['updated_at'], str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
        
        return Profile(**doc)

    async def get_by_id(self, profile_id: str) -> Optional[Profile]:
        """Get profile by ID"""
        doc = await self.collection.find_one({"id": profile_id}, {"_id": 0})
        if not doc:
            return None
        
        if 'created_at' in doc and isinstance(doc['created_at'], str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if 'updated_at' in doc and isinstance(doc['updated_at'], str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
        
        return Profile(**doc)

    async def update(self, profile: Profile) -> Profile:
        """Update profile"""
        profile.updated_at = datetime.utcnow()
        profile_dict = profile.dict()
        profile_dict['updated_at'] = profile.updated_at.isoformat()
        
        await self.collection.update_one(
            {"id": profile.id},
            {"$set": profile_dict}
        )
        return profile

    async def delete(self, profile_id: str) -> bool:
        """Delete profile"""
        result = await self.collection.delete_one({"id": profile_id})
        return result.deleted_count > 0

    async def list_by_type(
        self,
        profile_type: Union[ProfileType, str],
        skip: int = 0,
        limit: int = 100
    ) -> List[Profile]:
        """List profiles by type (enum or raw value)"""
        profile_type_value = profile_type.value if isinstance(profile_type, ProfileType) else profile_type
        cursor = self.collection.find(
            {"profile_type": profile_type_value},
            {"_id": 0}
        ).skip(skip).limit(limit)
        
        docs = await cursor.to_list(length=None)
        profiles = []
        for doc in docs:
            if 'created_at' in doc and isinstance(doc['created_at'], str):
                doc['created_at'] = datetime.fromisoformat(doc['created_at'])
            if 'updated_at' in doc and isinstance(doc['updated_at'], str):
                doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
            profiles.append(Profile(**doc))
        
        return profiles
