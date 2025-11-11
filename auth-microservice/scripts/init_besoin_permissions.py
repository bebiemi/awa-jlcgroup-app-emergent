"""
Initialize Besoin Permissions
Creates all permissions related to besoins management
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone


async def init_besoin_permissions():
    """Initialize besoin permissions in database"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")  # Default DB name from config
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc)
    
    print("🔧 Initializing besoin permissions...")
    
    permissions = [
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.create",
            "name": "Créer des besoins",
            "description": "Permet de créer et gérer des besoins de recrutement",
            "resource": "besoins",
            "action": "create",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.read",
            "name": "Consulter les besoins",
            "description": "Permet de consulter les besoins",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.edit",
            "name": "Modifier les besoins",
            "description": "Permet de modifier les besoins en brouillon",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.submit",
            "name": "Soumettre les besoins",
            "description": "Permet de soumettre les besoins à JLC",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.comment",
            "name": "Commenter les besoins",
            "description": "Permet d'ajouter des commentaires sur les besoins",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.validate",
            "name": "Valider les besoins (JLC)",
            "description": "Permet de valider et gérer le workflow des besoins (JLC seulement)",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "code": "besoins.convert_to_mission",
            "name": "Convertir en mission (JLC)",
            "description": "Permet de convertir un besoin en mission (JLC seulement)",
            "category": "besoins",
            "is_system_permission": False,
            "created_at": now,
            "updated_at": now,
        },
    ]
    
    for perm in permissions:
        # Check if exists
        existing = await db.permissions.find_one({"code": perm["code"]})
        if existing:
            print(f"ℹ️  Permission {perm['code']} already exists")
        else:
            await db.permissions.insert_one(perm)
            print(f"✅ Permission {perm['code']} created")
    
    print("\n🔧 Creating/Updating Entreprise profile...")
    
    # Get permission IDs
    perm_codes = ["besoins.create", "besoins.read", "besoins.edit", "besoins.submit", "besoins.comment", "missions.create", "missions.read"]
    permission_ids = []
    for code in perm_codes:
        perm = await db.permissions.find_one({"code": code})
        if perm:
            permission_ids.append(perm["id"])
    
    # Create or update Entreprise profile
    profile_id = str(uuid.uuid4())
    entreprise_profile = {
        "id": profile_id,
        "code": "entreprise",
        "name": "Entreprise",
        "description": "Profil pour les entreprises clientes - Gestion des besoins et missions",
        "permission_ids": permission_ids,
        "is_system_role": False,  # Correct field name
        "is_protected": False,
        "priority": 0,
        "category": "custom",
        "created_at": now,
        "updated_at": now,
    }
    
    existing_profile = await db.profiles.find_one({"code": "entreprise"})
    if existing_profile:
        await db.profiles.update_one(
            {"code": "entreprise"},
            {"$set": {
                "permission_ids": permission_ids,
                "updated_at": now
            }}
        )
        print(f"✅ Entreprise profile updated with {len(permission_ids)} permissions")
    else:
        await db.profiles.insert_one(entreprise_profile)
        print(f"✅ Entreprise profile created with {len(permission_ids)} permissions")
    
    print("\n✅ Besoin permissions initialization complete!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(init_besoin_permissions())
