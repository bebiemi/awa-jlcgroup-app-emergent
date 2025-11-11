"""
Script to initialize test users with correct IAM profiles
Run this after creating test accounts to ensure they have proper permissions
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

# Test users and their desired profiles
TEST_USERS_PROFILES = {
    'entreprise_test': ['entreprise'],
    'commercial_test': ['commercial', 'admin'],
    'interim_test2': ['interim_user'],
    'admin': ['super_admin', 'admin'],
}


async def init_test_users_profiles():
    """Initialize test users with correct IAM profiles"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # Get all profiles
    profiles = await db.profiles.find({}).to_list(length=None)
    profile_map = {p['code']: p['id'] for p in profiles}
    
    print(f"Available profiles: {list(profile_map.keys())}\n")
    
    for username, desired_profiles in TEST_USERS_PROFILES.items():
        user = await db.users.find_one({"username": username})
        
        if not user:
            print(f"⚠️  User '{username}' not found")
            continue
        
        user_id = user.get('id')
        current_profile_ids = user.get('profile_ids', [])
        
        # Get profile IDs for desired profiles
        profile_ids_to_assign = []
        for profile_code in desired_profiles:
            if profile_code in profile_map:
                profile_ids_to_assign.append(profile_map[profile_code])
            else:
                print(f"⚠️  Profile '{profile_code}' not found for user '{username}'")
        
        if not profile_ids_to_assign:
            print(f"⏭️  No profiles to assign for user '{username}'")
            continue
        
        # Check if user already has the desired profiles
        if set(current_profile_ids) == set(profile_ids_to_assign):
            print(f"✓ User '{username}' already has correct profiles: {desired_profiles}")
            continue
        
        # Update user with profiles
        result = await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "profile_ids": profile_ids_to_assign,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated user '{username}' with profiles: {desired_profiles}")
        else:
            print(f"❌ Failed to update user '{username}'")
    
    print("\n✅ Test users profile initialization complete!")
    client.close()


if __name__ == "__main__":
    asyncio.run(init_test_users_profiles())
