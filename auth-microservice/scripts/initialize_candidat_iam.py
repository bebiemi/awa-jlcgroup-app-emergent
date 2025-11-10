"""
Initialize Candidat IAM Resources
Creates groups, profiles, and permissions for the new candidat role
"""
import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# Add parent directory to path to import constants
sys.path.insert(0, str(Path(__file__).parent.parent))
from awana_auth.core.iam_constants import IAMGroups, IAMProfiles, IAMPermissions


async def initialize_candidat_iam():
    """Initialize IAM resources for candidat role"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/jlc_interim')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database()
    
    print("🚀 Initializing Candidat IAM Resources...")
    
    # 1. Create candidat permissions
    permissions_to_add = [
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.MISSIONS_BROWSE,
            "name": "Consulter les missions",
            "description": "Permet de voir la liste des missions disponibles",
            "resource": "missions",
            "action": "browse",
            "scope": "public",
            "category": "missions",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.APPLICATIONS_CREATE_OWN,
            "name": "Créer une candidature",
            "description": "Permet de postuler à une mission",
            "resource": "applications",
            "action": "create",
            "scope": "own",
            "category": "applications",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.APPLICATIONS_READ_OWN,
            "name": "Voir ses candidatures",
            "description": "Permet de consulter ses propres candidatures",
            "resource": "applications",
            "action": "read",
            "scope": "own",
            "category": "applications",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.PROFILE_MANAGE_OWN,
            "name": "Gérer son profil",
            "description": "Permet de modifier son profil utilisateur",
            "resource": "profile",
            "action": "manage",
            "scope": "own",
            "category": "profile",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.AUTH_MFA_MANAGE,
            "name": "Gérer l'authentification 2FA",
            "description": "Permet d'activer/désactiver la double authentification",
            "resource": "auth",
            "action": "mfa.manage",
            "scope": "own",
            "category": "security",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.SECURITY_EMAIL_DOMAINS_READ,
            "name": "Lire les domaines email",
            "description": "Permet de consulter les domaines email autorisés",
            "resource": "security",
            "action": "email_domains.read",
            "scope": "system",
            "category": "security",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": IAMPermissions.SECURITY_EMAIL_DOMAINS_MANAGE,
            "name": "Gérer les domaines email",
            "description": "Permet d'ajouter/modifier/supprimer des domaines email autorisés",
            "resource": "security",
            "action": "email_domains.manage",
            "scope": "system",
            "category": "security",
            "is_system": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    permission_ids = {}
    for perm in permissions_to_add:
        existing = await db.iam_permissions.find_one({"code": perm["code"]})
        if not existing:
            await db.iam_permissions.insert_one(perm)
            print(f"✅ Created permission: {perm['code']}")
            permission_ids[perm['code']] = perm['id']
        else:
            print(f"⏭️  Permission already exists: {perm['code']}")
            permission_ids[perm['code']] = existing['id']
    
    # 2. Create candidat profile
    candidat_profile_id = str(uuid.uuid4())
    candidat_profile = {
        "id": candidat_profile_id,
        "code": IAMProfiles.CANDIDAT,
        "name": "Candidat",
        "description": "Profil pour les candidats (avant signature de contrat)",
        "permission_ids": [
            permission_ids.get(IAMPermissions.MISSIONS_BROWSE),
            permission_ids.get(IAMPermissions.APPLICATIONS_CREATE_OWN),
            permission_ids.get(IAMPermissions.APPLICATIONS_READ_OWN),
            permission_ids.get(IAMPermissions.PROFILE_MANAGE_OWN),
            permission_ids.get(IAMPermissions.AUTH_MFA_MANAGE)
        ],
        "category": "system",
        "color": "#10B981",  # Green
        "icon": "user",
        "is_system_role": True,
        "is_protected": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    existing_profile = await db.iam_profiles.find_one({"code": IAMProfiles.CANDIDAT})
    if not existing_profile:
        await db.iam_profiles.insert_one(candidat_profile)
        print(f"✅ Created profile: {IAMProfiles.CANDIDAT}")
    else:
        candidat_profile_id = existing_profile['id']
        print(f"⏭️  Profile already exists: {IAMProfiles.CANDIDAT}")
    
    # 3. Create candidat group
    candidat_group_id = str(uuid.uuid4())
    candidat_group = {
        "id": candidat_group_id,
        "code": IAMGroups.CANDIDAT,
        "name": "Candidats",
        "description": "Groupe des candidats (avant signature)",
        "profile_ids": [candidat_profile_id],
        "user_ids": [],
        "is_system_group": True,
        "is_protected": True,
        "parent_group_id": None,
        "created_at": datetime.utcnow().isoformat()
    }
    
    existing_group = await db.iam_groups.find_one({"code": IAMGroups.CANDIDAT})
    if not existing_group:
        await db.iam_groups.insert_one(candidat_group)
        print(f"✅ Created group: {IAMGroups.CANDIDAT}")
    else:
        print(f"⏭️  Group already exists: {IAMGroups.CANDIDAT}")
    
    # 4. Update existing admin/superadmin profiles with new permissions
    admin_profiles = await db.iam_profiles.find({"code": {"$in": [IAMProfiles.ADMIN, IAMProfiles.SUPER_ADMIN]}}).to_list(None)
    
    for profile in admin_profiles:
        updated_perms = set(profile.get("permission_ids", []))
        updated_perms.add(permission_ids.get(IAMPermissions.SECURITY_EMAIL_DOMAINS_READ))
        updated_perms.add(permission_ids.get(IAMPermissions.SECURITY_EMAIL_DOMAINS_MANAGE))
        
        await db.iam_profiles.update_one(
            {"id": profile["id"]},
            {"$set": {"permission_ids": list(updated_perms)}}
        )
        print(f"✅ Updated profile {profile['code']} with email domain permissions")
    
    print("\n✅ Candidat IAM initialization completed!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_candidat_iam())
