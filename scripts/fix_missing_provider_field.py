"""
Script de migration: Correction du champ 'provider' manquant
Problème: Les utilisateurs créés sans le champ 'provider' ne peuvent pas se connecter
car la requête de login filtre par provider='local'
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


async def fix_missing_provider():
    """
    Met à jour tous les utilisateurs avec password_hash mais sans champ provider
    pour définir provider='local'
    """
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("🔍 Recherche des utilisateurs sans champ 'provider'...")
    
    # Trouver tous les utilisateurs avec password_hash mais sans provider
    users_without_provider = await db.users.find({
        'password_hash': {'$exists': True},
        'provider': {'$exists': False}
    }, {'_id': 0, 'id': 1, 'username': 1, 'email': 1}).to_list(1000)
    
    print(f"📋 Trouvé {len(users_without_provider)} utilisateurs sans champ 'provider'")
    
    if not users_without_provider:
        print("✅ Aucun utilisateur à corriger")
        return
    
    # Afficher les utilisateurs trouvés
    print("\nUtilisateurs à corriger:")
    for user in users_without_provider:
        print(f"  - {user.get('username')} ({user.get('email')})")
    
    # Demander confirmation (pour la sécurité)
    print(f"\n⚠️  Mise à jour de {len(users_without_provider)} utilisateurs avec provider='local'")
    
    # Mettre à jour tous les utilisateurs
    result = await db.users.update_many(
        {
            'password_hash': {'$exists': True},
            'provider': {'$exists': False}
        },
        {
            '$set': {
                'provider': 'local',
                'provider_user_id': None,  # Ajout du champ pour cohérence
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    print(f"\n✅ Migration terminée!")
    print(f"   - {result.matched_count} utilisateurs trouvés")
    print(f"   - {result.modified_count} utilisateurs mis à jour")
    
    # Vérifier que company_1 a été corrigé
    company_1 = await db.users.find_one(
        {'username': 'company_1'},
        {'_id': 0, 'username': 1, 'provider': 1, 'status': 1}
    )
    
    if company_1:
        print(f"\n🎯 Vérification de company_1:")
        print(f"   - Username: {company_1.get('username')}")
        print(f"   - Provider: {company_1.get('provider')}")
        print(f"   - Status: {company_1.get('status')}")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(fix_missing_provider())
