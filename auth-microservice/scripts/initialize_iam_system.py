"""
Initialize IAM System with predefined roles and permissions
Creates system profiles, groups, and permissions
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from awana_auth.utils.config_helpers import ConfigHelper as cfg

# Config-driven role codes (fallbacks preserve legacy behavior)
SUPER_ADMIN_ROLE = cfg.get_super_admin_role() or "super_admin"
ADMIN_ROLE = cfg.get_admin_role() or "admin"
COMMERCIAL_ROLE = cfg.get_commercial_role() or "commercial"
COMPANY_ROLE = cfg.get_company_role() or "company_admin"
INTERIM_ROLE = cfg.get_interim_role() or "interim_user"
POSTULANT_ROLE = cfg.get_role("postulant") or "applicant"


# System Permissions Definitions
SYSTEM_PERMISSIONS = [
    # Users Management
    {"code": "users.create", "name": "Créer des utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.read", "name": "Consulter les utilisateurs", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "users.update", "name": "Modifier les utilisateurs", "resource": "users", "action": "update", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "Supprimer les utilisateurs", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    
    # Missions Management
    {"code": "missions.create", "name": "Créer des missions", "resource": "missions", "action": "create", "scope": "organization", "category": "missions"},
    {"code": "missions.read", "name": "Consulter les missions", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    {"code": "missions.update", "name": "Modifier les missions", "resource": "missions", "action": "update", "scope": "organization", "category": "missions"},
    {"code": "missions.delete", "name": "Supprimer les missions", "resource": "missions", "action": "delete", "scope": "organization", "category": "missions"},
    {"code": "missions.approve", "name": "Approuver les missions", "resource": "missions", "action": "approve", "scope": "organization", "category": "missions"},
    
    # Contracts Management
    {"code": "contracts.create", "name": "Créer des contrats", "resource": "contracts", "action": "create", "scope": "organization", "category": "contracts"},
    {"code": "contracts.read", "name": "Consulter les contrats", "resource": "contracts", "action": "read", "scope": "organization", "category": "contracts"},
    {"code": "contracts.update", "name": "Modifier les contrats", "resource": "contracts", "action": "update", "scope": "organization", "category": "contracts"},
    {"code": "contracts.approve", "name": "Approuver les contrats", "resource": "contracts", "action": "approve", "scope": "organization", "category": "contracts"},
    
    # IAM Management
    {"code": "iam.profiles.manage", "name": "Gérer les profils", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.groups.manage", "name": "Gérer les groupes", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.manage", "name": "Gérer les permissions", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    
    # System Configuration
    {"code": "system.config.read", "name": "Consulter la configuration", "resource": "system", "action": "read", "scope": "system", "category": "system"},
    {"code": "system.config.update", "name": "Modifier la configuration", "resource": "system", "action": "update", "scope": "system", "category": "system"},
    {"code": "system.featureflags.manage", "name": "Gérer les feature flags", "resource": "system", "action": "update", "scope": "system", "category": "system"},
    
    # Reports & Analytics
    {"code": "reports.view", "name": "Consulter les rapports", "resource": "reports", "action": "read", "scope": "organization", "category": "reports"},
    {"code": "reports.export", "name": "Exporter les rapports", "resource": "reports", "action": "export", "scope": "organization", "category": "reports"},
]


# System Profiles Definitions
SYSTEM_PROFILES = [
    {
        "code": SUPER_ADMIN_ROLE,
        "name": "Super Administrateur",
        "description": "Accès complet et illimité à toutes les fonctionnalités",
        "is_system_role": True,
        "is_protected": True,
        "priority": 1000,
        "category": "admin",
        "color": "#DC2626",  # Red
        "icon": "shield-check",
        "permission_codes": ["*"]  # All permissions
    },
    {
        "code": ADMIN_ROLE,
        "name": "Administrateur",
        "description": "Gestion complète sauf configuration système",
        "is_system_role": True,
        "is_protected": True,
        "priority": 900,
        "category": "admin",
        "color": "#7C3AED",  # Purple
        "icon": "user-shield",
        "permission_codes": [
            "users.create", "users.read", "users.update", "users.delete",
            "missions.create", "missions.read", "missions.update", "missions.delete", "missions.approve",
            "contracts.create", "contracts.read", "contracts.update", "contracts.approve",
            "iam.profiles.manage", "iam.groups.manage",
            "reports.view", "reports.export"
        ]
    },
    {
        "code": "hr_manager",
        "name": "Responsable RH",
        "description": "Gestion des utilisateurs et validation entreprises",
        "is_system_role": True,
        "is_protected": True,
        "priority": 700,
        "category": "user",
        "color": "#0891B2",  # Cyan
        "icon": "users",
        "permission_codes": [
            "users.create", "users.read", "users.update",
            "contracts.read", "contracts.approve",
            "reports.view"
        ]
    },
    {
        "code": COMMERCIAL_ROLE,
        "name": "Commercial",
        "description": "Gestion des missions et matching",
        "is_system_role": True,
        "is_protected": True,
        "priority": 600,
        "category": "user",
        "color": "#059669",  # Green
        "icon": "briefcase",
        "permission_codes": [
            "missions.create", "missions.read", "missions.update",
            "users.read",
            "contracts.read",
            "reports.view"
        ]
    },
    {
        "code": COMPANY_ROLE,
        "name": "Admin Société",
        "description": "Gestion des missions et intérimaires de la société",
        "is_system_role": True,
        "is_protected": True,
        "priority": 500,
        "category": "user",
        "color": "#D97706",  # Amber
        "icon": "building",
        "permission_codes": [
            "missions.create", "missions.read", "missions.update",
            "users.read",
            "contracts.read"
        ]
    },
    {
        "code": "team_manager",
        "name": "Responsable d'Équipe",
        "description": "Validation émargements et gestion groupe",
        "is_system_role": True,
        "is_protected": True,
        "priority": 400,
        "category": "user",
        "color": "#2563EB",  # Blue
        "icon": "user-group",
        "permission_codes": [
            "users.read",
            "missions.read",
            "contracts.read"
        ]
    },
    {
        "code": INTERIM_ROLE,
        "name": "Intérimaire",
        "description": "Gestion profil et candidatures",
        "is_system_role": True,
        "is_protected": True,
        "priority": 300,
        "category": "user",
        "color": "#10B981",  # Emerald
        "icon": "user",
        "permission_codes": [
            "missions.read",
            "contracts.read"
        ]
    },
    {
        "code": POSTULANT_ROLE,
        "name": "Postulant",
        "description": "Consultation missions avant signature contrat",
        "is_system_role": True,
        "is_protected": True,
        "priority": 200,
        "category": "user",
        "color": "#8B5CF6",  # Violet
        "icon": "user-plus",
        "permission_codes": [
            "missions.read"
        ]
    },
    {
        "code": "read_only",
        "name": "Lecture Seule",
        "description": "Visualisation uniquement",
        "is_system_role": True,
        "is_protected": True,
        "priority": 100,
        "category": "user",
        "color": "#6B7280",  # Gray
        "icon": "eye",
        "permission_codes": [
            "users.read",
            "missions.read",
            "contracts.read",
            "reports.view"
        ]
    },
]


async def initialize_iam():
    """Initialize IAM system with predefined data"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    print("=" * 60)
    print("IAM System Initialization")
    print("=" * 60)
    
    # 1. Create Permissions
    print("\n📋 Creating system permissions...")
    permissions_collection = db.permissions
    permission_map = {}  # code -> id
    
    for perm_data in SYSTEM_PERMISSIONS:
        # Check if exists
        existing = await permissions_collection.find_one({"code": perm_data["code"]})
        if existing:
            print(f"  ⏭  Permission exists: {perm_data['code']}")
            permission_map[perm_data["code"]] = existing["id"]
        else:
            perm_id = str(uuid.uuid4())
            permission = {
                "id": perm_id,
                **perm_data,
                "is_system": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await permissions_collection.insert_one(permission)
            permission_map[perm_data["code"]] = perm_id
            print(f"  ✅ Created: {perm_data['code']}")
    
    print(f"\n✅ {len(permission_map)} permissions initialized")
    
    # 2. Create Profiles
    print("\n👥 Creating system profiles...")
    profiles_collection = db.profiles
    
    for profile_data in SYSTEM_PROFILES:
        # Check if exists
        existing = await profiles_collection.find_one({"code": profile_data["code"]})
        
        # Resolve permission IDs
        if profile_data["permission_codes"] == ["*"]:
            # Super admin gets all permissions
            permission_ids = list(permission_map.values())
        else:
            permission_ids = [
                permission_map[code] 
                for code in profile_data["permission_codes"]
                if code in permission_map
            ]
        
        if existing:
            # Update permissions if needed
            await profiles_collection.update_one(
                {"code": profile_data["code"]},
                {"$set": {
                    "permission_ids": permission_ids,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            print(f"  🔄 Updated: {profile_data['name']}")
        else:
            profile_id = str(uuid.uuid4())
            profile = {
                "id": profile_id,
                "code": profile_data["code"],
                "name": profile_data["name"],
                "description": profile_data["description"],
                "permission_ids": permission_ids,
                "is_system_role": profile_data["is_system_role"],
                "is_protected": profile_data["is_protected"],
                "priority": profile_data["priority"],
                "category": profile_data["category"],
                "color": profile_data.get("color"),
                "icon": profile_data.get("icon"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await profiles_collection.insert_one(profile)
            print(f"  ✅ Created: {profile_data['name']} ({len(permission_ids)} permissions)")
    
    print(f"\n✅ {len(SYSTEM_PROFILES)} profiles initialized")
    
    # 3. Create System Groups
    print("\n🏢 Creating system groups...")
    groups_collection = db.groups
    
    # Admin Group
    super_admin_profile = await profiles_collection.find_one({"code": SUPER_ADMIN_ROLE})
    admin_group_data = {
        "id": str(uuid.uuid4()),
        "code": f"{SUPER_ADMIN_ROLE}s",
        "name": "Super Administrateurs",
        "description": "Groupe des super administrateurs",
        "profile_ids": [super_admin_profile["id"]] if super_admin_profile else [],
        "user_ids": [],
        "is_system_group": True,
        "is_protected": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    existing_group = await groups_collection.find_one({"code": f"{SUPER_ADMIN_ROLE}s"})
    if not existing_group:
        await groups_collection.insert_one(admin_group_data)
        print("  ✅ Created: Super Administrateurs group")
    else:
        print("  ⏭  Super Administrateurs group exists")
    
    # 4. Add profile_ids and group_ids fields to users if not present
    print("\n👤 Updating user schema...")
    users_collection = db.users
    result = await users_collection.update_many(
        {"profile_ids": {"$exists": False}},
        {"$set": {"profile_ids": [], "group_ids": []}}
    )
    print(f"  ✅ Updated {result.modified_count} users with IAM fields")
    
    print("\n" + "=" * 60)
    print("✅ IAM System Initialization Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   - Permissions: {len(permission_map)}")
    print(f"   - Profiles: {len(SYSTEM_PROFILES)}")
    print(f"   - Groups: 1 (Super Admins)")
    print(f"\n💡 Next steps:")
    print(f"   1. Assign profiles to existing users")
    print(f"   2. Create additional custom groups as needed")
    print(f"   3. Configure IAM UI in frontend")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_iam())
