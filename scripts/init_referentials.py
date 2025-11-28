#!/usr/bin/env python3
"""
Script d'initialisation des référentiels depuis la configuration YAML
- Crée/met à jour tous les référentiels de données
- Supprime les référentiels obsolètes
- Gère les versions
- Validation des données

Usage:
  python3 init_referentials.py
  python3 init_referentials.py --config /path/to/custom.yaml
  python3 init_referentials.py --clean  # Supprime les anciens référentiels
  python3 init_referentials.py --dry-run  # Simule sans modifier
  python3 init_referentials.py --validate  # Valide seulement la config
  
Version: 2.0 (26 Novembre 2025)
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


def validate_referential_item(item, ref_key):
    """Valide un item de référentiel"""
    errors = []
    
    # Vérifier les champs obligatoires
    if 'code' not in item:
        errors.append(f"  ❌ Item sans 'code' dans {ref_key}")
    
    if 'label' not in item:
        errors.append(f"  ❌ Item '{item.get('code', 'unknown')}' sans 'label' dans {ref_key}")
    elif not isinstance(item['label'], dict):
        errors.append(f"  ❌ Item '{item.get('code')}': 'label' doit être un dictionnaire (fr, en)")
    elif 'fr' not in item['label']:
        errors.append(f"  ❌ Item '{item.get('code')}': label doit contenir 'fr'")
    
    return errors


def validate_config(config):
    """Valide la configuration YAML"""
    print("\n🔍 VALIDATION DE LA CONFIGURATION")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    for ref_key, ref_config in config.items():
        if ref_key.startswith('_'):
            continue
        
        print(f"\n📦 Validation de '{ref_key}'...")
        
        # Vérifier les champs requis
        if 'items' not in ref_config:
            errors.append(f"❌ '{ref_key}': champ 'items' manquant")
            continue
        
        if 'collection' not in ref_config:
            warnings.append(f"⚠️ '{ref_key}': 'collection' non spécifié, utilisation par défaut 'referentials'")
        
        if 'key' not in ref_config:
            warnings.append(f"⚠️ '{ref_key}': 'key' non spécifié, utilisation de '{ref_key}'")
        
        if 'version' not in ref_config:
            warnings.append(f"⚠️ '{ref_key}': 'version' non spécifiée, utilisation par défaut '1.0'")
        
        # Valider les items
        items = ref_config.get('items', [])
        if not items:
            warnings.append(f"⚠️ '{ref_key}': aucun item défini")
        
        # Vérifier les codes uniques
        codes = [item.get('code') for item in items]
        duplicates = [code for code in codes if codes.count(code) > 1]
        if duplicates:
            errors.append(f"❌ '{ref_key}': codes dupliqués: {set(duplicates)}")
        
        # Valider chaque item
        for i, item in enumerate(items):
            item_errors = validate_referential_item(item, ref_key)
            errors.extend(item_errors)
        
        print(f"   ✅ {len(items)} items trouvés")
    
    # Afficher le résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ VALIDATION")
    print("=" * 80)
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} avertissement(s):")
        for warning in warnings[:10]:  # Limiter l'affichage
            print(f"   {warning}")
        if len(warnings) > 10:
            print(f"   ... et {len(warnings) - 10} autres")
    
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) trouvée(s):")
        for error in errors[:10]:
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... et {len(errors) - 10} autres")
        print("\n❌ La configuration contient des erreurs. Veuillez les corriger avant de continuer.")
        return False
    else:
        print(f"\n✅ Configuration valide!")
        return True


def load_config(config_path=None):
    """Charge la configuration des référentiels"""
    config_file = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    
    if not config_file.exists():
        print(f"❌ Fichier de configuration non trouvé: {config_file}")
        sys.exit(1)
    
    print(f"📖 Chargement de la configuration depuis: {config_file}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config:
            print("❌ Fichier de configuration vide")
            sys.exit(1)
        
        print(f"   ✅ {len([k for k in config.keys() if not k.startswith('_')])} référentiel(s) trouvé(s)")
        return config
        
    except yaml.YAMLError as e:
        print(f"❌ Erreur de parsing YAML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        sys.exit(1)


async def init_referentials(config, clean_old=False, dry_run=False):
    """Initialise les référentiels depuis la configuration"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    mode = "MODE SIMULATION (DRY-RUN)" if dry_run else "MODE PRODUCTION"
    print("=" * 80)
    print(f"🔄 INITIALISATION DES RÉFÉRENTIELS ({DB_NAME})")
    print(f"   {mode}")
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
