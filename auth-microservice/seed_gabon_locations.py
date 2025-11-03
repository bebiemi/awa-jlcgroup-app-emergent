"""
Seed script for Gabon locations
Hierarchical structure: Country → Province → City → District → Neighborhood
"""
import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


async def seed_gabon_locations():
    """Seed Gabon location data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🌍 Seeding Gabon locations...")
    
    # Clear existing locations (optional - comment out if you want to keep existing data)
    # await db.locations.delete_many({})
    
    # Create Gabon (Country)
    gabon_id = str(uuid.uuid4())
    gabon = {
        "id": gabon_id,
        "type": "country",
        "name": "Gabon",
        "parent_id": None,
        "is_visible": True,
        "is_required": True,
        "postal_code": None,
        "gps_latitude": -0.8037,
        "gps_longitude": 11.6094,
        "custom_field_1": "GA",  # ISO Code
        "custom_field_2": "+241",  # Phone prefix
        "custom_field_1_label": "Code ISO",
        "custom_field_2_label": "Préfixe téléphonique",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.locations.insert_one(gabon)
    print(f"✅ Created country: Gabon")
    
    # Provinces of Gabon
    provinces = [
        {"name": "Estuaire", "lat": 0.4162, "lon": 9.4673},
        {"name": "Haut-Ogooué", "lat": -1.4771, "lon": 13.5784},
        {"name": "Moyen-Ogooué", "lat": -0.6956, "lon": 10.4069},
        {"name": "Ngounié", "lat": -1.5268, "lon": 10.9318},
        {"name": "Nyanga", "lat": -2.9283, "lon": 11.0878},
        {"name": "Ogooué-Ivindo", "lat": 0.5376, "lon": 13.4098},
        {"name": "Ogooué-Lolo", "lat": -0.8956, "lon": 12.5703},
        {"name": "Ogooué-Maritime", "lat": -1.5380, "lon": 9.8387},
        {"name": "Woleu-Ntem", "lat": 2.1514, "lon": 11.4761},
    ]
    
    province_ids = {}
    for province in provinces:
        province_id = str(uuid.uuid4())
        province_ids[province["name"]] = province_id
        
        province_doc = {
            "id": province_id,
            "type": "province",
            "name": province["name"],
            "parent_id": gabon_id,
            "is_visible": True,
            "is_required": False,
            "gps_latitude": province["lat"],
            "gps_longitude": province["lon"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.locations.insert_one(province_doc)
        print(f"  ✅ Created province: {province['name']}")
    
    # Cities (Chef-lieux) for each province
    cities_data = {
        "Estuaire": [
            {"name": "Libreville", "lat": 0.4162, "lon": 9.4673, "postal": "BP 1000"},
            {"name": "Owendo", "lat": 0.2917, "lon": 9.5000},
            {"name": "Akanda", "lat": 0.5333, "lon": 9.5833},
            {"name": "Ntoum", "lat": 0.3917, "lon": 9.7667},
        ],
        "Haut-Ogooué": [
            {"name": "Franceville", "lat": -1.6333, "lon": 13.5833, "postal": "BP 50"},
            {"name": "Moanda", "lat": -1.5667, "lon": 13.2000},
            {"name": "Mounana", "lat": -1.4167, "lon": 13.1500},
        ],
        "Moyen-Ogooué": [
            {"name": "Lambaréné", "lat": -0.7000, "lon": 10.2333},
            {"name": "Ndjolé", "lat": -0.1833, "lon": 10.7667},
        ],
        "Ngounié": [
            {"name": "Mouila", "lat": -1.8667, "lon": 11.0167},
            {"name": "Ndendé", "lat": -2.4000, "lon": 11.3667},
            {"name": "Mbigou", "lat": -1.9000, "lon": 11.9000},
        ],
        "Nyanga": [
            {"name": "Tchibanga", "lat": -2.9333, "lon": 11.0167},
            {"name": "Mayumba", "lat": -3.4167, "lon": 10.6500},
        ],
        "Ogooué-Ivindo": [
            {"name": "Makokou", "lat": 0.5667, "lon": 12.8667},
            {"name": "Mékambo", "lat": 1.0167, "lon": 13.9333},
            {"name": "Ovan", "lat": 1.2000, "lon": 11.6167},
        ],
        "Ogooué-Lolo": [
            {"name": "Koulamoutou", "lat": -1.1333, "lon": 12.4833},
            {"name": "Lastoursville", "lat": -0.8167, "lon": 12.7500},
        ],
        "Ogooué-Maritime": [
            {"name": "Port-Gentil", "lat": -0.7193, "lon": 8.7815, "postal": "BP 116"},
            {"name": "Omboué", "lat": -1.5750, "lon": 9.2622},
            {"name": "Gamba", "lat": -2.6500, "lon": 10.0000},
        ],
        "Woleu-Ntem": [
            {"name": "Oyem", "lat": 1.6000, "lon": 11.5833},
            {"name": "Bitam", "lat": 2.0833, "lon": 11.5000},
            {"name": "Mitzic", "lat": 0.7833, "lon": 11.5500},
        ],
    }
    
    city_ids = {}
    for province_name, cities in cities_data.items():
        province_id = province_ids.get(province_name)
        if not province_id:
            continue
        
        for city in cities:
            city_id = str(uuid.uuid4())
            city_key = f"{province_name}:{city['name']}"
            city_ids[city_key] = city_id
            
            city_doc = {
                "id": city_id,
                "type": "city",
                "name": city["name"],
                "parent_id": province_id,
                "is_visible": True,
                "is_required": True,
                "postal_code": city.get("postal"),
                "gps_latitude": city.get("lat"),
                "gps_longitude": city.get("lon"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.locations.insert_one(city_doc)
            print(f"    ✅ Created city: {city['name']} ({province_name})")
    
    # Sample Districts (Arrondissements) for Libreville
    libreville_id = city_ids.get("Estuaire:Libreville")
    if libreville_id:
        districts = [
            "1er Arrondissement",
            "2ème Arrondissement",
            "3ème Arrondissement",
            "4ème Arrondissement",
            "5ème Arrondissement",
            "6ème Arrondissement",
        ]
        
        district_ids = {}
        for district_name in districts:
            district_id = str(uuid.uuid4())
            district_ids[district_name] = district_id
            
            district_doc = {
                "id": district_id,
                "type": "district",
                "name": district_name,
                "parent_id": libreville_id,
                "is_visible": True,
                "is_required": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.locations.insert_one(district_doc)
            print(f"      ✅ Created district: {district_name}")
        
        # Sample Neighborhoods (Quartiers) for 1er Arrondissement Libreville
        first_district_id = district_ids.get("1er Arrondissement")
        if first_district_id:
            neighborhoods = [
                "Mont-Bouët",
                "Nombakélé",
                "Nkembo",
                "Batterie IV",
                "Louis",
            ]
            
            for neighborhood in neighborhoods:
                neighborhood_id = str(uuid.uuid4())
                neighborhood_doc = {
                    "id": neighborhood_id,
                    "type": "neighborhood",
                    "name": neighborhood,
                    "parent_id": first_district_id,
                    "is_visible": True,
                    "is_required": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                await db.locations.insert_one(neighborhood_doc)
                print(f"        ✅ Created neighborhood: {neighborhood}")
    
    # Port-Gentil districts and neighborhoods
    port_gentil_id = city_ids.get("Ogooué-Maritime:Port-Gentil")
    if port_gentil_id:
        pg_districts = [
            "Bantoville",
            "Toujours Pur",
            "Grand Village",
            "Beau Séjour",
        ]
        
        for district_name in pg_districts:
            district_id = str(uuid.uuid4())
            district_doc = {
                "id": district_id,
                "type": "district",
                "name": district_name,
                "parent_id": port_gentil_id,
                "is_visible": True,
                "is_required": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.locations.insert_one(district_doc)
            print(f"      ✅ Created district: {district_name} (Port-Gentil)")
    
    print(f"\n✅ Gabon locations seeded successfully!")
    print(f"   - 1 Country")
    print(f"   - {len(provinces)} Provinces")
    print(f"   - {sum(len(cities) for cities in cities_data.values())} Cities")
    print(f"   - Sample Districts and Neighborhoods")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_gabon_locations())
