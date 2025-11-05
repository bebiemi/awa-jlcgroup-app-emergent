"""
Script pour créer un admin de test (sans super_admin)
"""
import asyncio
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/auth_db')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_test_admin():
    """Créer un admin de test"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🔧 Création d'un admin de test (sans super_admin)")
    print("=" * 60)
    
    # Vérifier si existe déjà
    existing = await db.users.find_one({"username": "admin_test"})
    if existing:
        print("⏭️  L'utilisateur 'admin_test' existe déjà")
        print(f"   Rôles: {existing.get('roles', [])}")
        client.close()
        return
    
    # Créer l'utilisateur
    test_admin = {
        "id": str(uuid.uuid4()),
        "username": "admin_test",
        "email": "admin_test@awanagroup.com",
        "full_name": "Admin Test",
        "password_hash": pwd_context.hash("awana2025"),
        "roles": ["admin"],  # Seulement admin, PAS super_admin
        "status": "active",
        "provider": "local",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_verified": True,
    }
    
    await db.users.insert_one(test_admin)
    
    print("✅ Utilisateur créé avec succès!")
    print(f"   Username: admin_test")
    print(f"   Email: admin_test@awanagroup.com")
    print(f"   Password: awana2025")
    print(f"   Rôles: {test_admin['roles']}")
    print(f"   ID: {test_admin['id']}")
    
    print("\n" + "=" * 60)
    print("✅ Terminé!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_test_admin())
