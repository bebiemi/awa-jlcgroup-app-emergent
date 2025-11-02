"""Validation repository"""
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.domain.entities.validation import AccountValidation, ValidationStatus, ValidationType
from datetime import datetime


class ValidationRepository:
    """Repository for account validation operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.account_validations

    async def create(self, validation: AccountValidation) -> AccountValidation:
        """Create a new validation request"""
        validation_dict = validation.dict()
        validation_dict['created_at'] = validation.created_at.isoformat()
        validation_dict['updated_at'] = validation.updated_at.isoformat()
        if validation.reviewed_at:
            validation_dict['reviewed_at'] = validation.reviewed_at.isoformat()
        
        await self.collection.insert_one(validation_dict)
        return validation

    async def get_by_id(self, validation_id: str) -> Optional[AccountValidation]:
        """Get validation by ID"""
        doc = await self.collection.find_one({"id": validation_id}, {"_id": 0})
        if not doc:
            return None
        
        # Convert datetime strings
        if 'created_at' in doc and isinstance(doc['created_at'], str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if 'updated_at' in doc and isinstance(doc['updated_at'], str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
        if 'reviewed_at' in doc and doc['reviewed_at'] and isinstance(doc['reviewed_at'], str):
            doc['reviewed_at'] = datetime.fromisoformat(doc['reviewed_at'])
        
        return AccountValidation(**doc)

    async def get_by_user_id(self, user_id: str) -> Optional[AccountValidation]:
        """Get validation by user ID (most recent)"""
        doc = await self.collection.find_one(
            {"user_id": user_id},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        if not doc:
            return None
        
        if 'created_at' in doc and isinstance(doc['created_at'], str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if 'updated_at' in doc and isinstance(doc['updated_at'], str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
        if 'reviewed_at' in doc and doc['reviewed_at'] and isinstance(doc['reviewed_at'], str):
            doc['reviewed_at'] = datetime.fromisoformat(doc['reviewed_at'])
        
        return AccountValidation(**doc)

    async def update(self, validation: AccountValidation) -> AccountValidation:
        """Update validation"""
        validation.updated_at = datetime.utcnow()
        validation_dict = validation.dict()
        validation_dict['updated_at'] = validation.updated_at.isoformat()
        if validation.reviewed_at:
            validation_dict['reviewed_at'] = validation.reviewed_at.isoformat()
        
        await self.collection.update_one(
            {"id": validation.id},
            {"$set": validation_dict}
        )
        return validation

    async def list(
        self,
        status: Optional[ValidationStatus] = None,
        validation_type: Optional[ValidationType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[AccountValidation], int]:
        """List validations with filters"""
        query = {}
        if status:
            query["status"] = status.value
        if validation_type:
            query["validation_type"] = validation_type.value
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Get paginated results
        cursor = self.collection.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=None)
        
        validations = []
        for doc in docs:
            if 'created_at' in doc and isinstance(doc['created_at'], str):
                doc['created_at'] = datetime.fromisoformat(doc['created_at'])
            if 'updated_at' in doc and isinstance(doc['updated_at'], str):
                doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
            if 'reviewed_at' in doc and doc['reviewed_at'] and isinstance(doc['reviewed_at'], str):
                doc['reviewed_at'] = datetime.fromisoformat(doc['reviewed_at'])
            validations.append(AccountValidation(**doc))
        
        return validations, total

    async def count_by_status(self, status: ValidationStatus) -> int:
        """Count validations by status"""
        return await self.collection.count_documents({"status": status.value})
