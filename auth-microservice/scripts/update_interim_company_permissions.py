#!/usr/bin/env python3
"""
Update interim_user and company_admin profiles with correct permissions
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

async def update_profiles():
    """Update interim and company profiles with correct permissions"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🔄 Updating interim and company profiles...")
    
    # Get all permissions
    perms = await db.permissions.find({}).to_list(length=None)
    perm_map = {p['code']: p['id'] for p in perms}
    
    # Interim permissions
    interim_permissions = [
        'missions.browse',
        'applications.create',
        'applications.read_own',
        'profile.manage_own'
    ]
    interim_perm_ids = [perm_map[code] for code in interim_permissions if code in perm_map]
    
    # Company permissions
    company_permissions = [
        'missions.create',
        'missions.read',
        'missions.edit',
        'applications.read',
        'applications.manage',
        'profile.manage_own'
    ]
    company_perm_ids = [perm_map[code] for code in company_permissions if code in perm_map]
    
    # Update interim_user profile
    await db.profiles.update_one(
        {'code': 'interim_user'},
        {'$set': {
            'permission_ids': interim_perm_ids,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }}
    )
    print(f'✅ Updated interim_user with {len(interim_perm_ids)} permissions: {interim_permissions}')
    
    # Update company_admin profile
    await db.profiles.update_one(
        {'code': 'company_admin'},
        {'$set': {
            'permission_ids': company_perm_ids,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }}
    )
    print(f'✅ Updated company_admin with {len(company_perm_ids)} permissions: {company_permissions}')
    
    # Verify
    interim_profile = await db.profiles.find_one({'code': 'interim_user'})
    company_profile = await db.profiles.find_one({'code': 'company_admin'})
    
    print(f'\n📊 Verification:')
    print(f'  - interim_user: {len(interim_profile.get("permission_ids", []))} permissions')
    print(f'  - company_admin: {len(company_profile.get("permission_ids", []))} permissions')
    
    client.close()
    print("\n✅ Profile permissions update complete!")

if __name__ == "__main__":
    asyncio.run(update_profiles())
