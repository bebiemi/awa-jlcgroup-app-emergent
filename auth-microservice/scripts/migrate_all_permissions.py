"""
Migrate All Permissions - Fix missing fields
Updates all existing permissions to include resource, action, and scope fields
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


async def migrate_all_permissions():
    """Add required fields to all existing permissions"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc)
    
    print("🔧 Migrating all permissions...")
    
    # Find all permissions
    all_permissions = await db.permissions.find({}).to_list(length=None)
    
    print(f"Found {len(all_permissions)} total permissions")
    
    for perm in all_permissions:
        updates = {}
        
        # Extract resource and action from code if missing
        if "resource" not in perm or "action" not in perm:
            code = perm.get("code", "")
            parts = code.split(".")
            
            if len(parts) >= 2:
                resource = parts[0]  # e.g., "missions", "users", "besoins"
                action = parts[1]    # e.g., "create", "read", "edit"
                
                if "resource" not in perm:
                    updates["resource"] = resource
                    print(f"  Adding resource '{resource}' to {code}")
                
                if "action" not in perm:
                    updates["action"] = action
                    print(f"  Adding action '{action}' to {code}")
        
        # Add scope if missing
        if "scope" not in perm:
            updates["scope"] = "organization"
            print(f"  Adding scope 'organization' to {perm.get('code', 'unknown')}")
        
        # Fix field name if needed (is_system_permission -> is_system)
        if "is_system_permission" in perm and "is_system" not in perm:
            updates["is_system"] = perm.get("is_system_permission", False)
            print(f"  Renaming is_system_permission to is_system for {perm.get('code', 'unknown')}")
        
        # Apply updates if any
        if updates:
            updates["updated_at"] = now
            await db.permissions.update_one(
                {"id": perm["id"]},
                {"$set": updates}
            )
            
            # Remove old field if it exists
            if "is_system_permission" in perm:
                await db.permissions.update_one(
                    {"id": perm["id"]},
                    {"$unset": {"is_system_permission": ""}}
                )
            
            print(f"✅ Updated permission {perm.get('code', perm.get('id'))}")
    
    print("\n✅ Migration complete!")
    print(f"Total permissions processed: {len(all_permissions)}")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    missing_fields = await db.permissions.find({
        "$or": [
            {"resource": {"$exists": False}},
            {"action": {"$exists": False}},
            {"scope": {"$exists": False}}
        ]
    }).to_list(length=None)
    
    if missing_fields:
        print(f"⚠️  Warning: {len(missing_fields)} permissions still missing fields:")
        for perm in missing_fields:
            print(f"  - {perm.get('code', perm.get('id'))}: ", end="")
            missing = []
            if "resource" not in perm:
                missing.append("resource")
            if "action" not in perm:
                missing.append("action")
            if "scope" not in perm:
                missing.append("scope")
            print(", ".join(missing))
    else:
        print("✅ All permissions have required fields!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_all_permissions())
