#!/usr/bin/env python3
"""
Ajouter les permissions de base manquantes identifiées dans les routes
"""
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from uuid import uuid4

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["auth_db"]

# Permissions de base nécessaires pour les routes
BASE_PERMISSIONS = [
    # Missions - permissions de base
    {"code": "missions.read", "resource": "missions", "action": "read", "scope": "base", "name": "Lire les missions (base)", "category": "missions"},
    {"code": "missions.manage", "resource": "missions", "action": "manage", "scope": "base", "name": "Gérer les missions (base)", "category": "missions"},
    
    # Applications/Candidatures
    {"code": "applications.manage", "resource": "applications", "action": "manage", "scope": "base", "name": "Gérer les candidatures (base)", "category": "applications"},
    
    # Admin
    {"code": "admin.dashboard", "resource": "admin", "action": "dashboard", "scope": "base", "name": "Dashboard admin", "category": "admin"},
    {"code": "admin.access", "resource": "admin", "action": "access", "scope": "base", "name": "Accès admin", "category": "admin"},
    {"code": "admin.settings", "resource": "admin", "action": "settings", "scope": "base", "name": "Paramètres admin", "category": "admin"},
    
    # Users
    {"code": "users.read", "resource": "users", "action": "read", "scope": "base", "name": "Lire les utilisateurs (base)", "category": "users"},
    {"code": "users.manage", "resource": "users", "action": "manage", "scope": "base", "name": "Gérer les utilisateurs (base)", "category": "users"},
    {"code": "users.create", "resource": "users", "action": "create", "scope": "base", "name": "Créer des utilisateurs", "category": "users"},
    
    # Validations
    {"code": "validations.manage", "resource": "validations", "action": "manage", "scope": "base", "name": "Gérer les validations", "category": "validations"},
    
    # Entreprises
    {"code": "entreprises.read", "resource": "entreprises", "action": "read", "scope": "base", "name": "Lire les entreprises (base)", "category": "entreprises"},
    {"code": "entreprises.manage", "resource": "entreprises", "action": "manage", "scope": "base", "name": "Gérer les entreprises (base)", "category": "entreprises"},
    
    # Locations
    {"code": "locations.manage", "resource": "locations", "action": "manage", "scope": "base", "name": "Gérer les localisations", "category": "locations"},
    
    # References
    {"code": "references.manage", "resource": "references", "action": "manage", "scope": "base", "name": "Gérer les référentiels", "category": "references"},
    
    # Rules
    {"code": "rules.manage", "resource": "rules", "action": "manage", "scope": "base", "name": "Gérer les règles métier", "category": "rules"},
    
    # Config
    {"code": "config.manage", "resource": "config", "action": "manage", "scope": "base", "name": "Gérer la configuration", "category": "config"},
    
    # Flags
    {"code": "flags.manage", "resource": "flags", "action": "manage", "scope": "base", "name": "Gérer les feature flags", "category": "flags"},
    
    # Emails
    {"code": "emails.read_history", "resource": "emails", "action": "read_history", "scope": "base", "name": "Lire l'historique emails", "category": "emails"},
    {"code": "emails.manage_templates", "resource": "emails", "action": "manage_templates", "scope": "base", "name": "Gérer les templates emails", "category": "emails"},
    
    # IAM
    {"code": "iam.profiles.manage", "resource": "iam", "action": "manage", "scope": "profiles", "name": "Gérer les profils IAM", "category": "iam"},
    {"code": "iam.groups.manage", "resource": "iam", "action": "manage", "scope": "groups", "name": "Gérer les groupes IAM", "category": "iam"},
]

# Permissions additionnelles pour le profil commercial
COMMERCIAL_ADDITIONAL_PERMISSIONS = [
    "missions.read",
    "applications.manage",
]


def create_permission(perm_data):
    """Créer une permission si elle n'existe pas"""
    existing = db.permissions.find_one({"code": perm_data["code"]})
    if existing:
        print(f"  ⏭️  Permission '{perm_data['code']}' existe déjà")
        return existing["id"]
    
    now = datetime.now(timezone.utc).isoformat()
    permission = {
        "id": str(uuid4()),
        "code": perm_data["code"],
        "name": perm_data["name"],
        "description": perm_data.get("description", f"Permission {perm_data['code']}"),
        "resource": perm_data["resource"],
        "action": perm_data["action"],
        "scope": perm_data["scope"],
        "is_system": True,
        "category": perm_data["category"],
        "created_at": now,
        "updated_at": now
    }
    
    db.permissions.insert_one(permission)
    print(f"  ✅ Permission '{perm_data['code']}' créée")
    return permission["id"]


def update_commercial_profile():
    """Mettre à jour le profil commercial avec les permissions nécessaires"""
    print("\n🔄 Mise à jour du profil commercial...")
    
    profile = db.profiles.find_one({"code": "profile.commercial"})
    if not profile:
        print("❌ Profil commercial non trouvé")
        return
    
    # Récupérer les IDs des permissions additionnelles
    current_permission_ids = profile.get("permission_ids", [])
    
    for perm_code in COMMERCIAL_ADDITIONAL_PERMISSIONS:
        perm = db.permissions.find_one({"code": perm_code})
        if perm and perm["id"] not in current_permission_ids:
            current_permission_ids.append(perm["id"])
            print(f"  ➕ Ajout de {perm_code}")
    
    # Mettre à jour le profil
    db.profiles.update_one(
        {"code": "profile.commercial"},
        {
            "$set": {
                "permission_ids": current_permission_ids,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    print(f"✅ Profil commercial mis à jour avec {len(current_permission_ids)} permissions")


def main():
    print("=" * 80)
    print("AJOUT DES PERMISSIONS DE BASE")
    print("=" * 80)
    print()
    
    created = 0
    skipped = 0
    
    for perm_data in BASE_PERMISSIONS:
        perm_id = create_permission(perm_data)
        if perm_id:
            created += 1 if "créée" in str(perm_id) or isinstance(perm_id, str) and len(perm_id) > 10 else 0
        else:
            skipped += 1
    
    # Mettre à jour le profil commercial
    update_commercial_profile()
    
    print()
    print("=" * 80)
    print("RAPPORT")
    print("=" * 80)
    print(f"✅ Permissions créées: {created}")
    print(f"⏭️  Permissions existantes: {skipped}")
    print(f"📊 Total traité: {len(BASE_PERMISSIONS)}")
    print()
    print("✅ Opération terminée!")
    print("=" * 80)


if __name__ == "__main__":
    main()
