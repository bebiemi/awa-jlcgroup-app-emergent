#!/usr/bin/env python3
"""
Créer les permissions IAM manquantes identifiées lors de la migration
"""
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from uuid import uuid4

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["auth_db"]

# Liste des permissions manquantes identifiées
MISSING_PERMISSIONS = [
    # Dashboard
    {"code": "dashboard.admin.access", "resource": "dashboard", "action": "access", "scope": "admin", "name": "Accès dashboard admin", "category": "dashboard"},
    {"code": "dashboard.commercial.access", "resource": "dashboard", "action": "access", "scope": "commercial", "name": "Accès dashboard commercial", "category": "dashboard"},
    {"code": "dashboard.company.access", "resource": "dashboard", "action": "access", "scope": "company", "name": "Accès dashboard entreprise", "category": "dashboard"},
    {"code": "dashboard.candidat.access", "resource": "dashboard", "action": "access", "scope": "candidat", "name": "Accès dashboard candidat", "category": "dashboard"},
    
    # Users
    {"code": "users.read.all", "resource": "users", "action": "read", "scope": "all", "name": "Lire tous les utilisateurs", "category": "users"},
    {"code": "users.edit.all", "resource": "users", "action": "edit", "scope": "all", "name": "Modifier tous les utilisateurs", "category": "users"},
    {"code": "users.manage_status.all", "resource": "users", "action": "manage_status", "scope": "all", "name": "Gérer le statut des utilisateurs", "category": "users"},
    {"code": "users.reset_mfa.all", "resource": "users", "action": "reset_mfa", "scope": "all", "name": "Réinitialiser MFA des utilisateurs", "category": "users"},
    
    # Besoins
    {"code": "besoins.read.all", "resource": "besoins", "action": "read", "scope": "all", "name": "Lire tous les besoins", "category": "besoins"},
    {"code": "besoins.read.own", "resource": "besoins", "action": "read", "scope": "own", "name": "Lire ses besoins", "category": "besoins"},
    {"code": "besoins.validate.all", "resource": "besoins", "action": "validate", "scope": "all", "name": "Valider tous les besoins", "category": "besoins"},
    {"code": "besoins.submit.own", "resource": "besoins", "action": "submit", "scope": "own", "name": "Soumettre ses besoins", "category": "besoins"},
    {"code": "besoins.comment.all", "resource": "besoins", "action": "comment", "scope": "all", "name": "Commenter tous les besoins", "category": "besoins"},
    
    # Entreprises
    {"code": "entreprises.read.all", "resource": "entreprises", "action": "read", "scope": "all", "name": "Lire toutes les entreprises", "category": "entreprises"},
    {"code": "entreprises.create.own", "resource": "entreprises", "action": "create", "scope": "own", "name": "Créer son entreprise", "category": "entreprises"},
    
    # Validations
    {"code": "validations.manage.all", "resource": "validations", "action": "manage", "scope": "all", "name": "Gérer toutes les validations", "category": "validations"},
    
    # IAM
    {"code": "iam.profiles.edit", "resource": "iam", "action": "edit", "scope": "profiles", "name": "Modifier les profils IAM", "category": "iam"},
    {"code": "iam.groups.edit", "resource": "iam", "action": "edit", "scope": "groups", "name": "Modifier les groupes IAM", "category": "iam"},
    
    # Profile
    {"code": "profile.read.own", "resource": "profile", "action": "read", "scope": "own", "name": "Lire son profil", "category": "profile"},
    {"code": "profile.read.all", "resource": "profile", "action": "read", "scope": "all", "name": "Lire tous les profils", "category": "profile"},
    
    # Applications
    {"code": "applications.edit.own", "resource": "applications", "action": "edit", "scope": "own", "name": "Modifier ses candidatures", "category": "applications"},
]


def create_permission(perm_data):
    """Créer une permission si elle n'existe pas"""
    existing = db.permissions.find_one({"code": perm_data["code"]})
    if existing:
        print(f"  ⏭️  Permission '{perm_data['code']}' existe déjà")
        return False
    
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
    return True


def main():
    print("=" * 80)
    print("CRÉATION DES PERMISSIONS IAM MANQUANTES")
    print("=" * 80)
    print()
    
    created = 0
    skipped = 0
    
    for perm_data in MISSING_PERMISSIONS:
        if create_permission(perm_data):
            created += 1
        else:
            skipped += 1
    
    print()
    print("=" * 80)
    print("RAPPORT")
    print("=" * 80)
    print(f"✅ Permissions créées: {created}")
    print(f"⏭️  Permissions existantes: {skipped}")
    print(f"📊 Total traité: {len(MISSING_PERMISSIONS)}")
    print()
    print("✅ Opération terminée!")
    print("=" * 80)


if __name__ == "__main__":
    main()
