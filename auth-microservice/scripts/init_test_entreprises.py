"""
Script pour créer des entreprises de test et associer les utilisateurs
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid


async def init_test_entreprises():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # Entreprises de test à créer
    test_entreprises = [
        {
            "nom": "JLC Test Company",
            "raison_sociale": "JLC Test Company SAS",
            "siret": "12345678900001",
            "adresse": "123 Rue de Test, 75001 Paris",
            "email": "contact@jlc-test.fr",
            "telephone": "01 23 45 67 89",
            "description": "Entreprise de test principale",
        },
        {
            "nom": "Tech Solutions SARL",
            "raison_sociale": "Tech Solutions SARL",
            "siret": "98765432100002",
            "adresse": "456 Avenue Innovation, 69001 Lyon",
            "email": "contact@tech-solutions.fr",
            "telephone": "04 56 78 90 12",
            "description": "Entreprise de test secondaire",
        }
    ]
    
    created_entreprises = {}
    
    for entreprise_data in test_entreprises:
        nom = entreprise_data["nom"]
        entreprise = await db.entreprises.find_one({"nom": nom})
        
        if not entreprise:
            entreprise_id = str(uuid.uuid4())
            entreprise_doc = {
                "id": entreprise_id,
                **entreprise_data,
                "created_at": datetime.now(timezone.utc),
                "status": "active"
            }
            await db.entreprises.insert_one(entreprise_doc)
            print(f"✅ Entreprise créée: {nom} ({entreprise_id})")
            created_entreprises[nom] = entreprise_id
        else:
            entreprise_id = entreprise['id']
            print(f"✓ Entreprise existante: {nom} ({entreprise_id})")
            created_entreprises[nom] = entreprise_id
    
    # Association utilisateurs → entreprises
    user_mappings = {
        'entreprise_test': 'JLC Test Company',
        'commercial_test': 'Tech Solutions SARL',
        'admin': 'JLC Test Company',  # Admin aussi pour faciliter les tests
    }
    
    for username, entreprise_nom in user_mappings.items():
        user = await db.users.find_one({"username": username})
        if user:
            entreprise_id = created_entreprises.get(entreprise_nom)
            if entreprise_id:
                result = await db.users.update_one(
                    {"id": user['id']},
                    {"$set": {
                        "company_id": entreprise_id,
                        "entreprise_id": entreprise_id,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                print(f"  ✅ {username} → {entreprise_nom}")
            else:
                print(f"  ⚠️  {username}: entreprise non trouvée")
        else:
            print(f"  ⚠️  Utilisateur '{username}' non trouvé")
    
    # Résumé
    print(f"\n📊 Résumé:")
    print(f"  - {len(created_entreprises)} entreprises configurées")
    print(f"  - {len(user_mappings)} utilisateurs associés")
    
    # Vérification
    print(f"\n🔍 Vérification:")
    for username in user_mappings.keys():
        user = await db.users.find_one({"username": username})
        if user:
            company_id = user.get('company_id')
            if company_id:
                entreprise = await db.entreprises.find_one({"id": company_id})
                print(f"  ✓ {username:20} → {entreprise.get('nom', 'N/A')}")
            else:
                print(f"  ✗ {username:20} → Pas d'entreprise")
    
    client.close()
    print("\n✅ Initialisation complète!")


if __name__ == "__main__":
    asyncio.run(init_test_entreprises())
