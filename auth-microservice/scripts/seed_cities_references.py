"""
Script pour enrichir les référentiels avec les villes
Ajoute les principales villes françaises et européennes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid


async def seed_cities():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    now = datetime.now(timezone.utc)
    
    # Villes françaises principales (par région)
    french_cities = [
        # Île-de-France
        {"code": "75000", "label_fr": "Paris", "label_en": "Paris", "country_code": "FR", "region": "Île-de-France", "population": 2165423},
        {"code": "92000", "label_fr": "Nanterre", "label_en": "Nanterre", "country_code": "FR", "region": "Île-de-France", "population": 96807},
        {"code": "93000", "label_fr": "Bobigny", "label_en": "Bobigny", "country_code": "FR", "region": "Île-de-France", "population": 54332},
        {"code": "94000", "label_fr": "Créteil", "label_en": "Créteil", "country_code": "FR", "region": "Île-de-France", "population": 92265},
        {"code": "95000", "label_fr": "Cergy", "label_en": "Cergy", "country_code": "FR", "region": "Île-de-France", "population": 64813},
        
        # Auvergne-Rhône-Alpes
        {"code": "69000", "label_fr": "Lyon", "label_en": "Lyon", "country_code": "FR", "region": "Auvergne-Rhône-Alpes", "population": 516092},
        {"code": "38000", "label_fr": "Grenoble", "label_en": "Grenoble", "country_code": "FR", "region": "Auvergne-Rhône-Alpes", "population": 158180},
        {"code": "74000", "label_fr": "Annecy", "label_en": "Annecy", "country_code": "FR", "region": "Auvergne-Rhône-Alpes", "population": 128199},
        
        # Provence-Alpes-Côte d'Azur
        {"code": "13000", "label_fr": "Marseille", "label_en": "Marseille", "country_code": "FR", "region": "Provence-Alpes-Côte d'Azur", "population": 869815},
        {"code": "06000", "label_fr": "Nice", "label_en": "Nice", "country_code": "FR", "region": "Provence-Alpes-Côte d'Azur", "population": 340017},
        {"code": "83000", "label_fr": "Toulon", "label_en": "Toulon", "country_code": "FR", "region": "Provence-Alpes-Côte d'Azur", "population": 171953},
        
        # Occitanie
        {"code": "31000", "label_fr": "Toulouse", "label_en": "Toulouse", "country_code": "FR", "region": "Occitanie", "population": 471941},
        {"code": "34000", "label_fr": "Montpellier", "label_en": "Montpellier", "country_code": "FR", "region": "Occitanie", "population": 285121},
        
        # Nouvelle-Aquitaine
        {"code": "33000", "label_fr": "Bordeaux", "label_en": "Bordeaux", "country_code": "FR", "region": "Nouvelle-Aquitaine", "population": 252040},
        
        # Grand Est
        {"code": "67000", "label_fr": "Strasbourg", "label_en": "Strasbourg", "country_code": "FR", "region": "Grand Est", "population": 280966},
        {"code": "54000", "label_fr": "Nancy", "label_en": "Nancy", "country_code": "FR", "region": "Grand Est", "population": 104072},
        {"code": "51000", "label_fr": "Reims", "label_en": "Reims", "country_code": "FR", "region": "Grand Est", "population": 182460},
        
        # Hauts-de-France
        {"code": "59000", "label_fr": "Lille", "label_en": "Lille", "country_code": "FR", "region": "Hauts-de-France", "population": 232787},
        
        # Pays de la Loire
        {"code": "44000", "label_fr": "Nantes", "label_en": "Nantes", "country_code": "FR", "region": "Pays de la Loire", "population": 309346},
        
        # Bretagne
        {"code": "35000", "label_fr": "Rennes", "label_en": "Rennes", "country_code": "FR", "region": "Bretagne", "population": 216815},
        
        # Normandie
        {"code": "76000", "label_fr": "Rouen", "label_en": "Rouen", "country_code": "FR", "region": "Normandie", "population": 110145},
    ]
    
    # Villes européennes principales
    european_cities = [
        # Belgique
        {"code": "BRU", "label_fr": "Bruxelles", "label_en": "Brussels", "country_code": "BE", "region": "Bruxelles-Capitale", "population": 1200000},
        {"code": "ANT", "label_fr": "Anvers", "label_en": "Antwerp", "country_code": "BE", "region": "Flandre", "population": 520504},
        
        # Luxembourg
        {"code": "LUX", "label_fr": "Luxembourg", "label_en": "Luxembourg", "country_code": "LU", "region": "Luxembourg", "population": 120000},
        
        # Suisse
        {"code": "GVA", "label_fr": "Genève", "label_en": "Geneva", "country_code": "CH", "region": "Genève", "population": 200000},
        {"code": "ZRH", "label_fr": "Zurich", "label_en": "Zurich", "country_code": "CH", "region": "Zurich", "population": 400000},
        
        # Allemagne
        {"code": "BER", "label_fr": "Berlin", "label_en": "Berlin", "country_code": "DE", "region": "Berlin", "population": 3500000},
        {"code": "MUC", "label_fr": "Munich", "label_en": "Munich", "country_code": "DE", "region": "Bavière", "population": 1500000},
        
        # Espagne
        {"code": "MAD", "label_fr": "Madrid", "label_en": "Madrid", "country_code": "ES", "region": "Madrid", "population": 3200000},
        {"code": "BCN", "label_fr": "Barcelone", "label_en": "Barcelona", "country_code": "ES", "region": "Catalogne", "population": 1600000},
        
        # Italie
        {"code": "ROM", "label_fr": "Rome", "label_en": "Rome", "country_code": "IT", "region": "Latium", "population": 2800000},
        {"code": "MIL", "label_fr": "Milan", "label_en": "Milan", "country_code": "IT", "region": "Lombardie", "population": 1400000},
    ]
    
    all_cities = french_cities + european_cities
    
    inserted_count = 0
    updated_count = 0
    
    for city_data in all_cities:
        # Vérifier si la ville existe déjà
        existing = await db.system_references.find_one({
            "category": "cities",
            "code": city_data["code"]
        })
        
        city_doc = {
            "category": "cities",
            "code": city_data["code"],
            "label_fr": city_data["label_fr"],
            "label_en": city_data["label_en"],
            "order": 0,
            "metadata": {
                "country_code": city_data["country_code"],
                "region": city_data["region"],
                "population": city_data.get("population", 0),
                "is_major_city": city_data.get("population", 0) > 100000
            },
            "is_active": True,
            "is_system": True,
            "updated_at": now
        }
        
        if existing:
            await db.system_references.update_one(
                {"_id": existing["_id"]},
                {"$set": city_doc}
            )
            updated_count += 1
        else:
            city_doc["id"] = str(uuid.uuid4())
            city_doc["created_at"] = now
            await db.system_references.insert_one(city_doc)
            inserted_count += 1
    
    print(f"✅ Villes ajoutées: {inserted_count}")
    print(f"✅ Villes mises à jour: {updated_count}")
    print(f"📊 Total: {len(all_cities)} villes dans le référentiel")
    
    # Vérifier les pays existants et s'assurer qu'ils sont à jour
    countries = [
        {"code": "FR", "label_fr": "France", "label_en": "France", "flag": "🇫🇷"},
        {"code": "BE", "label_fr": "Belgique", "label_en": "Belgium", "flag": "🇧🇪"},
        {"code": "LU", "label_fr": "Luxembourg", "label_en": "Luxembourg", "flag": "🇱🇺"},
        {"code": "CH", "label_fr": "Suisse", "label_en": "Switzerland", "flag": "🇨🇭"},
        {"code": "DE", "label_fr": "Allemagne", "label_en": "Germany", "flag": "🇩🇪"},
        {"code": "ES", "label_fr": "Espagne", "label_en": "Spain", "flag": "🇪🇸"},
        {"code": "IT", "label_fr": "Italie", "label_en": "Italy", "flag": "🇮🇹"},
        {"code": "GB", "label_fr": "Royaume-Uni", "label_en": "United Kingdom", "flag": "🇬🇧"},
        {"code": "PT", "label_fr": "Portugal", "label_en": "Portugal", "flag": "🇵🇹"},
        {"code": "NL", "label_fr": "Pays-Bas", "label_en": "Netherlands", "flag": "🇳🇱"},
    ]
    
    countries_updated = 0
    for country_data in countries:
        existing = await db.system_references.find_one({
            "category": "countries",
            "code": country_data["code"]
        })
        
        country_doc = {
            "category": "countries",
            "code": country_data["code"],
            "label_fr": country_data["label_fr"],
            "label_en": country_data["label_en"],
            "metadata": {
                "flag": country_data.get("flag", ""),
                "eu_member": country_data["code"] in ["FR", "BE", "LU", "DE", "ES", "IT", "PT", "NL"]
            },
            "is_active": True,
            "is_system": True,
            "updated_at": now
        }
        
        if existing:
            await db.system_references.update_one(
                {"_id": existing["_id"]},
                {"$set": country_doc}
            )
            countries_updated += 1
        else:
            country_doc["id"] = str(uuid.uuid4())
            country_doc["created_at"] = now
            country_doc["order"] = 0
            await db.system_references.insert_one(country_doc)
            countries_updated += 1
    
    print(f"\n✅ Pays mis à jour: {countries_updated}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_cities())
