#!/usr/bin/env python3
"""
Script d'initialisation des référentiels depuis la configuration YAML
- Crée/met à jour tous les référentiels de données
- Supprime les référentiels obsolètes
- Gère les versions

Usage:
  python3 init_referentials.py
  python3 init_referentials.py --config /path/to/custom.yaml
  python3 init_referentials.py --clean  # Supprime les anciens référentiels
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
import argparse
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "jlc_db"
DEFAULT_CONFIG_FILE = Path(__file__).parent.parent / "config" / "referentials_config.yaml"


def load_config(config_path=None):
    """Charge la configuration des référentiels"""
    config_file = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    
    if not config_file.exists():
        print(f"❌ Fichier de configuration non trouvé: {config_file}")
        sys.exit(1)
    
    print(f"📖 Chargement de la configuration depuis: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


async def init_referentials(config, clean_old=False):
    """Initialise les référentiels depuis la configuration"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🔄 INITIALISATION DES RÉFÉRENTIELS ({DB_NAME})")
    print("=" * 80)
    
    stats = {
        'total': 0,
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    # Compter les référentiels
    referential_count = sum(1 for key in config.keys() if not key.startswith('_'))
    stats['total'] = referential_count
    
    print(f"\n📊 {referential_count} référentiel(s) à traiter\n")
    
    # Traiter chaque référentiel
    for ref_key, ref_config in config.items():
        if ref_key.startswith('_'):  # Ignorer les métadonnées
            continue
        
        try:
            collection_name = ref_config.get('collection', 'referentials')
            key = ref_config.get('key', ref_key)
            version = ref_config.get('version', '1.0')
            items = ref_config.get('items', [])
            
            print(f"📦 {key}")
            print(f"   Collection: {collection_name}")
            print(f"   Version: {version}")
            print(f"   Items: {len(items)}")
            
            # Vérifier si le référentiel existe
            existing = await db[collection_name].find_one({"key": key})
            
            # Préparer le document
            referential_doc = {
                "key": key,
                "version": version,
                "items": items,
                "metadata": {
                    "country": ref_config.get('country'),
                    "region": ref_config.get('region'),
                    "category": ref_config.get('category'),
                },
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            if existing:
                # Mettre à jour
                if existing.get('version') != version or existing.get('items') != items:
                    await db[collection_name].update_one(
                        {"key": key},
                        {"$set": referential_doc}
                    )
                    print(f"   ✅ Mis à jour")
                    stats['updated'] += 1
                else:
                    print(f"   ⏭️  Déjà à jour")
                    stats['skipped'] += 1
            else:
                # Créer
                referential_doc["created_at"] = datetime.now(timezone.utc).isoformat()
                await db[collection_name].insert_one(referential_doc)
                print(f"   ✅ Créé")
                stats['created'] += 1
            
            print()
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}\n")
            stats['errors'] += 1
    
    # Nettoyer les anciens référentiels si demandé
    if clean_old:
        print("🧹 Nettoyage des référentiels obsolètes...")
        
        # Récupérer les clés actuelles
        current_keys = [ref_config.get('key', key) for key, ref_config in config.items() if not key.startswith('_')]
        
        # Supprimer les référentiels qui ne sont plus dans la config
        result = await db.referentials.delete_many({
            "key": {"$nin": current_keys}
        })
        
        if result.deleted_count > 0:
            print(f"   ✅ {result.deleted_count} référentiel(s) obsolète(s) supprimé(s)")
        else:
            print(f"   ℹ️  Aucun référentiel obsolète trouvé")
    
    # Créer les index
    print("\n🔧 Création des index...")
    try:
        await db.referentials.create_index([("key", 1)], unique=True)
        print("   ✅ Index créés")
    except Exception as e:
        print(f"   ℹ️  Index déjà existants")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    ref_count = await db.referentials.count_documents({})
    print(f"   📊 Total référentiels en base: {ref_count}")
    
    client.close()
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ")
    print("=" * 80)
    print(f"\nRéférentiels traités: {stats['total']}")
    print(f"Créés: {stats['created']}")
    print(f"Mis à jour: {stats['updated']}")
    print(f"Déjà à jour: {stats['skipped']}")
    if stats['errors'] > 0:
        print(f"Erreurs: {stats['errors']}")
    
    if stats['created'] + stats['updated'] > 0:
        print(f"\n✅ {stats['created'] + stats['updated']} référentiel(s) initialisé(s) avec succès!")
    else:
        print("\n✅ Tous les référentiels sont déjà à jour!")
    
    print("\n💡 Utilisation:")
    print("   - API: GET /api/referentials/{key}")
    print("   - Frontend: useReferential(key)")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialiser les référentiels depuis la configuration YAML"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Chemin vers un fichier de configuration personnalisé"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Supprimer les référentiels obsolètes"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration
    config = load_config(args.config)
    
    # Exécuter l'initialisation
    asyncio.run(init_referentials(config, clean_old=args.clean))
