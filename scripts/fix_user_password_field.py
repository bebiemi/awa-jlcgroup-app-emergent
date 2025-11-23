#!/usr/bin/env python3
"""
Script de correction des champs de mot de passe dans la base de données
Corrige les utilisateurs qui ont 'password' au lieu de 'password_hash'
Active également les comptes super_admin inactifs
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")


async def fix_password_fields():
    """Corrige les champs password → password_hash et active les comptes admin"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print("🔧 CORRECTION DES CHAMPS DE MOT DE PASSE")
    print("=" * 80)
    
    # 1. Trouver les utilisateurs avec 'password' au lieu de 'password_hash'
    print("\n1️⃣ Recherche des utilisateurs avec champ 'password'...")
    users_with_password = await db.users.find(
        {"password": {"$exists": True}},
        {"username": 1, "password": 1, "_id": 0}
    ).to_list(length=100)
    
    print(f"   Trouvés: {len(users_with_password)} utilisateur(s)")
    for user in users_with_password:
        print(f"   - {user['username']}")
    
    if users_with_password:
        # 2. Renommer 'password' en 'password_hash'
        print("\n2️⃣ Renommage de 'password' en 'password_hash'...")
        result = await db.users.update_many(
            {"password": {"$exists": True}},
            {
                "$rename": {"password": "password_hash"},
                "$set": {
                    "provider": "local",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        print(f"   ✅ {result.modified_count} utilisateur(s) corrigé(s)")
    else:
        print("   ✅ Aucune correction nécessaire")
    
    # 3. Ajouter le provider pour les utilisateurs qui n'en ont pas
    print("\n3️⃣ Ajout du provider 'local' pour les utilisateurs sans provider...")
    result = await db.users.update_many(
        {"provider": {"$exists": False}},
        {"$set": {"provider": "local"}}
    )
    print(f"   ✅ {result.modified_count} utilisateur(s) mis à jour")
    
    # 4. Activer les comptes super_admin qui sont inactifs
    print("\n4️⃣ Activation des comptes super_admin inactifs...")
    result = await db.users.update_many(
        {
            "roles": "super_admin",
            "$or": [
                {"status": {"$ne": "active"}},
                {"is_active": {"$ne": True}}
            ]
        },
        {
            "$set": {
                "status": "active",
                "is_active": True,
                "is_verified": True,
                "email_verified": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    print(f"   ✅ {result.modified_count} compte(s) super_admin activé(s)")
    
    # 5. Vérification finale
    print("\n5️⃣ Vérification finale...")
    
    # Vérifier que tous les utilisateurs ont password_hash
    users_without_password_hash = await db.users.count_documents({
        "password_hash": {"$exists": False},
        "provider": "local"
    })
    
    if users_without_password_hash > 0:
        print(f"   ⚠️ {users_without_password_hash} utilisateur(s) local sans password_hash")
    else:
        print("   ✅ Tous les utilisateurs locaux ont password_hash")
    
    # Vérifier les comptes super_admin
    super_admins = await db.users.find(
        {"roles": "super_admin"},
        {"username": 1, "status": 1, "is_active": 1, "password_hash": 1, "_id": 0}
    ).to_list(length=10)
    
    print(f"\n   📋 Comptes super_admin ({len(super_admins)}):")
    for admin in super_admins:
        status_icon = "✅" if admin.get("status") == "active" and admin.get("is_active") else "❌"
        pwd_icon = "✅" if admin.get("password_hash") else "❌"
        print(f"   {status_icon} {admin['username']} - Status: {admin.get('status')} - Password: {pwd_icon}")
    
    client.close()
    
    print("\n" + "=" * 80)
    print("✅ CORRECTION TERMINÉE!")
    print("=" * 80)
    print("\n💡 Les utilisateurs peuvent maintenant se connecter avec leurs identifiants.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(fix_password_fields())
