#!/usr/bin/env python3
"""
Add IAM-specific permissions for managing the IAM system itself
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

async def add_iam_permissions():
    """Add IAM-specific management permissions"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    iam_permissions = [
        # IAM Permissions Management
        {
            "code": "iam.permissions.read",
            "name": "Lire Permissions IAM",
            "description": "Consulter les permissions IAM",
            "resource": "iam.permissions",
            "action": "read",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.permissions.create",
            "name": "Créer Permissions IAM",
            "description": "Créer de nouvelles permissions IAM",
            "resource": "iam.permissions",
            "action": "create",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.permissions.delete",
            "name": "Supprimer Permissions IAM",
            "description": "Supprimer des permissions IAM",
            "resource": "iam.permissions",
            "action": "delete",
            "scope": "global",
            "category": "iam"
        },
        
        # IAM Profiles Management
        {
            "code": "iam.profiles.read",
            "name": "Lire Profils IAM",
            "description": "Consulter les profils IAM",
            "resource": "iam.profiles",
            "action": "read",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.profiles.create",
            "name": "Créer Profils IAM",
            "description": "Créer de nouveaux profils IAM",
            "resource": "iam.profiles",
            "action": "create",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.profiles.update",
            "name": "Modifier Profils IAM",
            "description": "Modifier les profils IAM existants",
            "resource": "iam.profiles",
            "action": "update",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.profiles.delete",
            "name": "Supprimer Profils IAM",
            "description": "Supprimer des profils IAM",
            "resource": "iam.profiles",
            "action": "delete",
            "scope": "global",
            "category": "iam"
        },
        
        # IAM Groups Management
        {
            "code": "iam.groups.read",
            "name": "Lire Groupes IAM",
            "description": "Consulter les groupes IAM",
            "resource": "iam.groups",
            "action": "read",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.groups.create",
            "name": "Créer Groupes IAM",
            "description": "Créer de nouveaux groupes IAM",
            "resource": "iam.groups",
            "action": "create",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.groups.update",
            "name": "Modifier Groupes IAM",
            "description": "Modifier les groupes IAM existants",
            "resource": "iam.groups",
            "action": "update",
            "scope": "global",
            "category": "iam"
        },
        {
            "code": "iam.groups.delete",
            "name": "Supprimer Groupes IAM",
            "description": "Supprimer des groupes IAM",
            "resource": "iam.groups",
            "action": "delete",
            "scope": "global",
            "category": "iam"
        },
        
        # User Assignments
        {
            "code": "iam.users.assign",
            "name": "Assigner Profils/Groupes",
            "description": "Assigner des profils et groupes aux utilisateurs",
            "resource": "iam.users",
            "action": "assign",
            "scope": "global",
            "category": "iam"
        },
    ]
    
    print(f"🔄 Adding IAM-specific permissions...")
    added_count = 0
    
    for perm_data in iam_permissions:
        existing = await db.permissions.find_one({"code": perm_data["code"]})
        
        if not existing:
            perm_data.update({
                "id": str(uuid.uuid4()),
                "is_system": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            await db.permissions.insert_one(perm_data)
            print(f"  ✅ Added: {perm_data['code']}")
            added_count += 1
    
    # Update Admin & SuperAdmin profiles
    all_permissions = await db.permissions.find({}).to_list(length=None)
    all_permission_ids = [p["id"] for p in all_permissions]
    
    await db.profiles.update_one(
        {"code": "admin"},
        {"$set": {
            "permission_ids": all_permission_ids,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await db.profiles.update_one(
        {"code": "super_admin"},
        {"$set": {
            "permission_ids": all_permission_ids,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    print(f"\n✅ Updated Admin & SuperAdmin profiles with all {len(all_permission_ids)} permissions")
    print(f"\n📊 Summary:")
    print(f"  - Added: {added_count} IAM permissions")
    print(f"  - Total permissions in system: {len(all_permissions)}")
    
    client.close()
    print("\n✅ IAM permissions setup complete!")

if __name__ == "__main__":
    asyncio.run(add_iam_permissions())
