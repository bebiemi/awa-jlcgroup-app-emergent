"""
Script pour créer les permissions IAM avancées pour la gestion des entreprises
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from uuid import uuid4
import os

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = 'auth_db'

async def create_entreprise_advanced_permissions():
    """Créer les permissions IAM avancées pour les entreprises"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    permissions = [
        {
            "id": str(uuid4()),
            "code": "entreprises.manage",
            "name": "Gérer les entreprises",
            "description": "Permet de gérer complètement les entreprises (création, modification, suppression, invitation)",
            "resource": "entreprises",
            "action": "manage",
            "scope": "global",
            "is_system": True,
            "category": "entreprises",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "entreprises.invite_user",
            "name": "Inviter des utilisateurs entreprise",
            "description": "Permet d'inviter des utilisateurs à rejoindre une entreprise",
            "resource": "entreprises",
            "action": "invite_user",
            "scope": "own",
            "is_system": True,
            "category": "entreprises",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "forms.enterprise.manage",
            "name": "Gérer la configuration des formulaires entreprise",
            "description": "Permet de gérer la configuration dynamique des champs entreprise",
            "resource": "forms",
            "action": "manage",
            "scope": "global",
            "is_system": True,
            "category": "configuration",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "forms.enterprise.update",
            "name": "Modifier la configuration des formulaires entreprise",
            "description": "Permet de modifier les configurations de champs entreprise existants",
            "resource": "forms",
            "action": "update",
            "scope": "global",
            "is_system": True,
            "category": "configuration",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
    ]
    
    print("🔐 Création des permissions IAM avancées pour les entreprises...")
    
    for perm in permissions:
        # Vérifier si la permission existe déjà
        existing = await db.permissions.find_one({"code": perm["code"]})
        if existing:
            print(f"  ℹ️  Permission '{perm['code']}' existe déjà")
        else:
            await db.permissions.insert_one(perm)
            print(f"  ✅ Permission '{perm['code']}' créée")
    
    # Ajouter les permissions au profil Administrateur
    print("\n📋 Ajout des permissions au profil Administrateur...")
    admin_profile = await db.profiles.find_one({"code": "admin"})
    
    if admin_profile:
        permission_ids = [p["id"] for p in permissions]
        existing_permissions = admin_profile.get("permission_ids", [])
        new_permissions = list(set(existing_permissions + permission_ids))
        
        await db.profiles.update_one(
            {"code": "admin"},
            {
                "$set": {
                    "permission_ids": new_permissions,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        print(f"  ✅ {len(permission_ids)} permissions ajoutées au profil Administrateur")
    else:
        print("  ⚠️  Profil Administrateur non trouvé")
    
    # Vérifier et désactiver les permissions legacy si nécessaire
    print("\n🔍 Vérification des permissions legacy...")
    legacy_perms = ["voir_entreprises", "modifier_entreprises", "supprimer_entreprises"]
    
    for legacy_code in legacy_perms:
        legacy = await db.permissions.find_one({"code": legacy_code})
        if legacy:
            # Marquer comme legacy/deprecated
            await db.permissions.update_one(
                {"code": legacy_code},
                {
                    "$set": {
                        "is_deprecated": True,
                        "is_system": False,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            print(f"  ⚠️  Permission legacy '{legacy_code}' marquée comme deprecated")
    
    print("\n✅ Script terminé avec succès!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_entreprise_advanced_permissions())
