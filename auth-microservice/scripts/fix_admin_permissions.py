"""
Fix Admin vs Super Admin Permissions
- Super Admin: ALL permissions (global access)
- Admin: Limited permissions (specific administrative tasks)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


async def fix_admin_permissions():
    """Set appropriate permissions for admin vs super_admin"""
    
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc).isoformat()
    
    print("🔧 Fixing Admin vs Super Admin permissions...")
    
    # Define permissions for Admin profile (limited, operational permissions)
    admin_permission_codes = [
        # User management (limited)
        "users.read",
        "users.create",
        "users.edit",
        
        # Besoins management
        "besoins.read",
        "besoins.edit",
        "besoins.validate",
        "besoins.convert_to_mission",
        
        # Missions management
        "missions.read",
        "missions.create",
        "missions.edit",
        "missions.publish",
        "missions.browse",
        
        # Applications management
        "applications.read",
        "applications.manage",
        "applications.evaluate",
        
        # Configuration (read-only)
        "config.read",
        
        # IAM (limited)
        "iam.profiles.read",
        "iam.permissions.read",
        
        # Reports
        "reports.read",
        "reports.export",
        
        # Entreprises (read)
        "entreprises.read",
        "entreprises.edit",
    ]
    
    print(f"\n📋 Admin permissions defined: {len(admin_permission_codes)} permissions")
    
    # Get permission IDs for admin
    admin_perm_ids = []
    for code in admin_permission_codes:
        perm = await db.permissions.find_one({"code": code})
        if perm:
            admin_perm_ids.append(perm["id"])
        else:
            print(f"⚠️  Permission not found: {code}")
    
    print(f"✅ Found {len(admin_perm_ids)} valid permissions for admin")
    
    # Update Admin profile with limited permissions
    admin_profile = await db.profiles.find_one({"code": "admin"})
    if admin_profile:
        result = await db.profiles.update_one(
            {"code": "admin"},
            {"$set": {
                "permission_ids": admin_perm_ids,
                "updated_at": now
            }}
        )
        print(f"✅ Admin profile updated: {len(admin_perm_ids)} permissions")
    else:
        print("❌ Admin profile not found!")
    
    # Ensure Super Admin has ALL permissions
    print("\n🔧 Ensuring Super Admin has ALL permissions...")
    all_permissions = await db.permissions.find({}).to_list(length=None)
    all_permission_ids = [perm["id"] for perm in all_permissions]
    
    super_admin_profile = await db.profiles.find_one({"code": "super_admin"})
    if super_admin_profile:
        result = await db.profiles.update_one(
            {"code": "super_admin"},
            {"$set": {
                "permission_ids": all_permission_ids,
                "updated_at": now
            }}
        )
        print(f"✅ Super Admin profile updated: {len(all_permission_ids)} permissions (ALL)")
    else:
        print("❌ Super Admin profile not found!")
    
    # Show summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Admin permissions: {len(admin_perm_ids)}/{len(all_permission_ids)}")
    print(f"Super Admin permissions: {len(all_permission_ids)}/{len(all_permission_ids)} (ALL)")
    print("\n✅ Permissions fixed successfully!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_admin_permissions())
