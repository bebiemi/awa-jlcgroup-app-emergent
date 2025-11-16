"""
Script pour ajouter les pays et villes d'Afrique centrale prioritaires
GABON, RCA, CAMEROUN, CONGO BRAZZAVILLE
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid


async def seed_africa():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    now = datetime.now(timezone.utc)
    
    # Pays d'Afrique centrale prioritaires
    african_countries = [
        {"code": "GA", "label_fr": "Gabon", "label_en": "Gabon", "flag": "🇬🇦", "capital": "Libreville"},
        {"code": "CF", "label_fr": "République Centrafricaine", "label_en": "Central African Republic", "flag": "🇨🇫", "capital": "Bangui"},
        {"code": "CM", "label_fr": "Cameroun", "label_en": "Cameroon", "flag": "🇨🇲", "capital": "Yaoundé"},
        {"code": "CG", "label_fr": "Congo-Brazzaville", "label_en": "Republic of the Congo", "flag": "🇨🇬", "capital": "Brazzaville"},
    ]
    
    # Villes principales par pays
    african_cities = [
        # GABON
        {"code": "LBV", "label_fr": "Libreville", "label_en": "Libreville", "country_code": "GA", "region": "Estuaire", "population": 703904, "is_capital": True},
        {"code": "POG", "label_fr": "Port-Gentil", "label_en": "Port-Gentil", "country_code": "GA", "region": "Ogooué-Maritime", "population": 136462, "is_capital": False},
        {"code": "FRV", "label_fr": "Franceville", "label_en": "Franceville", "country_code": "GA", "region": "Haut-Ogooué", "population": 110568, "is_capital": False},
        {"code": "OYM", "label_fr": "Oyem", "label_en": "Oyem", "country_code": "GA", "region": "Woleu-Ntem", "population": 60685, "is_capital": False},
        {"code": "MOU", "label_fr": "Moanda", "label_en": "Moanda", "country_code": "GA", "region": "Haut-Ogooué", "population": 39298, "is_capital": False},
        
        # RÉPUBLIQUE CENTRAFRICAINE (RCA)
        {"code": "BGF", "label_fr": "Bangui", "label_en": "Bangui", "country_code": "CF", "region": "Bangui", "population": 889231, "is_capital": True},
        {"code": "BIM", "label_fr": "Bimbo", "label_en": "Bimbo", "country_code": "CF", "region": "Ombella-M'Poko", "population": 267859, "is_capital": False},
        {"code": "BRB", "label_fr": "Berbérati", "label_en": "Berbérati", "country_code": "CF", "region": "Mambéré-Kadéï", "population": 105155, "is_capital": False},
        {"code": "CRF", "label_fr": "Carnot", "label_en": "Carnot", "country_code": "CF", "region": "Mambéré-Kadéï", "population": 68820, "is_capital": False},
        {"code": "BNG", "label_fr": "Bambari", "label_en": "Bambari", "country_code": "CF", "region": "Ouaka", "population": 47044, "is_capital": False},
        
        # CAMEROUN
        {"code": "YAO", "label_fr": "Yaoundé", "label_en": "Yaoundé", "country_code": "CM", "region": "Centre", "population": 2765568, "is_capital": True},
        {"code": "DLA", "label_fr": "Douala", "label_en": "Douala", "country_code": "CM", "region": "Littoral", "population": 2768000, "is_capital": False},
        {"code": "GOU", "label_fr": "Garoua", "label_en": "Garoua", "country_code": "CM", "region": "Nord", "population": 436899, "is_capital": False},
        {"code": "BUE", "label_fr": "Buéa", "label_en": "Buea", "country_code": "CM", "region": "Sud-Ouest", "population": 300000, "is_capital": False},
        {"code": "BAF", "label_fr": "Bafoussam", "label_en": "Bafoussam", "country_code": "CM", "region": "Ouest", "population": 290768, "is_capital": False},
        {"code": "BAM", "label_fr": "Bamenda", "label_en": "Bamenda", "country_code": "CM", "region": "Nord-Ouest", "population": 348766, "is_capital": False},
        {"code": "NGA", "label_fr": "Ngaoundéré", "label_en": "Ngaoundéré", "country_code": "CM", "region": "Adamaoua", "population": 189800, "is_capital": False},
        
        # CONGO-BRAZZAVILLE
        {"code": "BZV", "label_fr": "Brazzaville", "label_en": "Brazzaville", "country_code": "CG", "region": "Brazzaville", "population": 1696392, "is_capital": True},
        {"code": "PNR", "label_fr": "Pointe-Noire", "label_en": "Pointe-Noire", "country_code": "CG", "region": "Kouilou", "population": 715334, "is_capital": False},
        {"code": "DJA", "label_fr": "Dolisie", "label_en": "Dolisie", "country_code": "CG", "region": "Niari", "population": 103894, "is_capital": False},
        {"code": "NKY", "label_fr": "Nkayi", "label_en": "Nkayi", "country_code": "CG", "region": "Bouenza", "population": 71620, "is_capital": False},
        {"code": "OWD", "label_fr": "Owando", "label_en": "Owando", "country_code": "CG", "region": "Cuvette", "population": 36100, "is_capital": False},
    ]
    
    # Insertion/Mise à jour des pays
    countries_inserted = 0
    countries_updated = 0
    
    for country_data in african_countries:
        existing = await db.system_references.find_one({
            "category": "countries",
            "code": country_data["code"]
        })
        
        country_doc = {
            "category": "countries",
            "code": country_data["code"],
            "label_fr": country_data["label_fr"],
            "label_en": country_data["label_en"],
            "order": 0,
            "metadata": {
                "flag": country_data["flag"],
                "capital": country_data["capital"],
                "region": "Afrique Centrale",
                "currency": "XAF",  # Franc CFA
                "languages": ["Français"]
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
            await db.system_references.insert_one(country_doc)
            countries_inserted += 1
    
    print("🌍 PAYS D'AFRIQUE CENTRALE")
    print(f"✅ Pays ajoutés: {countries_inserted}")
    print(f"✅ Pays mis à jour: {countries_updated}")
    
    # Insertion/Mise à jour des villes
    cities_inserted = 0
    cities_updated = 0
    
    for city_data in african_cities:
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
                "is_capital": city_data.get("is_capital", False),
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
            cities_updated += 1
        else:
            city_doc["id"] = str(uuid.uuid4())
            city_doc["created_at"] = now
            await db.system_references.insert_one(city_doc)
            cities_inserted += 1
    
    print(f"\n🏙️ VILLES D'AFRIQUE CENTRALE")
    print(f"✅ Villes ajoutées: {cities_inserted}")
    print(f"✅ Villes mises à jour: {cities_updated}")
    
    # Récapitulatif par pays
    print(f"\n📊 RÉCAPITULATIF PAR PAYS:")
    for country in african_countries:
        cities_count = len([c for c in african_cities if c["country_code"] == country["code"]])
        capital = country["capital"]
        print(f"   {country['flag']} {country['label_fr']}: {cities_count} villes (capitale: {capital})")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_africa())
