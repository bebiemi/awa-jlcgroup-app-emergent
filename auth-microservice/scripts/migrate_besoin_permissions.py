"""
Migrate Besoin Permissions - Add scope field
Updates existing besoin permissions to include the scope field
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


async def migrate_besoin_permissions():
    """Add scope field to existing besoin permissions"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc)
    
    print("🔧 Migrating besoin permissions...")
    
    # Find all besoin permissions
    besoin_permissions = await db.permissions.find({
        "code": {"$regex": "^besoins\."}
    }).to_list(length=None)
    
    print(f"Found {len(besoin_permissions)} besoin permissions")
    
    for perm in besoin_permissions:
        # Check if scope exists
        if "scope" not in perm:
            await db.permissions.update_one(
                {"id": perm["id"]},
                {
                    "$set": {
                        "scope": "organization",
                        "updated_at": now
                    }
                }
            )
            print(f"✅ Updated permission {perm['code']} with scope field")
        else:
            print(f"ℹ️  Permission {perm['code']} already has scope field")
        
        # Also fix field name if needed (is_system_permission -> is_system)
        if "is_system_permission" in perm and "is_system" not in perm:
            await db.permissions.update_one(
                {"id": perm["id"]},
                {
                    "$set": {
                        "is_system": perm.get("is_system_permission", False)
                    },
                    "$unset": {
                        "is_system_permission": ""
                    }
                }
            )
            print(f"✅ Fixed field name for permission {perm['code']}")
    
    print("\n✅ Migration complete!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_besoin_permissions())
