#!/usr/bin/env python3
"""
Corriger l'accès aux besoins pour le profil commercial
"""
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from uuid import uuid4

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["auth_db"]

# Permissions nécessaires pour l'accès aux besoins
BESOINS_PERMISSIONS = [
    {"code": "besoins.read", "resource": "besoins", "action": "read", "scope": "base", "name": "Lire les besoins (base)", "category": "besoins"},
    {"code": "besoins.view.all", "resource": "besoins", "action": "view", "scope": "all", "name": "Voir tous les besoins", "category": "besoins"},
    {"code": "besoins.view.own", "resource": "besoins", "action": "view", "scope": "own", "name": "Voir ses besoins", "category": "besoins"},
]


def create_permission(perm_data):
    """Créer une permission si elle n'existe pas"""
    existing = db.permissions.find_one({"code": perm_data["code"]})
    if existing:
        print(f"  ⏭️  Permission '{perm_data['code']}' existe déjà - ID: {existing['id']}")
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
    print(f"  ✅ Permission '{perm_data['code']}' créée - ID: {permission['id']}")
    return permission["id"]


def update_commercial_profile():
    """Mettre à jour le profil commercial avec les permissions besoins"""
    print("\n🔄 Mise à jour du profil commercial...")
    
    profile = db.profiles.find_one({"code": "profile.commercial"})
    if not profile:
        print("❌ Profil commercial non trouvé")
        return
    
    current_permission_ids = profile.get("permission_ids", [])
    initial_count = len(current_permission_ids)
    
    for perm_data in BESOINS_PERMISSIONS:
        perm_id = create_permission(perm_data)
        if perm_id not in current_permission_ids:
            current_permission_ids.append(perm_id)
            print(f"  ➕ Ajout de {perm_data['code']}")
    
    db.profiles.update_one(
        {"code": "profile.commercial"},
        {
            "$set": {
                "permission_ids": current_permission_ids,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    added = len(current_permission_ids) - initial_count
    print(f"\n✅ Profil commercial mis à jour:")
    print(f"   Avant: {initial_count} permissions")
    print(f"   Après: {len(current_permission_ids)} permissions")
    print(f"   Ajoutées: {added} permissions")


def main():
    print("=" * 80)
    print("CORRECTION ACCÈS BESOINS POUR COMMERCIAL")
    print("=" * 80)
    print()
    
    update_commercial_profile()
    
    print()
    print("=" * 80)
    print("✅ Opération terminée!")
    print("=" * 80)


if __name__ == "__main__":
    main()
