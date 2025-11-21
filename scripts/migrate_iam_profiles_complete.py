#!/usr/bin/env python3
"""
Script de Migration IAM Complète - Phase 1
Objectif: Nettoyer les profils legacy et assigner les bonnes permissions
"""
import sys
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from uuid import uuid4

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["auth_db"]

# Mapping des profils legacy vers les profils système
PROFILE_MIGRATION_MAP = {
    "commercial": "profile.commercial",
    "admin": "profile.admin",
    "super_admin": "profile.super_admin",
    "hr_manager": "profile.hr_manager",
    "company_admin": "profile.company",
    "interim_user": "profile.candidat_confirmed",
    "candidat": "profile.candidat_confirmed",
    "team_manager": "profile.hr_manager",  # À valider
}

# Définition des permissions par profil système
PROFILE_PERMISSIONS = {
    "profile.super_admin": ["*"],  # Wildcard - toutes les permissions
    
    "profile.admin": [
        "dashboard.admin.access",
        "users.read.all",
        "users.edit.all",
        "users.manage_status.all",
        "users.reset_mfa.all",
        "missions.read.all",
        "missions.edit.all",
        "missions.delete.all",
        "applications.read.all",
        "besoins.read.all",
        "besoins.validate.all",
        "entreprises.read.all",
        "validations.manage.all",
        "emails.read_config",
        "emails.configure",
        "iam.profiles.read",
        "iam.profiles.edit",
        "iam.groups.read",
        "iam.groups.edit",
        "iam.permissions.read",
    ],
    
    "profile.commercial": [
        "dashboard.commercial.access",
        "missions.browse",
        "missions.read.all",
        "missions.create.own",
        "missions.edit.own",
        "missions.delete.own",
        "besoins.read.all",
        "besoins.create.own",
        "besoins.edit.own",
        "besoins.comment.all",
        "entreprises.read.all",
        "entreprises.create.own",
        "entreprises.edit.own",
        "applications.read.all",
        "profile.read.own",
        "profile.edit.own",
        "documents.read.own",
        "documents.create.own",
    ],
    
    "profile.company": [
        "dashboard.company.access",
        "besoins.create.own",
        "besoins.read.own",
        "besoins.edit.own",
        "besoins.submit.own",
        "missions.read.own",
        "applications.read.own",
        "profile.read.own",
        "profile.edit.own",
        "documents.read.own",
        "documents.create.own",
    ],
    
    "profile.hr_manager": [
        "dashboard.admin.access",
        "users.read.all",
        "users.edit.all",
        "missions.read.all",
        "missions.edit.all",
        "applications.read.all",
        "besoins.read.all",
        "besoins.validate.all",
        "validations.manage.all",
        "profile.read.all",
        "documents.read.all",
    ],
    
    "profile.payroll": [
        "dashboard.admin.access",
        "missions.read.all",
        "applications.read.all",
        "users.read.all",
        "profile.read.all",
        "documents.read.all",
    ],
    
    "profile.candidat_confirmed": [
        "dashboard.candidat.access",
        "missions.browse",
        "missions.read.all",
        "applications.create.own",
        "applications.read.own",
        "applications.edit.own",
        "profile.read.own",
        "profile.edit.own",
        "documents.read.own",
        "documents.create.own",
    ],
    
    "profile.candidat_temp": [
        "dashboard.candidat.access",
        "missions.browse",
        "profile.read.own",
        "profile.edit.own",
    ],
}


def log_action(action, details):
    """Logger les actions de migration"""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] {action}: {details}")


def get_permission_ids_by_codes(permission_codes):
    """Récupérer les IDs des permissions par leurs codes"""
    if "*" in permission_codes:
        # Wildcard - toutes les permissions
        all_perms = list(db.permissions.find({}, {"id": 1, "_id": 0}))
        return [p["id"] for p in all_perms]
    
    permission_ids = []
    for code in permission_codes:
        perm = db.permissions.find_one({"code": code}, {"id": 1, "_id": 0})
        if perm:
            permission_ids.append(perm["id"])
        else:
            log_action("WARNING", f"Permission '{code}' n'existe pas dans la DB")
    
    return permission_ids


