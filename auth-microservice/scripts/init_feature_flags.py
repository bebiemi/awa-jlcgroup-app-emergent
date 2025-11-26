#!/usr/bin/env python3
"""
Script d'initialisation des feature flags depuis la configuration YAML
- Crée/met à jour tous les feature flags
- Gère le rollout progressif
- Historise les changements

Usage:
  python3 init_feature_flags.py
  python3 init_feature_flags.py --config /path/to/custom.yaml
  python3 init_feature_flags.py --enable chat  # Active un flag spécifique
  python3 init_feature_flags.py --disable chat  # Désactive un flag
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
DEFAULT_CONFIG_FILE = Path(__file__).parent.parent / "config" / "feature_flags_config.yaml"


def load_config(config_path=None):
    """Charge la configuration des feature flags"""
    config_file = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    
    if not config_file.exists():
        print(f"❌ Fichier de configuration non trouvé: {config_file}")
        sys.exit(1)
    
    print(f"📖 Chargement de la configuration depuis: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


async def init_feature_flags(config, enable_flag=None, disable_flag=None):
    """Initialise les feature flags depuis la configuration"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🚩 INITIALISATION DES FEATURE FLAGS ({DB_NAME})")
    print("=" * 80)
    
    stats = {
        'total': 0,
        'created': 0,
        'updated': 0,
        'enabled': 0,
        'disabled': 0,
        'skipped': 0,
    }
    
    # Compter les feature flags
    flag_count = sum(1 for key in config.keys() if not key.startswith('_'))
    stats['total'] = flag_count
    
    print(f"\n📊 {flag_count} feature flag(s) à traiter\n")
    
    # Traiter chaque feature flag
    for flag_key, flag_config in config.items():
        if flag_key.startswith('_'):  # Ignorer les métadonnées
            continue
        
        try:
            key = flag_config.get('key', f'features.{flag_key}')
            name = flag_config.get('name', flag_key)
            enabled = flag_config.get('enabled', False)
            category = flag_config.get('category', 'general')
            description = flag_config.get('description', '')
            
            # Override si demandé en ligne de commande
            if enable_flag and flag_key == enable_flag:
                enabled = True
                print(f"🎚️  Activation forcée de '{flag_key}'")
            elif disable_flag and flag_key == disable_flag:
                enabled = False
                print(f"🎚️  Désactivation forcée de '{flag_key}'")
            
            status_icon = "✅" if enabled else "⏸️ "
            print(f"{status_icon} {name} ({flag_key})")
            print(f"   Key: {key}")
            print(f"   Enabled: {enabled}")
            print(f"   Category: {category}")
            
            # Vérifier si le flag existe
            existing = await db.feature_flags.find_one({"key": key})
            
            # Préparer le document
            flag_doc = {
                "key": key,
                "flag_key": flag_key,
                "name": name,
                "description": description,
                "enabled": enabled,
                "category": category,
                "config": flag_config.get('config', {}),
                "rollout": flag_config.get('rollout', {}),
                "metadata": flag_config.get('metadata', {}),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            if existing:
                # Historiser le changement si le status change
                if existing.get('enabled') != enabled:
                    history_entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "action": "enabled" if enabled else "disabled",
                        "previous_state": existing.get('enabled'),
                        "new_state": enabled,
                    }
                    await db.feature_flags.update_one(
                        {"key": key},
                        {"$push": {"history": history_entry}}
                    )
                
                # Mettre à jour
                await db.feature_flags.update_one(
                    {"key": key},
                    {"$set": flag_doc}
                )
                print(f"   ✅ Mis à jour")
                stats['updated'] += 1
                
                if enabled:
                    stats['enabled'] += 1
                else:
                    stats['disabled'] += 1
            else:
                # Créer
                flag_doc["created_at"] = datetime.now(timezone.utc).isoformat()
                flag_doc["history"] = [{
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "created",
                    "initial_state": enabled,
                }]
                await db.feature_flags.insert_one(flag_doc)
                print(f"   ✅ Créé")
                stats['created'] += 1
                
                if enabled:
                    stats['enabled'] += 1
                else:
                    stats['disabled'] += 1
            
            # Afficher le rollout
            rollout = flag_config.get('rollout', {})
            percentage = rollout.get('percentage', 0)
            if percentage < 100:
                print(f"   📊 Rollout: {percentage}%")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}\n")
    
    # Créer les index
    print("🔧 Création des index...")
    try:
        await db.feature_flags.create_index([("key", 1)], unique=True)
        await db.feature_flags.create_index([("flag_key", 1)])
        await db.feature_flags.create_index([("category", 1)])
        print("   ✅ Index créés")
    except Exception as e:
        print(f"   ℹ️  Index déjà existants")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    flag_count = await db.feature_flags.count_documents({})
    enabled_count = await db.feature_flags.count_documents({"enabled": True})
    print(f"   📊 Total feature flags: {flag_count}")
    print(f"   ✅ Activés: {enabled_count}")
    print(f"   ⏸️  Désactivés: {flag_count - enabled_count}")
    
    client.close()
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ")
    print("=" * 80)
    print(f"\nFeature flags traités: {stats['total']}")
    print(f"Créés: {stats['created']}")
    print(f"Mis à jour: {stats['updated']}")
    print(f"\n📈 État actuel:")
    print(f"Activés: {stats['enabled']}")
    print(f"Désactivés: {stats['disabled']}")
    
    print("\n💡 Utilisation:")
    print("   - API: GET /api/features/flags/{key}")
    print("   - Frontend: useFeatureFlag(key)")
    print("   - Backend: is_feature_enabled(key, user)")
    print("\n📝 Gestion:")
    print("   - Activer: python3 init_feature_flags.py --enable {flag_key}")
    print("   - Désactiver: python3 init_feature_flags.py --disable {flag_key}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialiser les feature flags depuis la configuration YAML"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Chemin vers un fichier de configuration personnalisé"
    )
    parser.add_argument(
        "--enable",
        type=str,
        metavar="FLAG_KEY",
        help="Activer un feature flag spécifique"
    )
    parser.add_argument(
        "--disable",
        type=str,
        metavar="FLAG_KEY",
        help="Désactiver un feature flag spécifique"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration
    config = load_config(args.config)
    
    # Exécuter l'initialisation
    asyncio.run(init_feature_flags(
        config,
        enable_flag=args.enable,
        disable_flag=args.disable
    ))
