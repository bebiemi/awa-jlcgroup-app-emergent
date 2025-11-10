"""
Email Domain Service
Handles validation of email domains for collaborator accounts
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime


class EmailDomainService:
    """Service for managing and verifying allowed email domains"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.allowed_email_domains
    
    async def initialize_default_domains(self):
        """Initialize default JLC Group domains if not exists"""
        default_domains = [
            {
                "domain": "@jlcgroup.org",
                "country_code": "GA",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"description": "Main JLC Group domain"}
            },
            {
                "domain": "@jlcgroup.com",
                "country_code": None,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"description": "JLC Group international"}
            },
            {
                "domain": "@jlcgroup.ga",
                "country_code": "GA",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"description": "JLC Group Gabon"}
            }
        ]
        
        for domain_data in default_domains:
            existing = await self.collection.find_one({"domain": domain_data["domain"]})
            if not existing:
                await self.collection.insert_one(domain_data)
    
    async def is_collaborator_email(self, email: str) -> bool:
        """
        Check if email belongs to a collaborator (allowed domain)
        
        Args:
            email: Email address to check
            
        Returns:
            True if email domain is in allowed list and active
        """
        if not email or '@' not in email:
            return False
        
        # Extract domain from email
        domain = '@' + email.split('@')[1].lower()
        
        # Check if domain exists and is active
        domain_doc = await self.collection.find_one({
            "domain": domain,
            "is_active": True
        })
        
        return domain_doc is not None
    
    async def get_all_active_domains(self) -> List[str]:
        """Get list of all active allowed domains"""
        cursor = self.collection.find({"is_active": True})
        domains = []
        async for doc in cursor:
            domains.append(doc["domain"])
        return domains
    
    async def verify_email_domain(self, email: str) -> dict:
        """
        Verify email domain and return detailed information
        
        Args:
            email: Email to verify
            
        Returns:
            Dict with verification details
        """
        if not email or '@' not in email:
            return {
                "email": email,
                "is_valid": False,
                "domain": None,
                "is_collaborator": False,
                "message": "Format d'email invalide"
            }
        
        domain = '@' + email.split('@')[1].lower()
        is_collaborator = await self.is_collaborator_email(email)
        
        if is_collaborator:
            message = "Email collaborateur valide"
        else:
            message = "Email candidat (domaine public)"
        
        return {
            "email": email,
            "is_valid": True,
            "domain": domain,
            "is_collaborator": is_collaborator,
            "message": message
        }
    
    async def create_domain(self, domain_data: dict, created_by: Optional[str] = None) -> dict:
        """Create a new allowed domain"""
        domain_data["created_by"] = created_by
        domain_data["created_at"] = datetime.utcnow().isoformat()
        domain_data["updated_at"] = None
        
        result = await self.collection.insert_one(domain_data)
        domain_data["_id"] = str(result.inserted_id)
        return domain_data
    
    async def update_domain(self, domain_id: str, update_data: dict) -> Optional[dict]:
        """Update an existing domain"""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await self.collection.find_one_and_update(
            {"id": domain_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    async def delete_domain(self, domain_id: str) -> bool:
        """Delete a domain (soft delete by setting is_active to False)"""
        result = await self.collection.update_one(
            {"id": domain_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow().isoformat()}}
        )
        return result.modified_count > 0
    
    async def get_domain(self, domain_id: str) -> Optional[dict]:
        """Get a single domain by ID"""
        return await self.collection.find_one({"id": domain_id})
    
    async def list_domains(self, active_only: bool = False) -> List[dict]:
        """List all domains"""
        query = {"is_active": True} if active_only else {}
        cursor = self.collection.find(query)
        domains = []
        async for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            domains.append(doc)
        return domains