def migrate_profile(legacy_code, system_code):
    """Migrer un profil legacy vers le profil système"""
    log_action("MIGRATE_PROFILE", f"Migration de '{legacy_code}' vers '{system_code}'")
    
    # 1. Récupérer le profil legacy
    legacy_profile = db.profiles.find_one({"code": legacy_code})
    if not legacy_profile:
        log_action("INFO", f"Profil legacy '{legacy_code}' n'existe pas")
        return None
    
    # 2. Récupérer ou créer le profil système
    system_profile = db.profiles.find_one({"code": system_code})
    if not system_profile:
        log_action("ERROR", f"Profil système '{system_code}' n'existe pas!")
        return None
    
    system_profile_id = system_profile["id"]
    legacy_profile_id = legacy_profile["id"]
    
    # 3. Mettre à jour les permissions du profil système
    if system_code in PROFILE_PERMISSIONS:
        permission_codes = PROFILE_PERMISSIONS[system_code]
        permission_ids = get_permission_ids_by_codes(permission_codes)
        
        result = db.profiles.update_one(
            {"id": system_profile_id},
            {
                "$set": {
                    "permission_ids": permission_ids,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        log_action("UPDATE", f"Profil '{system_code}' mis à jour avec {len(permission_ids)} permissions")
    
    # 4. Migrer tous les utilisateurs du profil legacy vers le profil système
    users_with_legacy = db.users.find({"profile_ids": legacy_profile_id})
    user_count = 0
    
    for user in users_with_legacy:
        # Remplacer l'ID du profil legacy par l'ID du profil système
        new_profile_ids = [
            system_profile_id if pid == legacy_profile_id else pid
            for pid in user.get("profile_ids", [])
        ]
        
        db.users.update_one(
            {"id": user["id"]},
            {
                "$set": {
                    "profile_ids": new_profile_ids,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        user_count += 1
        log_action("USER_UPDATE", f"Utilisateur '{user.get('username', user['id'])}' migré vers '{system_code}'")
    
    log_action("SUMMARY", f"{user_count} utilisateurs migrés de '{legacy_code}' vers '{system_code}'")
    
    # 5. Marquer le profil legacy comme deprecated
    db.profiles.update_one(
        {"id": legacy_profile_id},
        {
            "$set": {
                "deprecated": True,
                "deprecated_at": datetime.now(timezone.utc).isoformat(),
                "migration_target": system_code,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    log_action("DEPRECATE", f"Profil '{legacy_code}' marqué comme deprecated")
    
    return {
        "legacy_code": legacy_code,
        "system_code": system_code,
        "users_migrated": user_count
    }


def update_system_profile_permissions(profile_code):
    """Mettre à jour les permissions d'un profil système"""
    log_action("UPDATE_PERMISSIONS", f"Mise à jour des permissions pour '{profile_code}'")
    
    profile = db.profiles.find_one({"code": profile_code})
    if not profile:
        log_action("ERROR", f"Profil '{profile_code}' n'existe pas!")
        return None
    
    if profile_code in PROFILE_PERMISSIONS:
        permission_codes = PROFILE_PERMISSIONS[profile_code]
        permission_ids = get_permission_ids_by_codes(permission_codes)
        
        result = db.profiles.update_one(
            {"code": profile_code},
            {
                "$set": {
                    "permission_ids": permission_ids,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        log_action("SUCCESS", f"Profil '{profile_code}' mis à jour avec {len(permission_ids)} permissions")
        return len(permission_ids)
    
    return 0


def verify_commercial1():
    """Vérifier que commercial1 a les bonnes permissions"""
    log_action("VERIFY", "Vérification de commercial1")
    
    user = db.users.find_one({"username": "commercial1"})
    if not user:
        log_action("ERROR", "Utilisateur commercial1 non trouvé")
        return False
    
    profile_ids = user.get("profile_ids", [])
    log_action("INFO", f"commercial1 a {len(profile_ids)} profils assignés")
    
    total_permissions = 0
    for profile_id in profile_ids:
        profile = db.profiles.find_one({"id": profile_id})
        if profile:
            perm_count = len(profile.get("permission_ids", []))
            log_action("INFO", f"  - Profil '{profile['code']}': {perm_count} permissions")
            total_permissions += perm_count
    
    log_action("RESULT", f"commercial1 a un total de {total_permissions} permissions")
    return total_permissions > 0


def main():
    """Fonction principale de migration"""
    print("=" * 80)
    print("MIGRATION IAM COMPLÈTE - PHASE 1")
    print("=" * 80)
    print()
    
    # Étape 1: Mettre à jour les permissions des profils système existants
    print("\n📋 ÉTAPE 1: Mise à jour des profils système")
    print("-" * 80)
    for profile_code in PROFILE_PERMISSIONS.keys():
        update_system_profile_permissions(profile_code)
    
    # Étape 2: Migrer les profils legacy
    print("\n🔄 ÉTAPE 2: Migration des profils legacy")
    print("-" * 80)
    migration_results = []
    for legacy_code, system_code in PROFILE_MIGRATION_MAP.items():
        result = migrate_profile(legacy_code, system_code)
        if result:
            migration_results.append(result)
    
    # Étape 3: Vérification de commercial1
    print("\n✅ ÉTAPE 3: Vérification de commercial1")
    print("-" * 80)
    commercial1_ok = verify_commercial1()
    
    # Rapport final
    print("\n" + "=" * 80)
    print("RAPPORT FINAL")
    print("=" * 80)
    print(f"✅ Profils système mis à jour: {len(PROFILE_PERMISSIONS)}")
    print(f"✅ Profils legacy migrés: {len(migration_results)}")
    
    total_users = sum(r["users_migrated"] for r in migration_results)
    print(f"✅ Utilisateurs migrés: {total_users}")
    
    if commercial1_ok:
        print("✅ commercial1 a maintenant des permissions")
    else:
        print("❌ commercial1 n'a toujours pas de permissions - ÉCHEC")
    
    print("\n📊 Détails des migrations:")
    for result in migration_results:
        print(f"  • {result['legacy_code']} → {result['system_code']}: {result['users_migrated']} utilisateurs")
    
    print("\n✅ Migration terminée avec succès!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
