"""
Script pour créer les permissions de rattachement d'entreprise
Phase 3: Workflow de rattachement
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


async def create_permissions():
    """Créer les permissions de rattachement et regroupement"""
    
    print("🔐 Création des permissions de rattachement/regroupement...")
    
    permissions = [
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.validate",
            "name": "Valider les comptes entreprises",
            "description": "Permet de valider ou rejeter les demandes d'inscription des entreprises",
            "category": "entreprises",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.link_existing",
            "name": "Rattacher à un client existant",
            "description": "Permet de rattacher une nouvelle entreprise à un représentant légal existant",
            "category": "entreprises",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.group_request",
            "name": "Demander un regroupement",
            "description": "Permet de demander le regroupement de deux entreprises",
            "category": "entreprises",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.group_approve",
            "name": "Approuver un regroupement",
            "description": "Permet d'approuver ou rejeter une demande de regroupement",
            "category": "entreprises",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "code": "entreprises.view_linked",
            "name": "Voir les entreprises liées",
            "description": "Permet de consulter les entreprises rattachées ou regroupées",
            "category": "entreprises",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for permission in permissions:
        # Vérifier si la permission existe déjà
        existing = await db.iam_permissions.find_one({"code": permission["code"]})
        
        if existing:
            print(f"  ⚠️  Permission '{permission['code']}' existe déjà")
            skipped_count += 1
        else:
            await db.iam_permissions.insert_one(permission)
            print(f"  ✅ Permission '{permission['code']}' créée")
            created_count += 1
    
    print(f"\n✅ {created_count} permissions créées, {skipped_count} déjà existantes")
    
    # Assigner les permissions au rôle admin
    print("\n🔄 Attribution des permissions au rôle admin...")
    
    admin_role = await db.iam_roles.find_one({"code": "admin"})
    
    if admin_role:
        permission_codes = [p["code"] for p in permissions]
        
        result = await db.iam_roles.update_one(
            {"code": "admin"},
            {
                "$addToSet": {
                    "permissions": {"$each": permission_codes}
                },
                "$set": {
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        print(f"✅ Permissions ajoutées au rôle admin")
    else:
        print("⚠️  Rôle admin non trouvé")


async def main():
    try:
        print("=" * 80)
        print("🚀 CRÉATION PERMISSIONS PHASE 3 : RATTACHEMENT")
        print("=" * 80)
        
        await create_permissions()
        
        print("\n" + "=" * 80)
        print("🎉 TERMINÉ")
        print("=" * 80)
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
