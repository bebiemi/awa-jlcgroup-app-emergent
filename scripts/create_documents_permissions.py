"""
Script pour créer les permissions IAM pour la gestion des documents
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from uuid import uuid4
import os

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = 'auth_db'

async def create_documents_permissions():
    """Créer les permissions IAM pour les documents"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    permissions = [
        {
            "id": str(uuid4()),
            "code": "documents.create",
            "name": "Créer des documents",
            "description": "Permet de créer et uploader des documents",
            "resource": "documents",
            "action": "create",
            "scope": "own",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "documents.read",
            "name": "Consulter ses documents",
            "description": "Permet de consulter ses propres documents",
            "resource": "documents",
            "action": "read",
            "scope": "own",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "documents.read.all",
            "name": "Consulter tous les documents",
            "description": "Permet de consulter tous les documents (admin)",
            "resource": "documents",
            "action": "read",
            "scope": "global",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "documents.update",
            "name": "Modifier ses documents",
            "description": "Permet de modifier ses propres documents",
            "resource": "documents",
            "action": "update",
            "scope": "own",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "documents.delete",
            "name": "Supprimer ses documents",
            "description": "Permet de supprimer ses propres documents",
            "resource": "documents",
            "action": "delete",
            "scope": "own",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "documents.verify",
            "name": "Vérifier les documents",
            "description": "Permet de vérifier et approuver les documents",
            "resource": "documents",
            "action": "verify",
            "scope": "global",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "code": "documents.download",
            "name": "Télécharger des documents",
            "description": "Permet de télécharger des documents",
            "resource": "documents",
            "action": "download",
            "scope": "own",
            "is_system": True,
            "category": "documents",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
    ]
    
    print("🔐 Création des permissions IAM pour les documents...")
    
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
    
    # Ajouter les permissions de base (read, create, update, delete, download) aux profils utilisateurs
    print("\n📋 Ajout des permissions de base aux profils utilisateurs...")
    base_permission_codes = ["documents.create", "documents.read", "documents.update", "documents.delete", "documents.download"]
    base_permission_ids = [p["id"] for p in permissions if p["code"] in base_permission_codes]
    
    user_profile_codes = ["intérimaire", "candidat", "company_manager", "collaborator"]
    
    for profile_code in user_profile_codes:
        profile = await db.profiles.find_one({"code": profile_code})
        if profile:
            existing_permissions = profile.get("permission_ids", [])
            new_permissions = list(set(existing_permissions + base_permission_ids))
            
            await db.profiles.update_one(
                {"code": profile_code},
                {
                    "$set": {
                        "permission_ids": new_permissions,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            print(f"  ✅ Permissions ajoutées au profil '{profile_code}'")
        else:
            print(f"  ℹ️  Profil '{profile_code}' non trouvé")
    
    print("\n✅ Script terminé avec succès!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_documents_permissions())
