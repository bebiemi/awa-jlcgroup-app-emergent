"""
Initialize Postulant Profile
Creates the Postulant IAM profile with appropriate permissions
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main initialization function"""
    # Get MongoDB URL from environment
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    try:
        logger.info("🚀 Initializing Postulant profile...")
        
        # Postulant permissions
        postulant_permissions = [
            # Missions
            "missions.browse",
            "missions.read",
            
            # Applications
            "applications.create_own",
            "applications.read_own",
            "applications.update_own",
            
            # Profile
            "profile.manage_own",
            
            # Documents
            "documents.read_own",
            "documents.upload_own",
            "documents.delete_own",
            
            # Notifications
            "notifications.read_own",
            "notifications.manage_own",
            
            # Dashboard
            "dashboard.view_own",
            "dashboard.customize",
            
            # Messages/Chat
            "messages.read_own",
            "messages.send_own",
            
            # Matching AI
            "matching.view_recommendations",
        ]
        
        # Check if permissions exist, create if not
        for perm_code in postulant_permissions:
            existing = await db.permissions.find_one({"code": perm_code})
            if not existing:
                # Create permission
                permission = {
                    "id": f"perm_{perm_code.replace('.', '_')}",
                    "code": perm_code,
                    "name": perm_code.replace('.', ' ').replace('_', ' ').title(),
                    "description": f"Permission: {perm_code}",
                    "category": perm_code.split('.')[0],
                    "is_system": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                await db.permissions.insert_one(permission)
                logger.info(f"  ✅ Created permission: {perm_code}")
        
        # Check if Postulant profile exists
        existing_profile = await db.profiles.find_one({"code": "role.postulant"})
        
        if existing_profile:
            logger.info("📋 Postulant profile already exists, updating permissions...")
            result = await db.profiles.update_one(
                {"code": "role.postulant"},
                {
                    "$set": {
                        "permission_ids": postulant_permissions,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            logger.info(f"  ✅ Updated permissions: {result.modified_count} profile(s)")
        else:
            # Create Postulant profile
            profile = {
                "id": "profile_postulant",
                "code": "role.postulant",
                "name": "Postulant",
                "description": "Utilisateur postulant à des missions - Phase 3",
                "permission_ids": postulant_permissions,
                "is_system": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await db.profiles.insert_one(profile)
            logger.info("✅ Created Postulant profile")
        
        # Display profile summary
        profile = await db.profiles.find_one({"code": "role.postulant"}, {"_id": 0})
        logger.info(f"\n📊 Postulant Profile Summary:")
        logger.info(f"  Name: {profile['name']}")
        logger.info(f"  Code: {profile['code']}")
        logger.info(f"  Permissions: {len(profile['permission_ids'])}")
        logger.info(f"  Permissions list:")
        for perm in profile['permission_ids']:
            logger.info(f"    - {perm}")
        
        logger.info("\n✅ Postulant profile initialization complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
