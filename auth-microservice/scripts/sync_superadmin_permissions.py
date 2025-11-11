"""
Sync All Permissions to SuperAdmin Profile
Ensures super_admin profile has ALL permissions in the system
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


async def sync_superadmin_permissions():
    """Add all existing permissions to super_admin profile"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc).isoformat()
    
    print("🔧 Syncing all permissions to super_admin profile...")
    
    # Get super_admin profile
    super_admin_profile = await db.profiles.find_one({"code": "super_admin"})
    
    if not super_admin_profile:
        print("❌ super_admin profile not found!")
        client.close()
        return
    
    print(f"✅ Found super_admin profile: {super_admin_profile.get('name')}")
    
    # Get ALL permissions
    all_permissions = await db.permissions.find({}).to_list(length=None)
    all_permission_ids = [perm["id"] for perm in all_permissions]
    
    print(f"📊 Total permissions in system: {len(all_permission_ids)}")
    
    # Get current permissions in super_admin profile
    current_permission_ids = super_admin_profile.get("permission_ids", [])
    print(f"📊 Current permissions in super_admin: {len(current_permission_ids)}")
    
    # Check if update needed
    if set(current_permission_ids) == set(all_permission_ids):
        print("✅ super_admin already has all permissions! No update needed.")
    else:
        # Update super_admin profile with all permissions
        result = await db.profiles.update_one(
            {"code": "super_admin"},
            {"$set": {
                "permission_ids": all_permission_ids,
                "updated_at": now
            }}
        )
        
        if result.modified_count > 0:
            new_perms = len(all_permission_ids) - len(current_permission_ids)
            print(f"✅ super_admin profile updated!")
            print(f"   Added {new_perms} new permissions")
            print(f"   Total permissions now: {len(all_permission_ids)}")
        else:
            print("⚠️  No changes made")
    
    # Show permission categories
    print("\n📋 Permission categories:")
    categories = {}
    for perm in all_permissions:
        cat = perm.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count} permissions")
    
    print("\n✅ Sync complete!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(sync_superadmin_permissions())
