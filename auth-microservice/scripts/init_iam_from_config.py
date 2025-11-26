#!/usr/bin/env python3
"""
Script d'initialisation IAM piloté par configuration (Config-Driven)
Source de vérité: /app/config/iam_config.yaml

Ce script:
- Lit toute la configuration depuis le fichier YAML
- Crée les permissions atomiques
- Crée les bundles
- Crée/Met à jour les profils système
- Crée le compte super_admin
- Aligne les utilisateurs existants

Usage:
  python3 init_iam_from_config.py
  python3 init_iam_from_config.py --delete-users
  python3 init_iam_from_config.py --config /path/to/custom_config.yaml
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
import argparse
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")
DEFAULT_CONFIG_FILE = Path(__file__).parent.parent / "config" / "iam_config.yaml"


def load_config(config_path=None):
    """Charge la configuration IAM depuis le fichier YAML"""
    config_file = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    
    if not config_file.exists():
        print(f"❌ Fichier de configuration non trouvé: {config_file}")
        sys.exit(1)
    
    print(f"📖 Chargement de la configuration depuis: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Valider la configuration
    required_sections = ['permissions', 'bundles', 'profiles']
    for section in required_sections:
        if section not in config:
            print(f"❌ Section manquante dans la configuration: {section}")
            sys.exit(1)
    
    return config


async def initialize_from_config(config, delete_users=False):
    """Initialise la base de données IAM depuis la configuration"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🔄 INITIALISATION IAM DEPUIS CONFIGURATION ({DB_NAME})")
    print("=" * 80)
    
    # 1. Nettoyer les permissions existantes
    print("\n1️⃣ Nettoyage des permissions existantes...")
    result = await db.permissions.delete_many({})
    print(f"   ✅ {result.deleted_count} permissions supprimées")
    
    # 2. Créer les permissions atomiques depuis la config
    permissions_config = config['permissions']
    print(f"\n2️⃣ Création des permissions atomiques ({len(permissions_config)})...")
    
    permissions_to_insert = []
    all_permission_codes = []
    
    for perm in permissions_config:
        perm_doc = {
            "id": str(uuid4()),
            "code": perm["code"],
            "name": perm["name"],
            "resource": perm["resource"],
            "action": perm["action"],
            "scope": perm.get("scope", "organization"),
            "category": perm.get("category", "general"),
            "description": perm.get("description"),
            "is_system": True,
            "is_atomic": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        permissions_to_insert.append(perm_doc)
        all_permission_codes.append(perm["code"])
    
    if permissions_to_insert:
        result = await db.permissions.insert_many(permissions_to_insert)
        print(f"   ✅ {len(result.inserted_ids)} permissions atomiques créées")
    
    # 3. Créer les bundles depuis la config
    bundles_config = config['bundles']
    print(f"\n3️⃣ Création des bundles de permissions ({len(bundles_config)})...")
    
    await db.permission_bundles.delete_many({})
    
    bundles_to_insert = []
    for bundle in bundles_config:
        bundle_doc = {
            "id": str(uuid4()),
            "code": bundle["code"],
            "name": bundle["name"],
            "description": bundle["description"],
            "category": bundle["category"],
            "permissions": bundle["permissions"],
            "is_system": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        bundles_to_insert.append(bundle_doc)
    
    if bundles_to_insert:
        result = await db.permission_bundles.insert_many(bundles_to_insert)
        print(f"   ✅ {len(result.inserted_ids)} bundles créés")
        for bundle in bundles_config:
            print(f"      • {bundle['code']}: {len(bundle['permissions'])} permissions")
    
    # 4. Créer/Mettre à jour les profils système depuis la config
    profiles_config = config['profiles']
    print(f"\n4️⃣ Création/Mise à jour des profils système ({len(profiles_config)})...")
    
    # Créer un mapping des bundles pour résolution rapide
    bundles_map = {b['code']: b['permissions'] for b in bundles_config}
    
    for profile in profiles_config:
        # Résoudre les permissions du profil
        if profile['permissions'] == "*":
            # Super Admin: toutes les permissions
            profile_permissions = all_permission_codes.copy()
        else:
            profile_permissions = profile['permissions'].copy() if profile['permissions'] else []
            
            # Ajouter les permissions des bundles
            for bundle_code in profile.get('bundles', []):
                if bundle_code in bundles_map:
                    profile_permissions.extend(bundles_map[bundle_code])
        
        # Supprimer les doublons
        profile_permissions = list(set(profile_permissions))
        
        profile_doc = {
            "id": str(uuid4()),
            "code": profile['code'],
            "name": profile['name'],
            "description": profile['description'],
            "permissions": profile_permissions,
            "bundles": profile.get('bundles', []),
            "is_protected": profile.get('is_protected', False),
            "is_system_role": True,
            "priority": profile.get('priority', 100),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert (update or insert)
        await db.profiles.update_one(
            {"code": profile['code']},
            {"$set": profile_doc},
            upsert=True
        )
        
        bundle_info = f" + {len(profile.get('bundles', []))} bundles" if profile.get('bundles') else ""
        print(f"   ✅ {profile['code']}: {len(profile_permissions)} permissions{bundle_info}")
    
    # 5. Créer les index
    print("\n5️⃣ Création des index...")
    try:
        await db.permissions.create_index([("code", 1)], unique=True, sparse=True)
        await db.permission_bundles.create_index([("code", 1)], unique=True)
        await db.profiles.create_index([("code", 1)], unique=True)
        print("   ✅ Index créés")
    except Exception as e:
        print(f"   ℹ️  Index déjà existants")
    
    # 6. Créer le compte super_admin
    print("\n6️⃣ Création du compte administrateur...")
    
    password = "Awana2025!"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Récupérer l'ID du profil super_admin
    super_admin_profile = await db.profiles.find_one({"code": "super_admin"}, {"id": 1, "_id": 0})
    
    admin_user = {
        "id": str(uuid4()),
        "username": "admin",
        "email": "admin@awana-group.com",
        "first_name": "Admin",
        "last_name": "System",
        "full_name": "Admin System",
        "password_hash": hashed.decode('utf-8'),
        "provider": "local",
        "roles": ["super_admin"],
        "profile_ids": [super_admin_profile["id"]] if super_admin_profile else [],
        "is_active": True,
        "is_verified": True,
        "email_verified": True,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.update_one(
        {"username": "admin"},
        {"$set": admin_user},
        upsert=True
    )
    print("   ✅ Compte 'admin' créé/réinitialisé")
    
    # 7. Aligner les utilisateurs existants selon les règles de validation
    print("\n7️⃣ Alignement des utilisateurs existants...")
    
    validation_rules = config.get('user_validation_rules', {})
    field_migrations = validation_rules.get('field_migrations', {})
    default_values = validation_rules.get('default_values', {})
    active_requirements = validation_rules.get('active_user_requirements', {})
    
    # Migration password → password_hash
    if 'password' in field_migrations:
        result = await db.users.update_many(
            {"password": {"$exists": True}},
            {
                "$rename": {"password": "password_hash"},
                "$set": {
                    "provider": default_values.get("provider", "local"),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        if result.modified_count > 0:
            print(f"   ✅ {result.modified_count} utilisateur(s) migré(s) (password → password_hash)")
    
    # Ajouter provider pour les utilisateurs qui n'en ont pas
    result = await db.users.update_many(
        {"provider": {"$exists": False}},
        {"$set": {"provider": default_values.get("provider", "local")}}
    )
    if result.modified_count > 0:
        print(f"   ✅ {result.modified_count} utilisateur(s) mis à jour (provider ajouté)")
    
    # Activer les comptes super_admin inactifs
    if active_requirements:
        result = await db.users.update_many(
            {
                "roles": "super_admin",
                "$or": [
                    {"status": {"$ne": active_requirements.get("status")}},
                    {"is_active": {"$ne": active_requirements.get("is_active")}}
                ]
            },
            {
                "$set": {
                    **active_requirements,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        if result.modified_count > 0:
            print(f"   ✅ {result.modified_count} compte(s) super_admin activé(s)")
    
    # 8. Supprimer les utilisateurs de test si demandé
    if delete_users:
        print("\n8️⃣ Suppression des utilisateurs de test...")
        result = await db.users.delete_many({"username": {"$nin": ["admin", "adminbe"]}})
        print(f"   ✅ {result.deleted_count} utilisateurs supprimés")
    
    # 9. Vérification finale
    print("\n9️⃣ Vérification finale...")
    perm_count = await db.permissions.count_documents({})
    bundle_count = await db.permission_bundles.count_documents({})
    profile_count = await db.profiles.count_documents({"is_system_role": True})
    user_count = await db.users.count_documents({})
    
    print(f"   📊 Permissions atomiques: {perm_count}")
    print(f"   📊 Bundles: {bundle_count}")
    print(f"   📊 Profils système: {profile_count}")
    print(f"   📊 Utilisateurs: {user_count}")
    
    client.close()
    
    # Résumé final
    print("\n" + "=" * 80)
    print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 80)
    print("\n🔑 Identifiants SuperAdmin:")
    print("   Username: admin")
    print("   Email: admin@awana-group.com")
    print("   Password: Awana2025!")
    print(f"\n📊 Système de permissions:")
    print(f"   - {perm_count} permissions atomiques")
    print(f"   - {bundle_count} bundles de permissions")
    print(f"   - {profile_count} profils système avec permissions appropriées")
    print("\n💡 Profils créés/mis à jour:")
    for profile in profiles_config:
        print(f"   - {profile['code']}: {profile['name']}")
    print("\n📖 Configuration:")
    print(f"   - Source: {DEFAULT_CONFIG_FILE}")
    print("   - Format: YAML (config-driven)")
    print("\n💡 Prochaines étapes:")
    print("   1. Vérifier les utilisateurs: python3 verify_and_align_users.py")
    print("   2. Corriger si nécessaire: python3 verify_and_align_users.py --fix")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialisation IAM depuis configuration YAML"
    )
    parser.add_argument(
        "--delete-users",
        action="store_true",
        help="Supprimer TOUS les utilisateurs (sauf admin/adminbe)"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Chemin vers un fichier de configuration personnalisé"
    )
    
    args = parser.parse_args()
    
    if args.delete_users:
        print("\n⚠️  ATTENTION: Cette option va supprimer TOUS les utilisateurs de test!")
        confirm = input("Tapez 'OUI' pour confirmer: ")
        if confirm != "OUI":
            print("❌ Opération annulée")
            sys.exit(0)
    
    # Charger la configuration
    config = load_config(args.config)
    
    # Exécuter l'initialisation
    asyncio.run(initialize_from_config(config, delete_users=args.delete_users))
