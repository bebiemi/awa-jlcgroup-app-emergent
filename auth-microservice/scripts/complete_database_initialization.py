#!/usr/bin/env python3
"""
🚀 Initialisation Complète de la Base de Données
================================================

Ce script initialise toutes les collections et données nécessaires
pour le fonctionnement complet de l'application JLC.

Collections créées:
- permissions (IAM)
- profiles (IAM)
- groups (IAM)
- iam_permissions (nouveau système IAM)
- iam_profiles (nouveau système IAM)
- iam_groups (nouveau système IAM)
- system_references (données de référence)
- users (déjà existant, mais mis à jour)
- audit_logs (déjà existant)
- sessions (déjà existant)
- locations (données géographiques)
- validations (validations utilisateurs)

Usage:
    python scripts/complete_database_initialization.py
    
Ou depuis Docker:
    docker exec jlc-auth-dev python /app/auth-microservice/scripts/complete_database_initialization.py
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==================== PERMISSIONS ====================

SYSTEM_PERMISSIONS = [
    # Users Management
    {"code": "users.create", "name": "Créer des utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.read", "name": "Consulter les utilisateurs", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "users.update", "name": "Modifier les utilisateurs", "resource": "users", "action": "update", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "Supprimer les utilisateurs", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    {"code": "users.manage", "name": "Gérer les utilisateurs", "resource": "users", "action": "manage", "scope": "organization", "category": "users"},
    
    # Missions Management
    {"code": "missions.create", "name": "Créer des missions", "resource": "missions", "action": "create", "scope": "organization", "category": "missions"},
    {"code": "missions.read", "name": "Consulter les missions", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    {"code": "missions.update", "name": "Modifier les missions", "resource": "missions", "action": "update", "scope": "organization", "category": "missions"},
    {"code": "missions.delete", "name": "Supprimer les missions", "resource": "missions", "action": "delete", "scope": "organization", "category": "missions"},
    {"code": "missions.approve", "name": "Approuver les missions", "resource": "missions", "action": "approve", "scope": "organization", "category": "missions"},
    {"code": "missions.manage", "name": "Gérer les missions", "resource": "missions", "action": "manage", "scope": "organization", "category": "missions"},
    
    # Contracts Management
    {"code": "contracts.create", "name": "Créer des contrats", "resource": "contracts", "action": "create", "scope": "organization", "category": "contracts"},
    {"code": "contracts.read", "name": "Consulter les contrats", "resource": "contracts", "action": "read", "scope": "organization", "category": "contracts"},
    {"code": "contracts.update", "name": "Modifier les contrats", "resource": "contracts", "action": "update", "scope": "organization", "category": "contracts"},
    {"code": "contracts.approve", "name": "Approuver les contrats", "resource": "contracts", "action": "approve", "scope": "organization", "category": "contracts"},
    
    # IAM Management
    {"code": "iam.profiles.read", "name": "Consulter les profils IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.manage", "name": "Gérer les profils IAM", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.groups.read", "name": "Consulter les groupes IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.groups.manage", "name": "Gérer les groupes IAM", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.read", "name": "Consulter les permissions", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.manage", "name": "Gérer les permissions", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    
    # Admin Dashboard
    {"code": "admin.dashboard", "name": "Accès au tableau de bord admin", "resource": "admin", "action": "read", "scope": "system", "category": "admin"},
    {"code": "admin.settings", "name": "Gérer les paramètres", "resource": "admin", "action": "update", "scope": "system", "category": "admin"},
    
    # System Configuration
    {"code": "system.config.read", "name": "Consulter la configuration", "resource": "system", "action": "read", "scope": "system", "category": "system"},
    {"code": "system.config.update", "name": "Modifier la configuration", "resource": "system", "action": "update", "scope": "system", "category": "system"},
    {"code": "system.featureflags.manage", "name": "Gérer les feature flags", "resource": "system", "action": "update", "scope": "system", "category": "system"},
    
    # Reports & Analytics
    {"code": "reports.view", "name": "Consulter les rapports", "resource": "reports", "action": "read", "scope": "organization", "category": "reports"},
    {"code": "reports.export", "name": "Exporter les rapports", "resource": "reports", "action": "export", "scope": "organization", "category": "reports"},
    
    # Profiles Management (user profiles, not IAM profiles)
    {"code": "profiles.read", "name": "Consulter les profils utilisateurs", "resource": "profiles", "action": "read", "scope": "organization", "category": "profiles"},
    {"code": "profiles.update", "name": "Modifier les profils utilisateurs", "resource": "profiles", "action": "update", "scope": "organization", "category": "profiles"},
]


# ==================== PROFILES ====================

SYSTEM_PROFILES = [
    {
        "code": "super_admin",
        "name": "Super Administrateur",
        "description": "Accès complet et illimité à toutes les fonctionnalités",
        "is_system_role": True,
        "is_protected": True,
        "priority": 1000,
        "category": "admin",
        "color": "#DC2626",
        "icon": "shield-check",
        "permission_codes": ["*"]
    },
    {
        "code": "admin",
        "name": "Administrateur",
        "description": "Gestion complète sauf configuration système",
        "is_system_role": True,
        "is_protected": True,
        "priority": 900,
        "category": "admin",
        "color": "#7C3AED",
        "icon": "user-shield",
        "permission_codes": [
            "users.create", "users.read", "users.update", "users.delete", "users.manage",
            "missions.create", "missions.read", "missions.update", "missions.delete", "missions.approve", "missions.manage",
            "contracts.create", "contracts.read", "contracts.update", "contracts.approve",
            "iam.profiles.read", "iam.profiles.manage", "iam.groups.read", "iam.groups.manage", "iam.permissions.read",
            "admin.dashboard", "admin.settings",
            "reports.view", "reports.export",
            "profiles.read", "profiles.update"
        ]
    },
    {
        "code": "company",
        "name": "Entreprise",
        "description": "Gestion des missions et intérimaires",
        "is_system_role": True,
        "is_protected": True,
        "priority": 500,
        "category": "user",
        "color": "#D97706",
        "icon": "building",
        "permission_codes": [
            "missions.create", "missions.read", "missions.update",
            "users.read",
            "contracts.read"
        ]
    },
    {
        "code": "interim",
        "name": "Intérimaire",
        "description": "Gestion profil et candidatures",
        "is_system_role": True,
        "is_protected": True,
        "priority": 300,
        "category": "user",
        "color": "#10B981",
        "icon": "user",
        "permission_codes": [
            "missions.read",
            "contracts.read",
            "profiles.read", "profiles.update"
        ]
    },
    {
        "code": "candidat",
        "name": "Candidat",
        "description": "Accès limité pour les candidats",
        "is_system_role": True,
        "is_protected": True,
        "priority": 200,
        "category": "user",
        "color": "#8B5CF6",
        "icon": "user-plus",
        "permission_codes": [
            "missions.read",
            "profiles.read", "profiles.update"
        ]
    },
]


# ==================== IAM GROUPS, PROFILES, PERMISSIONS ====================

IAM_PERMISSIONS = [
    # Candidat permissions
    {"code": "perm.candidat.view_own_profile", "name": "Voir son propre profil", "resource": "profiles", "action": "read", "scope": "own", "category": "profiles"},
    {"code": "perm.candidat.edit_own_profile", "name": "Modifier son propre profil", "resource": "profiles", "action": "update", "scope": "own", "category": "profiles"},
    {"code": "perm.candidat.view_missions", "name": "Voir les missions", "resource": "missions", "action": "read", "scope": "all", "category": "missions"},
    {"code": "perm.candidat.apply_mission", "name": "Postuler à une mission", "resource": "missions", "action": "apply", "scope": "all", "category": "missions"},
    
    # Company permissions
    {"code": "perm.company.create_mission", "name": "Créer une mission", "resource": "missions", "action": "create", "scope": "own", "category": "missions"},
    {"code": "perm.company.view_own_missions", "name": "Voir ses missions", "resource": "missions", "action": "read", "scope": "own", "category": "missions"},
    {"code": "perm.company.edit_own_missions", "name": "Modifier ses missions", "resource": "missions", "action": "update", "scope": "own", "category": "missions"},
    {"code": "perm.company.view_applications", "name": "Voir les candidatures", "resource": "missions", "action": "read_applications", "scope": "own", "category": "missions"},
    
    # Admin permissions
    {"code": "perm.admin.manage_users", "name": "Gérer les utilisateurs", "resource": "users", "action": "manage", "scope": "all", "category": "users"},
    {"code": "perm.admin.manage_missions", "name": "Gérer toutes les missions", "resource": "missions", "action": "manage", "scope": "all", "category": "missions"},
    {"code": "perm.admin.view_dashboard", "name": "Voir le tableau de bord", "resource": "dashboard", "action": "read", "scope": "all", "category": "dashboard"},
    {"code": "perm.admin.manage_iam", "name": "Gérer IAM", "resource": "iam", "action": "manage", "scope": "all", "category": "iam"},
]

IAM_PROFILES = [
    {
        "code": "role.super_admin",
        "name": "Super Admin",
        "description": "Accès complet",
        "permission_codes": ["*"],  # All permissions
        "is_system_role": True,
        "color": "#DC2626",
        "icon": "shield-check"
    },
    {
        "code": "role.admin",
        "name": "Admin",
        "description": "Administration complète",
        "permission_codes": [
            "perm.admin.manage_users",
            "perm.admin.manage_missions",
            "perm.admin.view_dashboard",
            "perm.admin.manage_iam"
        ],
        "is_system_role": True,
        "color": "#7C3AED",
        "icon": "user-shield"
    },
    {
        "code": "role.candidat",
        "name": "Candidat",
        "description": "Profil candidat",
        "permission_codes": [
            "perm.candidat.view_own_profile",
            "perm.candidat.edit_own_profile",
            "perm.candidat.view_missions",
            "perm.candidat.apply_mission"
        ],
        "is_system_role": True,
        "color": "#8B5CF6",
        "icon": "user-plus"
    },
    {
        "code": "role.company",
        "name": "Entreprise",
        "description": "Profil entreprise",
        "permission_codes": [
            "perm.company.create_mission",
            "perm.company.view_own_missions",
            "perm.company.edit_own_missions",
            "perm.company.view_applications"
        ],
        "is_system_role": True,
        "color": "#D97706",
        "icon": "building"
    },
]

IAM_GROUPS = [
    {
        "code": "grp.super_admin",
        "name": "Super Administrateurs",
        "description": "Groupe des super administrateurs",
        "profile_code": "role.super_admin",
        "is_system_group": True
    },
    {
        "code": "grp.admin",
        "name": "Administrateurs",
        "description": "Groupe des administrateurs",
        "profile_code": "role.admin",
        "is_system_group": True
    },
    {
        "code": "grp.candidat",
        "name": "Candidats",
        "description": "Groupe des candidats",
        "profile_code": "role.candidat",
        "is_system_group": True
    },
    {
        "code": "grp.company",
        "name": "Entreprises",
        "description": "Groupe des entreprises",
        "profile_code": "role.company",
        "is_system_group": True
    },
]


# ==================== SYSTEM REFERENCES ====================

SYSTEM_REFERENCES = [
    # User statuses
    {"category": "user_status", "code": "active", "name": "Actif", "description": "Utilisateur actif"},
    {"category": "user_status", "code": "pending", "name": "En attente", "description": "En attente de validation"},
    {"category": "user_status", "code": "suspended", "name": "Suspendu", "description": "Compte suspendu"},
    {"category": "user_status", "code": "inactive", "name": "Inactif", "description": "Compte inactif"},
    
    # Mission statuses
    {"category": "mission_status", "code": "draft", "name": "Brouillon", "description": "Mission en cours de création"},
    {"category": "mission_status", "code": "published", "name": "Publiée", "description": "Mission publiée"},
    {"category": "mission_status", "code": "in_progress", "name": "En cours", "description": "Mission en cours"},
    {"category": "mission_status", "code": "completed", "name": "Terminée", "description": "Mission terminée"},
    {"category": "mission_status", "code": "cancelled", "name": "Annulée", "description": "Mission annulée"},
    
    # Roles (for backward compatibility)
    {"category": "roles", "code": "super_admin", "name": "Super Admin", "is_hidden_from_admins": True},
    {"category": "roles", "code": "admin", "name": "Admin", "is_hidden_from_admins": False},
    {"category": "roles", "code": "company", "name": "Entreprise", "is_hidden_from_admins": False},
    {"category": "roles", "code": "interim", "name": "Intérimaire", "is_hidden_from_admins": False},
    {"category": "roles", "code": "candidat", "name": "Candidat", "is_hidden_from_admins": False},
]


async def initialize_database():
    """Initialize complete database with all required collections and data"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    print("=" * 70)
    print(" 🚀 INITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
    print("=" * 70)
    print(f"\n📍 MongoDB URL: {mongo_url}")
    print(f"📍 Database: auth_db")
    
    # ==================== 1. LEGACY PERMISSIONS ====================
    print("\n" + "=" * 70)
    print("📋 1. Création des Permissions (Legacy)")
    print("=" * 70)
    
    permissions_collection = db.permissions
    permission_map = {}
    
    for perm_data in SYSTEM_PERMISSIONS:
        existing = await permissions_collection.find_one({"code": perm_data["code"]})
        if existing:
            print(f"  ⏭  {perm_data['code']}")
            permission_map[perm_data["code"]] = existing["id"]
        else:
            perm_id = str(uuid.uuid4())
            permission = {
                "id": perm_id,
                **perm_data,
                "is_system": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await permissions_collection.insert_one(permission)
            permission_map[perm_data["code"]] = perm_id
            print(f"  ✅ {perm_data['code']}")
    
    print(f"\n✅ Total: {len(permission_map)} permissions")
    
    # ==================== 2. LEGACY PROFILES ====================
    print("\n" + "=" * 70)
    print("👥 2. Création des Profils (Legacy)")
    print("=" * 70)
    
    profiles_collection = db.profiles
    profile_map = {}
    
    for profile_data in SYSTEM_PROFILES:
        existing = await profiles_collection.find_one({"code": profile_data["code"]})
        
        # Resolve permission IDs
        if profile_data["permission_codes"] == ["*"]:
            permission_ids = list(permission_map.values())
        else:
            permission_ids = [
                permission_map[code] 
                for code in profile_data["permission_codes"]
                if code in permission_map
            ]
        
        if existing:
            await profiles_collection.update_one(
                {"code": profile_data["code"]},
                {"$set": {
                    "permission_ids": permission_ids,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            print(f"  🔄 {profile_data['name']} ({len(permission_ids)} permissions)")
            profile_map[profile_data["code"]] = existing["id"]
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
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await profiles_collection.insert_one(profile)
            profile_map[profile_data["code"]] = profile_id
            print(f"  ✅ {profile_data['name']} ({len(permission_ids)} permissions)")
    
    print(f"\n✅ Total: {len(SYSTEM_PROFILES)} profils")
    
    # ==================== 3. LEGACY GROUPS ====================
    print("\n" + "=" * 70)
    print("🏢 3. Création des Groupes (Legacy)")
    print("=" * 70)
    
    groups_collection = db.groups
    
    super_admin_profile = await profiles_collection.find_one({"code": "super_admin"})
    admin_group_data = {
        "id": str(uuid.uuid4()),
        "code": "super_admins",
        "name": "Super Administrateurs",
        "description": "Groupe des super administrateurs",
        "profile_ids": [super_admin_profile["id"]] if super_admin_profile else [],
        "user_ids": [],
        "is_system_group": True,
        "is_protected": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    existing_group = await groups_collection.find_one({"code": "super_admins"})
    if not existing_group:
        await groups_collection.insert_one(admin_group_data)
        print("  ✅ Super Administrateurs")
    else:
        print("  ⏭  Super Administrateurs")
    
    # ==================== 4. IAM PERMISSIONS ====================
    print("\n" + "=" * 70)
    print("🔐 4. Création des Permissions IAM (Nouveau Système)")
    print("=" * 70)
    
    iam_permissions_collection = db.iam_permissions
    iam_permission_map = {}
    
    for perm_data in IAM_PERMISSIONS:
        existing = await iam_permissions_collection.find_one({"code": perm_data["code"]})
        if existing:
            print(f"  ⏭  {perm_data['code']}")
            iam_permission_map[perm_data["code"]] = existing["id"]
        else:
            perm_id = str(uuid.uuid4())
            permission = {
                "id": perm_id,
                **perm_data,
                "is_system": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await iam_permissions_collection.insert_one(permission)
            iam_permission_map[perm_data["code"]] = perm_id
            print(f"  ✅ {perm_data['code']}")
    
    print(f"\n✅ Total: {len(iam_permission_map)} permissions IAM")
    
    # ==================== 5. IAM PROFILES ====================
    print("\n" + "=" * 70)
    print("👤 5. Création des Profils IAM (Nouveau Système)")
    print("=" * 70)
    
    iam_profiles_collection = db.iam_profiles
    iam_profile_map = {}
    
    for profile_data in IAM_PROFILES:
        existing = await iam_profiles_collection.find_one({"code": profile_data["code"]})
        
        # Resolve permission IDs
        if profile_data["permission_codes"] == ["*"]:
            permission_ids = list(iam_permission_map.values())
        else:
            permission_ids = [
                iam_permission_map[code]
                for code in profile_data["permission_codes"]
                if code in iam_permission_map
            ]
        
        if existing:
            await iam_profiles_collection.update_one(
                {"code": profile_data["code"]},
                {"$set": {
                    "permission_ids": permission_ids,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            print(f"  🔄 {profile_data['name']} ({len(permission_ids)} permissions)")
            iam_profile_map[profile_data["code"]] = existing["id"]
        else:
            profile_id = str(uuid.uuid4())
            profile = {
                "id": profile_id,
                "code": profile_data["code"],
                "name": profile_data["name"],
                "description": profile_data["description"],
                "permission_ids": permission_ids,
                "is_system_role": profile_data.get("is_system_role", True),
                "color": profile_data.get("color"),
                "icon": profile_data.get("icon"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await iam_profiles_collection.insert_one(profile)
            iam_profile_map[profile_data["code"]] = profile_id
            print(f"  ✅ {profile_data['name']} ({len(permission_ids)} permissions)")
    
    print(f"\n✅ Total: {len(IAM_PROFILES)} profils IAM")
    
    # ==================== 6. IAM GROUPS ====================
    print("\n" + "=" * 70)
    print("🏢 6. Création des Groupes IAM (Nouveau Système)")
    print("=" * 70)
    
    iam_groups_collection = db.iam_groups
    
    for group_data in IAM_GROUPS:
        existing = await iam_groups_collection.find_one({"code": group_data["code"]})
        
        # Get profile ID
        profile_id = iam_profile_map.get(group_data["profile_code"])
        
        if existing:
            print(f"  ⏭  {group_data['name']}")
        else:
            group_id = str(uuid.uuid4())
            group = {
                "id": group_id,
                "code": group_data["code"],
                "name": group_data["name"],
                "description": group_data["description"],
                "profile_ids": [profile_id] if profile_id else [],
                "user_ids": [],
                "is_system_group": group_data.get("is_system_group", True),
                "is_protected": True,
                "parent_group_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await iam_groups_collection.insert_one(group)
            print(f"  ✅ {group_data['name']}")
    
    print(f"\n✅ Total: {len(IAM_GROUPS)} groupes IAM")
    
    # ==================== 7. SYSTEM REFERENCES ====================
    print("\n" + "=" * 70)
    print("📚 7. Création des Références Système")
    print("=" * 70)
    
    system_refs_collection = db.system_references
    
    for ref_data in SYSTEM_REFERENCES:
        existing = await system_refs_collection.find_one({
            "category": ref_data["category"],
            "code": ref_data["code"]
        })
        if existing:
            print(f"  ⏭  {ref_data['category']}.{ref_data['code']}")
        else:
            ref_id = str(uuid.uuid4())
            ref = {
                "id": ref_id,
                **ref_data,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await system_refs_collection.insert_one(ref)
            print(f"  ✅ {ref_data['category']}.{ref_data['code']}")
    
    print(f"\n✅ Total: {len(SYSTEM_REFERENCES)} références")
    
    # ==================== 8. UPDATE EXISTING USERS ====================
    print("\n" + "=" * 70)
    print("👤 8. Mise à Jour des Utilisateurs Existants")
    print("=" * 70)
    
    users_collection = db.users
    
    # Add IAM fields if missing
    result = await users_collection.update_many(
        {"profile_ids": {"$exists": False}},
        {"$set": {"profile_ids": [], "group_ids": []}}
    )
    print(f"  ✅ {result.modified_count} utilisateurs mis à jour avec champs IAM")
    
    # Assign super_admin users to super_admin group
    super_admin_users = await users_collection.find({"roles": "super_admin"}).to_list(None)
    super_admin_group = await iam_groups_collection.find_one({"code": "grp.super_admin"})
    
    if super_admin_group and super_admin_users:
        user_ids = [user["id"] for user in super_admin_users]
        await iam_groups_collection.update_one(
            {"id": super_admin_group["id"]},
            {"$addToSet": {"user_ids": {"$each": user_ids}}}
        )
        print(f"  ✅ {len(user_ids)} super_admin assignés au groupe IAM")
    
    # ==================== 9. CREATE MISSING COLLECTIONS ====================
    print("\n" + "=" * 70)
    print("📦 9. Vérification des Collections")
    print("=" * 70)
    
    required_collections = [
        "users", "permissions", "profiles", "groups",
        "iam_permissions", "iam_profiles", "iam_groups",
        "system_references", "audit_logs", "sessions",
        "locations", "validations"
    ]
    
    existing_collections = await db.list_collection_names()
    
    for collection_name in required_collections:
        if collection_name in existing_collections:
            count = await db[collection_name].count_documents({})
            print(f"  ✅ {collection_name}: {count} documents")
        else:
            await db.create_collection(collection_name)
            print(f"  ✨ {collection_name}: créée")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print(" ✅ INITIALISATION TERMINÉE AVEC SUCCÈS")
    print("=" * 70)
    
    print("\n📊 Résumé:")
    print(f"   ✓ Permissions (Legacy): {len(permission_map)}")
    print(f"   ✓ Profils (Legacy): {len(SYSTEM_PROFILES)}")
    print(f"   ✓ Groupes (Legacy): 1")
    print(f"   ✓ Permissions IAM: {len(iam_permission_map)}")
    print(f"   ✓ Profils IAM: {len(IAM_PROFILES)}")
    print(f"   ✓ Groupes IAM: {len(IAM_GROUPS)}")
    print(f"   ✓ Références Système: {len(SYSTEM_REFERENCES)}")
    print(f"   ✓ Collections: {len(required_collections)}")
    
    print("\n💡 Prochaines étapes:")
    print("   1. Vérifier que l'interface IAM fonctionne")
    print("   2. Assigner des profils/groupes aux utilisateurs")
    print("   3. Tester les permissions")
    
    print("\n📝 Pour tester la connexion:")
    print("   curl -X POST http://localhost:8001/auth-api/auth/local/login \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"username\": \"adminbe\", \"password\": \"Awana2025!\"}'")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_database())
