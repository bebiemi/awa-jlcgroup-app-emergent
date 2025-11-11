"""
Script to assign IAM profiles to users based on their roles
Fixes the 403 Forbidden issue for users with roles but no profiles
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

# Role to Profile mapping
ROLE_TO_PROFILE_MAPPING = {
    'admin': 'admin',
    'super_admin': 'super_admin',
    'company': 'entreprise',  # Company users get 'entreprise' profile
    'interim': 'interim_user',
    'agency': 'company_admin',  # For now, agency gets company_admin
    'commercial': 'commercial',
    'validator': 'admin',  # Validators get admin profile
}


async def assign_profiles():
    """Assign profiles to users based on their roles"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # Get all users
    users = await db.users.find({}).to_list(length=None)
    
    print(f"Found {len(users)} users")
    
    # Get all profiles
    profiles = await db.profiles.find({}).to_list(length=None)
    profile_map = {p['code']: p['id'] for p in profiles}
    
    print(f"Available profiles: {list(profile_map.keys())}")
    
    updated_count = 0
    skipped_count = 0
    
    for user in users:
        user_id = user.get('id')
        username = user.get('username')
        roles = user.get('roles', [])
        current_profile_ids = user.get('profile_ids', [])
        
        # Skip users who already have profiles
        if current_profile_ids:
            print(f"  ⏭️  Skipping {username} - already has {len(current_profile_ids)} profile(s)")
            skipped_count += 1
            continue
        
        # Skip users without roles
        if not roles:
            print(f"  ⏭️  Skipping {username} - no roles assigned")
            skipped_count += 1
            continue
        
        # Assign profiles based on roles
        profiles_to_assign = []
        for role in roles:
            profile_code = ROLE_TO_PROFILE_MAPPING.get(role)
            if profile_code and profile_code in profile_map:
                profile_id = profile_map[profile_code]
                if profile_id not in profiles_to_assign:
                    profiles_to_assign.append(profile_id)
        
        if profiles_to_assign:
            # Update user with profiles
            result = await db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "profile_ids": profiles_to_assign,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                profile_names = [code for code, pid in profile_map.items() if pid in profiles_to_assign]
                print(f"  ✅ Updated {username} - assigned profiles: {profile_names}")
                updated_count += 1
            else:
                print(f"  ❌ Failed to update {username}")
        else:
            print(f"  ⚠️  No matching profiles found for {username} with roles: {roles}")
    
    print(f"\n📊 Summary:")
    print(f"  - Updated: {updated_count} users")
    print(f"  - Skipped: {skipped_count} users")
    print(f"  - Total: {len(users)} users")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(assign_profiles())
