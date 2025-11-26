#!/usr/bin/env python3
"""
Script pour s'assurer que toutes les configurations applicatives essentielles existent
Crée automatiquement les configurations manquantes dans la collection app_config
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "jlc_db"  # Base de données principale de l'application

# Configurations essentielles
ESSENTIAL_CONFIGS = [
    {
        "key": "profiles.badge_new_user",
        "value": {
            "enabled": True,
            "expiration_days": 7,
            "expiration_mode": "creation_date",  # "creation_date", "first_view", "both"
            "badge_text": {
                "fr": "NOUVEAU",
                "en": "NEW"
            }
        },
        "description": "Configuration du badge NOUVEAU pour les profils récemment créés",
        "category": "profiles"
    },
    # Ajouter d'autres configurations essentielles ici
]


async def ensure_app_configs():
    """S'assure que toutes les configurations essentielles existent"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🔍 VÉRIFICATION DES CONFIGURATIONS APPLICATIVES ({DB_NAME})")
    print("=" * 80)
    
    stats = {
        'total': len(ESSENTIAL_CONFIGS),
        'existing': 0,
        'created': 0,
        'updated': 0,
    }
    
    for config in ESSENTIAL_CONFIGS:
        key = config['key']
        
        # Vérifier si la configuration existe
        existing = await db.app_config.find_one({"key": key})
        
        if existing:
            print(f"\n✅ {key}")
            print(f"   Status: Déjà présente")
            stats['existing'] += 1
        else:
            print(f"\n➕ {key}")
            print(f"   Status: Manquante - Création...")
            
            # Ajouter les timestamps
            config_doc = {
                **config,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insérer la configuration
            result = await db.app_config.insert_one(config_doc)
            
            if result.inserted_id:
                print(f"   ✅ Créée avec succès")
                stats['created'] += 1
            else:
                print(f"   ❌ Échec de création")
    
    client.close()
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ")
    print("=" * 80)
    print(f"\nConfigurations totales: {stats['total']}")
    print(f"Déjà présentes: {stats['existing']}")
    print(f"Créées: {stats['created']}")
    
    if stats['created'] > 0:
        print(f"\n✅ {stats['created']} configuration(s) créée(s) avec succès!")
    else:
        print("\n✅ Toutes les configurations sont déjà en place!")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(ensure_app_configs())
