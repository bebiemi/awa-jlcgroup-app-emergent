"""
Script pour créer ou promouvoir un utilisateur en super_admin
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/auth_db')


async def create_super_admin():
    """Promouvoir admin en super_admin"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🔧 Promotion de l'utilisateur admin en super_admin")
    print("=" * 60)
    
    # Trouver l'utilisateur admin
    admin_user = await db.users.find_one({"username": "admin"})
    
    if not admin_user:
        print("❌ Utilisateur 'admin' non trouvé")
        return
    
    print(f"✓ Utilisateur trouvé: {admin_user['username']} ({admin_user.get('email', 'N/A')})")
    print(f"  Rôles actuels: {admin_user.get('roles', [])}")
    
    # Vérifier si déjà super_admin
    if "super_admin" in admin_user.get('roles', []):
        print("⏭️  L'utilisateur est déjà super_admin")
        client.close()
        return
    
    # Ajouter le rôle super_admin
    current_roles = admin_user.get('roles', [])
    if "super_admin" not in current_roles:
        current_roles.append("super_admin")
    
    result = await db.users.update_one(
        {"username": "admin"},
        {"$set": {"roles": current_roles}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Rôle 'super_admin' ajouté avec succès")
        print(f"  Nouveaux rôles: {current_roles}")
    else:
        print("❌ Erreur lors de la mise à jour")
    
    print("\n" + "=" * 60)
    print("✅ Terminé!")
    
    # Vérification
    updated_user = await db.users.find_one({"username": "admin"})
    print(f"\nVérification finale - Rôles: {updated_user.get('roles', [])}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_super_admin())
