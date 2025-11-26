#!/usr/bin/env python3
"""
Migrate existing users to IAM system
Assigns profiles based on their current roles
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

from awana_auth.utils.config_helpers import ConfigHelper as cfg

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


def _build_role_to_profile_mapping():
    """Build a config-driven mapping from roles to IAM profile codes."""
    mapping = {
        cfg.get_super_admin_role(): "super_admin",
        cfg.get_admin_role(): "admin",
        cfg.get_interim_role(): "interim_user",  # Fixed: map to interim_user profile
        cfg.get_company_role(): "company_admin",  # Fixed: map to company_admin profile
        cfg.get_commercial_role(): "commercial",
        cfg.get_validator_role(): "validator",
        cfg.get_agency_role(): "agency",
    }

    # Remove any undefined entries to avoid None keys in lookups
    return {role: profile for role, profile in mapping.items() if role}


# Role to Profile mapping
ROLE_TO_PROFILE_MAPPING = _build_role_to_profile_mapping()

async def migrate_users():
    """Migrate all users to IAM by assigning profiles based on roles"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🔄 Migrating users to IAM system...")
    
    # Get all profiles
    profiles = await db.profiles.find({}).to_list(length=None)
    profile_map = {p["code"]: p["id"] for p in profiles}
    
    print(f"📊 Found {len(profiles)} profiles in system:")
    for code, pid in profile_map.items():
        print(f"  - {code}: {pid}")
    
    # Get all users
    users = await db.users.find({}).to_list(length=None)
    print(f"\n👥 Found {len(users)} users to migrate")
    
    migrated_count = 0
    skipped_count = 0
    
    for user in users:
        user_id = user.get("id")
        username = user.get("username", "unknown")
        roles = user.get("roles", [])
        
        # Skip if already has profile_ids
        if user.get("profile_ids") and len(user.get("profile_ids", [])) > 0:
            print(f"  ⏭️  Skipped {username} (already has profiles)")
            skipped_count += 1
            continue
        
        # Determine profile IDs based on roles
        profile_ids = []
        for role in roles:
            profile_code = ROLE_TO_PROFILE_MAPPING.get(role)
            if profile_code and profile_code in profile_map:
                profile_ids.append(profile_map[profile_code])
        
        if not profile_ids:
            print(f"  ⚠️  {username}: No matching profiles for roles {roles}")
            continue
        
        # Update user with profile_ids
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "profile_ids": profile_ids,
                    "group_ids": [],  # Empty for now, can be assigned later
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        profile_names = [code for code, pid in profile_map.items() if pid in profile_ids]
        print(f"  ✅ {username}: Assigned profiles {profile_names}")
        migrated_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"  - Migrated: {migrated_count} users")
    print(f"  - Skipped: {skipped_count} users (already migrated)")
    print(f"  - Total: {len(users)} users")
    
    # Verify migration
    users_with_profiles = await db.users.count_documents({"profile_ids": {"$exists": True, "$ne": []}})
    print(f"\n✅ Verification: {users_with_profiles}/{len(users)} users now have IAM profiles")
    
    client.close()
    print("\n✅ User IAM migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_users())
