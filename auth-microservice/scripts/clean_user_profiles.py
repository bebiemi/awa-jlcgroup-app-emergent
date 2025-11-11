"""
Clean User Profile Assignments
Remove super_admin profile from regular admin users
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


async def clean_user_profiles():
    """Remove super_admin profile from users who also have admin profile"""
    
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc).isoformat()
    
    print("🔧 Cleaning user profile assignments...")
    
    # Get profile IDs
    admin_profile = await db.profiles.find_one({"code": "admin"})
    super_admin_profile = await db.profiles.find_one({"code": "super_admin"})
    
    if not admin_profile or not super_admin_profile:
        print("❌ Admin or Super Admin profile not found!")
        client.close()
        return
    
    admin_profile_id = admin_profile["id"]
    super_admin_profile_id = super_admin_profile["id"]
    
    print(f"Admin profile ID: {admin_profile_id}")
    print(f"Super Admin profile ID: {super_admin_profile_id}")
    
    # Find users with both profiles
    users = await db.users.find({
        "profile_ids": {"$all": [admin_profile_id, super_admin_profile_id]}
    }).to_list(length=None)
    
    print(f"\n📊 Found {len(users)} user(s) with both admin AND super_admin profiles")
    
    for user in users:
        username = user.get('username', 'unknown')
        current_profiles = user.get('profile_ids', [])
        
        print(f"\n👤 User: {username}")
        print(f"   Current profiles: {current_profiles}")
        
        # Decision: Keep only admin profile, remove super_admin
        # Unless username explicitly indicates super_admin
        if 'super' in username.lower():
            print(f"   ℹ️  Username contains 'super' - keeping super_admin, removing admin")
            new_profiles = [super_admin_profile_id]
        else:
            print(f"   ℹ️  Regular admin - keeping admin profile, removing super_admin")
            new_profiles = [admin_profile_id]
        
        # Update user
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "profile_ids": new_profiles,
                "updated_at": now
            }}
        )
        
        print(f"   ✅ Updated to: {new_profiles}")
    
    print("\n✅ User profiles cleaned!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(clean_user_profiles())
