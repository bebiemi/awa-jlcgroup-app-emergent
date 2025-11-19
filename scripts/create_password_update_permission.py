"""
Script pour créer la permission users.password.update
Permet aux admins/super-admins de modifier le mot de passe des utilisateurs
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.auth_db


async def create_permission():
    """Créer la permission users.password.update"""
    
    print("🔐 Création de la permission users.password.update...")
    
    permission = {
        "id": str(uuid.uuid4()),
        "code": "users.password.update",
        "name": "Modifier les mots de passe utilisateurs",
        "description": "Permet de modifier le mot de passe d'un utilisateur (admin/super-admin uniquement)",
        "category": "users",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Vérifier si la permission existe déjà
    existing = await db.iam_permissions.find_one({"code": permission["code"]})
    
    if existing:
        print(f"  ⚠️  Permission '{permission['code']}' existe déjà")
        return
    
    await db.iam_permissions.insert_one(permission)
    print(f"  ✅ Permission '{permission['code']}' créée")
    
    # Assigner la permission au rôle admin
    print("\n🔄 Attribution de la permission au rôle admin...")
    
    admin_role = await db.iam_roles.find_one({"code": "admin"})
    
    if admin_role:
        result = await db.iam_roles.update_one(
            {"code": "admin"},
            {
                "$addToSet": {
                    "permissions": "users.password.update"
                },
                "$set": {
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        print(f"✅ Permission ajoutée au rôle admin")
    else:
        print("⚠️  Rôle admin non trouvé")


async def main():
    try:
        print("=" * 80)
        print("🚀 CRÉATION PERMISSION : users.password.update")
        print("=" * 80)
        
        await create_permission()
        
        print("\n" + "=" * 80)
        print("🎉 TERMINÉ")
        print("=" * 80)
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
