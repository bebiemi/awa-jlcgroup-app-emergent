#!/usr/bin/env python3
"""
🚀 Initialisation Forcée de la Base de Données
================================================

Ce script force la création des permissions, profils et groupes
même si les collections existent déjà.

ATTENTION: Ce script n'efface PAS les données existantes, il ajoute
uniquement les données manquantes.

Usage:
    docker exec jlc-auth-dev python /app/auth-microservice/scripts/force_initialize_database.py
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
    
    # Reports & Analytics
    {"code": "reports.view", "name": "Consulter les rapports", "resource": "reports", "action": "read", "scope": "organization", "category": "reports"},
    {"code": "reports.export", "name": "Exporter les rapports", "resource": "reports", "action": "export", "scope": "organization", "category": "reports"},
    
    # Profiles Management
    {"code": "profiles.read", "name": "Consulter les profils utilisateurs", "resource": "profiles", "action": "read", "scope": "organization", "category": "profiles"},
    {"code": "profiles.update", "name": "Modifier les profils utilisateurs", "resource": "profiles", "action": "update", "scope": "organization", "category": "profiles"},
]


# ==================== IAM PERMISSIONS ====================

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


async def force_initialize():
    """Force initialization of database"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    print("=" * 70)
    print(" 🚀 INITIALISATION FORCÉE DE LA BASE DE DONNÉES")
    print("=" * 70)
    print(f"\n📍 MongoDB URL: {mongo_url}")
    print(f"📍 Database: auth_db\n")
    
    created_count = 0
    skipped_count = 0
    
    # ==================== 1. PERMISSIONS (LEGACY) ====================
    print("=" * 70)
    print("📋 1. Création des Permissions (Legacy)")
    print("=" * 70 + "\n")
    
    permissions_collection = db.permissions
    permission_map = {}
    
    for perm_data in SYSTEM_PERMISSIONS:
        existing = await permissions_collection.find_one({"code": perm_data["code"]})
        if existing:
            print(f"  ⏭  {perm_data['code']}")
            permission_map[perm_data["code"]] = existing["id"]
            skipped_count += 1
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
            created_count += 1
    
    print(f"\n✅ Permissions: {created_count} créées, {skipped_count} existantes")
    
    # ==================== 2. IAM PERMISSIONS ====================
    print("\n" + "=" * 70)
    print("🔐 2. Création des Permissions IAM")
    print("=" * 70 + "\n")
    
    iam_permissions_collection = db.iam_permissions
    iam_permission_map = {}
    created_iam = 0
    skipped_iam = 0
    
    for perm_data in IAM_PERMISSIONS:
        existing = await iam_permissions_collection.find_one({"code": perm_data["code"]})
        if existing:
            print(f"  ⏭  {perm_data['code']}")
            iam_permission_map[perm_data["code"]] = existing["id"]
            skipped_iam += 1
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
            created_iam += 1
    
    print(f"\n✅ Permissions IAM: {created_iam} créées, {skipped_iam} existantes")
    
    # ==================== 3. PROFILES (LEGACY) ====================
    print("\n" + "=" * 70)
    print("👥 3. Création/Mise à jour des Profils (Legacy)")
    print("=" * 70 + "\n")
    
    profiles_collection = db.profiles
    
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
            "permission_codes": list(permission_map.keys())  # All permissions
        },
    ]
    
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
            # Force update with new permissions
            await profiles_collection.update_one(
                {"code": profile_data["code"]},
                {"$set": {
                    "permission_ids": permission_ids,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            print(f"  🔄 {profile_data['name']} - {len(permission_ids)} permissions")
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
            print(f"  ✅ {profile_data['name']} - {len(permission_ids)} permissions")
    
    # ==================== 4. IAM PROFILES ====================
    print("\n" + "=" * 70)
    print("🆔 4. Création/Mise à jour des Profils IAM")
    print("=" * 70 + "\n")
    
    iam_profiles_collection = db.iam_profiles
    
    IAM_PROFILES = [
        {
            "code": "role.super_admin",
            "name": "Super Admin",
            "description": "Accès complet",
            "permission_codes": list(iam_permission_map.keys()),  # All IAM permissions
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
    
    iam_profile_map = {}
    
    for profile_data in IAM_PROFILES:
        existing = await iam_profiles_collection.find_one({"code": profile_data["code"]})
        
        # Resolve permission IDs
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
            print(f"  🔄 {profile_data['name']} - {len(permission_ids)} permissions")
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
            print(f"  ✅ {profile_data['name']} - {len(permission_ids)} permissions")
    
    # ==================== 5. IAM GROUPS ====================
    print("\n" + "=" * 70)
    print("🏢 5. Création des Groupes IAM")
    print("=" * 70 + "\n")
    
    iam_groups_collection = db.iam_groups
    
    IAM_GROUPS = [
        {"code": "grp.super_admin", "name": "Super Administrateurs", "profile_code": "role.super_admin"},
        {"code": "grp.admin", "name": "Administrateurs", "profile_code": "role.admin"},
        {"code": "grp.candidat", "name": "Candidats", "profile_code": "role.candidat"},
        {"code": "grp.company", "name": "Entreprises", "profile_code": "role.company"},
    ]
    
    for group_data in IAM_GROUPS:
        existing = await iam_groups_collection.find_one({"code": group_data["code"]})
        
        profile_id = iam_profile_map.get(group_data["profile_code"])
        
        if existing:
            print(f"  ⏭  {group_data['name']}")
        else:
            group_id = str(uuid.uuid4())
            group = {
                "id": group_id,
                "code": group_data["code"],
                "name": group_data["name"],
                "description": f"Groupe des {group_data['name'].lower()}",
                "profile_ids": [profile_id] if profile_id else [],
                "user_ids": [],
                "is_system_group": True,
                "is_protected": True,
                "parent_group_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await iam_groups_collection.insert_one(group)
            print(f"  ✅ {group_data['name']}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print(" ✅ INITIALISATION TERMINÉE")
    print("=" * 70)
    
    # Final count
    final_perm_count = await permissions_collection.count_documents({})
    final_iam_perm_count = await iam_permissions_collection.count_documents({})
    final_profile_count = await profiles_collection.count_documents({})
    final_iam_profile_count = await iam_profiles_collection.count_documents({})
    final_group_count = await iam_groups_collection.count_documents({})
    
    print(f"\n📊 État final:")
    print(f"   ✓ Permissions (Legacy): {final_perm_count}")
    print(f"   ✓ Permissions IAM: {final_iam_perm_count}")
    print(f"   ✓ Profils (Legacy): {final_profile_count}")
    print(f"   ✓ Profils IAM: {final_iam_profile_count}")
    print(f"   ✓ Groupes IAM: {final_group_count}")
    
    print("\n💡 Vérifiez l'interface IAM maintenant!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(force_initialize())
