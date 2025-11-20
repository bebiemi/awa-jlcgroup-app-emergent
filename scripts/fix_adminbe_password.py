#!/usr/bin/env python3
"""
Script de correction du mot de passe adminbe
Corrige le problème de hachage bcrypt
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")

async def fix_password():
    """Corrige le mot de passe du compte adminbe"""
    
    print("\n" + "="*80)
    print("🔐 CORRECTION DU MOT DE PASSE ADMINBE")
    print("="*80 + "\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Vérifier que le compte existe
        user = await db.users.find_one({"username": "adminbe"})
        if not user:
            print("❌ Compte adminbe non trouvé!")
            return False
        
        print(f"✅ Compte trouvé: {user.get('email')}")
        
        # Hasher le mot de passe avec bcrypt directement
        password = "Awana2025!"
        print(f"🔑 Hachage du mot de passe: {password}")
        
        # Utiliser bcrypt directement (plus fiable que passlib)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_str = hashed.decode('utf-8')
        
        print(f"✅ Hash généré: {hashed_str[:30]}...")
        
        # Mettre à jour le mot de passe ET s'assurer que provider, status et roles sont définis
        result = await db.users.update_one(
            {"username": "adminbe"},
            {
                "$set": {
                    "password_hash": hashed_str,  # IMPORTANT: Doit être "password_hash" pas "hashed_password"
                    "provider": "local",  # S'assurer que le provider est défini
                    "status": "active",  # S'assurer que le statut est actif
                    "roles": ["super_admin"],  # IMPORTANT: Pour le JWT token
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Mot de passe mis à jour avec succès!\n")
        else:
            print("⚠️  Aucune modification effectuée\n")
        
        # Vérifier que le hash fonctionne
        print("🧪 Test de vérification du mot de passe...")
        is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed_str.encode('utf-8'))
        
        if is_valid:
            print("✅ Vérification OK - Le mot de passe fonctionne!\n")
        else:
            print("❌ Erreur de vérification!\n")
            return False
        
        print("="*80)
        print("✅ CORRECTION TERMINÉE AVEC SUCCÈS!")
        print("="*80)
        print("\n🔑 Vous pouvez maintenant vous connecter avec:")
        print("   Username: adminbe")
        print("   Password: Awana2025!")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()


if __name__ == "__main__":
    success = asyncio.run(fix_password())
    sys.exit(0 if success else 1)
