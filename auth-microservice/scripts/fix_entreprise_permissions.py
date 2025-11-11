"""
Fix Entreprise Permissions - Correct format
Removes incorrectly formatted permissions and recreates them
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone


async def fix_entreprise_permissions():
    """Fix entreprise management permissions with correct format"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc).isoformat()
    
    print("🔧 Fixing entreprise management permissions...")
    
    # Delete existing entreprise permissions
    result = await db.permissions.delete_many({"code": {"$regex": "^entreprises\\."}})
    print(f"🗑️  Deleted {result.deleted_count} existing entreprise permissions")
    
    # Create permissions with correct format
    permissions = [
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.create",
            "name": "Créer des entreprises",
            "description": "Permet de créer de nouvelles entreprises dans le système",
            "resource": "entreprises",
            "action": "create",  # lowercase
            "scope": "all",
            "category": "entreprises",
            "is_system": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.read",
            "name": "Consulter les entreprises",
            "description": "Permet de consulter les informations des entreprises",
            "resource": "entreprises",
            "action": "read",  # lowercase
            "scope": "own",
            "category": "entreprises",
            "is_system": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.edit",
            "name": "Modifier les entreprises",
            "description": "Permet de modifier les informations des entreprises",
            "resource": "entreprises",
            "action": "edit",  # lowercase
            "scope": "own",
            "category": "entreprises",
            "is_system": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.delete",
            "name": "Supprimer des entreprises",
            "description": "Permet de supprimer des entreprises (admin seulement)",
            "resource": "entreprises",
            "action": "delete",  # lowercase
            "scope": "all",
            "category": "entreprises",
            "is_system": False,
            "created_at": now,
            "updated_at": now,
        },
    ]
    
    # Insert new permissions
    await db.permissions.insert_many(permissions)
    print(f"✅ Created {len(permissions)} entreprise permissions with correct format")
    
    print("\n🔧 Updating profiles with corrected permission IDs...")
    
    # Get new permission IDs
    entreprise_perm_codes = ["entreprises.read", "entreprises.edit"]
    entreprise_perm_ids = []
    for code in entreprise_perm_codes:
        perm = await db.permissions.find_one({"code": code})
        if perm:
            entreprise_perm_ids.append(perm["id"])
    
    # Update Entreprise profile
    if entreprise_perm_ids:
        existing_profile = await db.profiles.find_one({"code": "entreprise"})
        if existing_profile:
            # Get existing permissions that are NOT entreprise permissions
            current_perm_ids = existing_profile.get("permission_ids", [])
            
            # Get all entreprise permission codes
            all_entreprise_perms = await db.permissions.find({"code": {"$regex": "^entreprises\\."}}).to_list(length=None)
            all_entreprise_perm_ids = [p["id"] for p in all_entreprise_perms]
            
            # Remove old entreprise permissions and add new ones
            updated_perm_ids = [pid for pid in current_perm_ids if pid not in all_entreprise_perm_ids]
            updated_perm_ids.extend(entreprise_perm_ids)
            
            await db.profiles.update_one(
                {"code": "entreprise"},
                {"$set": {
                    "permission_ids": updated_perm_ids,
                    "updated_at": now
                }}
            )
            print(f"✅ Entreprise profile updated")
        else:
            print(f"⚠️  Entreprise profile not found")
    
    # Update Admin and SuperAdmin profiles
    all_entreprise_perm_ids = []
    for code in ["entreprises.create", "entreprises.read", "entreprises.edit", "entreprises.delete"]:
        perm = await db.permissions.find_one({"code": code})
        if perm:
            all_entreprise_perm_ids.append(perm["id"])
    
    for profile_code in ["admin", "super_admin"]:
        existing_profile = await db.profiles.find_one({"code": profile_code})
        if existing_profile:
            current_perm_ids = existing_profile.get("permission_ids", [])
            
            # Remove old entreprise permissions
            old_entreprise_perms = await db.permissions.find({"code": {"$regex": "^entreprises\\."}}).to_list(length=None)
            old_entreprise_perm_ids = [p["id"] for p in old_entreprise_perms]
            
            updated_perm_ids = [pid for pid in current_perm_ids if pid not in old_entreprise_perm_ids]
            updated_perm_ids.extend(all_entreprise_perm_ids)
            
            await db.profiles.update_one(
                {"code": profile_code},
                {"$set": {
                    "permission_ids": updated_perm_ids,
                    "updated_at": now
                }}
            )
            print(f"✅ {profile_code} profile updated")
        else:
            print(f"⚠️  {profile_code} profile not found")
    
    print("\n✅ Entreprise permissions fixed!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_entreprise_permissions())
