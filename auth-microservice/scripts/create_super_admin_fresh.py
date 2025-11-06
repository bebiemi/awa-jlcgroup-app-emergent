"""
Script pour créer un super admin depuis zéro sur une nouvelle installation

Usage:
    python scripts/create_super_admin_fresh.py

Le script va:
1. Créer un utilisateur avec le rôle super_admin
2. Hasher le mot de passe
3. L'enregistrer dans MongoDB
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DATABASE_NAME', 'auth_db')

# Configuration du hashing de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hasher un mot de passe"""
    return pwd_context.hash(password)


async def create_super_admin():
    """Créer un super admin depuis zéro"""
    print("🔧 Création d'un Super Admin")
    print("=" * 60)
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Informations du super admin
    username = input("Nom d'utilisateur (ex: admin): ").strip() or "admin"
    email = input("Email (ex: admin@jlc.com): ").strip() or "admin@jlc.com"
    password = input("Mot de passe (min 8 caractères): ").strip()
    full_name = input("Nom complet (ex: Super Admin): ").strip() or "Super Admin"
    
    # Validation
    if len(password) < 8:
        print("❌ Le mot de passe doit contenir au moins 8 caractères")
        client.close()
        return
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = await db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    
    if existing_user:
        print(f"\n⚠️  Un utilisateur avec ce username ou email existe déjà")
        print(f"   Username: {existing_user.get('username')}")
        print(f"   Email: {existing_user.get('email')}")
        print(f"   Rôles: {existing_user.get('roles', [])}")
        
        choice = input("\nVoulez-vous ajouter le rôle super_admin à cet utilisateur? (y/N): ").strip().lower()
        
        if choice == 'y':
            current_roles = existing_user.get('roles', [])
            if "super_admin" not in current_roles:
                current_roles.append("super_admin")
                
                result = await db.users.update_one(
                    {"id": existing_user["id"]},
                    {"$set": {"roles": current_roles}}
                )
                
                if result.modified_count > 0:
                    print(f"✅ Rôle super_admin ajouté avec succès")
                    print(f"   Nouveaux rôles: {current_roles}")
                else:
                    print("❌ Erreur lors de la mise à jour")
            else:
                print("ℹ️  L'utilisateur a déjà le rôle super_admin")
        
        client.close()
        return
    
    # Créer le nouvel utilisateur
    print(f"\n📝 Création de l'utilisateur...")
    
    hashed_password = hash_password(password)
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    new_user = {
        "id": user_id,
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "roles": ["super_admin"],
        "is_active": True,
        "is_verified": True,
        "phone_number": None,
        "avatar_url": None,
        "metadata": {
            "created_via": "script",
            "created_by": "system"
        },
        "created_at": now,
        "updated_at": now
    }
    
    try:
        result = await db.users.insert_one(new_user)
        
        if result.inserted_id:
            print("\n✅ Super Admin créé avec succès!")
            print("=" * 60)
            print(f"👤 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"🔑 Rôles: {new_user['roles']}")
            print(f"🆔 ID: {user_id}")
            print("=" * 60)
            print("\n🎉 Vous pouvez maintenant vous connecter avec ces identifiants")
            
        else:
            print("❌ Erreur lors de la création de l'utilisateur")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    finally:
        client.close()


async def list_super_admins():
    """Lister tous les super admins existants"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n🔍 Super Admins existants:")
    print("=" * 60)
    
    cursor = db.users.find({"roles": "super_admin"})
    super_admins = await cursor.to_list(length=None)
    
    if not super_admins:
        print("Aucun super admin trouvé")
    else:
        for i, user in enumerate(super_admins, 1):
            print(f"\n{i}. {user.get('full_name', 'N/A')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Rôles: {user.get('roles', [])}")
            print(f"   Actif: {'✓' if user.get('is_active') else '✗'}")
            print(f"   ID: {user.get('id')}")
    
    print("=" * 60)
    client.close()


async def main():
    """Menu principal"""
    print("\n" + "=" * 60)
    print("🛠️  JLC - Gestion des Super Admins")
    print("=" * 60)
    print("\n1. Créer un nouveau super admin")
    print("2. Lister les super admins existants")
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        await create_super_admin()
    elif choice == "2":
        await list_super_admins()
    elif choice == "3":
        print("Au revoir!")
        return
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du script")
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
