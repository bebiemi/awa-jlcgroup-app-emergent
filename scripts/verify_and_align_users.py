#!/usr/bin/env python3
"""
Script dynamique de vérification et alignement des comptes utilisateurs
- Lit la configuration depuis /app/config/iam_config.yaml
- Vérifie tous les comptes utilisateurs
- Aligne automatiquement les champs manquants/incorrects
- Corrige les problèmes legacy (password → password_hash)
- Active les comptes super_admin
- Génère un rapport détaillé

Usage:
  python3 verify_and_align_users.py              # Vérification seule
  python3 verify_and_align_users.py --fix        # Vérification + correction
  python3 verify_and_align_users.py --fix --activate-admins  # Avec activation des admins
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
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")
CONFIG_FILE = Path(__file__).parent.parent / "config" / "iam_config.yaml"


def load_config():
    """Charge la configuration IAM depuis le fichier YAML"""
    if not CONFIG_FILE.exists():
        print(f"❌ Fichier de configuration non trouvé: {CONFIG_FILE}")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


async def verify_and_align_users(fix=False, activate_admins=False):
    """Vérifie et aligne les comptes utilisateurs selon la configuration"""
    
    config = load_config()
    validation_rules = config.get('user_validation_rules', {})
    
    required_fields = validation_rules.get('required_fields', [])
    default_values = validation_rules.get('default_values', {})
    active_requirements = validation_rules.get('active_user_requirements', {})
    field_migrations = validation_rules.get('field_migrations', {})
    deprecated_fields = validation_rules.get('deprecated_fields', [])
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🔍 VÉRIFICATION ET ALIGNEMENT DES COMPTES UTILISATEURS")
    print(f"Mode: {'CORRECTION' if fix else 'LECTURE SEULE'}")
    print("=" * 80)
    
    # Statistiques
    stats = {
        'total_users': 0,
        'valid_users': 0,
        'users_with_issues': 0,
        'issues_found': [],
        'migrations_applied': 0,
        'fields_added': 0,
        'fields_removed': 0,
        'admins_activated': 0,
    }
    
    # Récupérer tous les utilisateurs
    users = await db.users.find({}).to_list(length=1000)
    stats['total_users'] = len(users)
    
    print(f"\n📊 Analyse de {stats['total_users']} utilisateur(s)...\n")
    
    issues_by_user = {}
    
    for user in users:
        username = user.get('username', user.get('id', 'UNKNOWN'))
        user_issues = []
        
        # 1. Vérifier les champs requis
        for field in required_fields:
            if field not in user or user[field] is None:
                user_issues.append({
                    'type': 'missing_field',
                    'field': field,
                    'fix': default_values.get(field, 'N/A')
                })
        
        # 2. Vérifier les migrations de champs
        for old_field, new_field in field_migrations.items():
            if old_field in user and new_field not in user:
                user_issues.append({
                    'type': 'field_migration',
                    'old_field': old_field,
                    'new_field': new_field,
                })
        
        # 3. Vérifier les champs deprecated
        for dep_field in deprecated_fields:
            if dep_field in user:
                user_issues.append({
                    'type': 'deprecated_field',
                    'field': dep_field,
                })
        
        # 4. Vérifier les comptes super_admin inactifs
        if 'super_admin' in user.get('roles', []):
            if user.get('status') != 'active' or not user.get('is_active'):
                user_issues.append({
                    'type': 'inactive_admin',
                    'status': user.get('status'),
                    'is_active': user.get('is_active'),
                })
        
        # Enregistrer les issues
        if user_issues:
            issues_by_user[username] = user_issues
            stats['users_with_issues'] += 1
        else:
            stats['valid_users'] += 1
    
    # Afficher les issues trouvées
    if issues_by_user:
        print(f"⚠️  {stats['users_with_issues']} utilisateur(s) avec problèmes:\n")
        
        for username, issues in issues_by_user.items():
            print(f"👤 {username}:")
            for issue in issues:
                if issue['type'] == 'missing_field':
                    print(f"   ❌ Champ manquant: {issue['field']} (défaut: {issue['fix']})")
                elif issue['type'] == 'field_migration':
                    print(f"   🔄 Migration nécessaire: {issue['old_field']} → {issue['new_field']}")
                elif issue['type'] == 'deprecated_field':
                    print(f"   🗑️  Champ obsolète: {issue['field']}")
                elif issue['type'] == 'inactive_admin':
                    print(f"   🔒 Compte admin inactif: status={issue['status']}, is_active={issue['is_active']}")
            print()
    else:
        print("✅ Tous les utilisateurs sont conformes!\n")
    
    # Appliquer les corrections si demandé
    if fix and issues_by_user:
        print("=" * 80)
        print("🔧 APPLICATION DES CORRECTIONS")
        print("=" * 80 + "\n")
        
        for username, issues in issues_by_user.items():
            user = await db.users.find_one({'username': username})
            if not user:
                continue
            
            updates = {}
            renames = {}
            unsets = {}
            
            for issue in issues:
                if issue['type'] == 'missing_field':
                    field = issue['field']
                    updates[field] = default_values.get(field)
                    stats['fields_added'] += 1
                    
                elif issue['type'] == 'field_migration':
                    renames[issue['old_field']] = issue['new_field']
                    stats['migrations_applied'] += 1
                    
                elif issue['type'] == 'deprecated_field':
                    unsets[issue['field']] = ""
                    stats['fields_removed'] += 1
                    
                elif issue['type'] == 'inactive_admin' and activate_admins:
                    updates.update(active_requirements)
                    stats['admins_activated'] += 1
            
            # Ajouter updated_at
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Construire la requête de mise à jour
            update_query = {}
            if updates:
                update_query['$set'] = updates
            if renames:
                update_query['$rename'] = renames
            if unsets:
                update_query['$unset'] = unsets
            
            if update_query:
                await db.users.update_one(
                    {'username': username},
                    update_query
                )
                print(f"✅ {username}: Corrigé ({len(issues)} problème(s))")
        
        print(f"\n✅ Corrections appliquées!")
    
    elif fix and not issues_by_user:
        print("✅ Aucune correction nécessaire - tous les utilisateurs sont conformes!")
    
    elif not fix and issues_by_user:
        print("\n💡 Pour appliquer les corrections, exécutez:")
        print("   python3 verify_and_align_users.py --fix")
        has_inactive_admins = any(
            issue['type'] == 'inactive_admin' 
            for issues in issues_by_user.values() 
            for issue in issues
        )
        if has_inactive_admins:
            print("   python3 verify_and_align_users.py --fix --activate-admins")
    
    # Vérification finale
    if fix:
        print("\n" + "=" * 80)
        print("🔍 VÉRIFICATION POST-CORRECTION")
        print("=" * 80 + "\n")
        
        # Recompter les utilisateurs valides
        users_after = await db.users.find({}).to_list(length=1000)
        valid_after = 0
        
        for user in users_after:
            all_fields_present = all(field in user and user[field] is not None for field in required_fields)
            if all_fields_present:
                valid_after += 1
        
        print(f"✅ Utilisateurs conformes: {valid_after}/{len(users_after)}")
    
    client.close()
    
    # Rapport final
    print("\n" + "=" * 80)
    print("📊 RAPPORT FINAL")
    print("=" * 80)
    print(f"\n📈 Statistiques:")
    print(f"   Total utilisateurs: {stats['total_users']}")
    print(f"   Utilisateurs conformes: {stats['valid_users']}")
    print(f"   Utilisateurs avec problèmes: {stats['users_with_issues']}")
    
    if fix:
        print(f"\n🔧 Corrections appliquées:")
        print(f"   Migrations de champs: {stats['migrations_applied']}")
        print(f"   Champs ajoutés: {stats['fields_added']}")
        print(f"   Champs supprimés: {stats['fields_removed']}")
        if activate_admins:
            print(f"   Admins activés: {stats['admins_activated']}")
    
    print("\n" + "=" * 80)
    
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Vérifier et aligner les comptes utilisateurs selon la configuration IAM"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Appliquer les corrections automatiquement"
    )
    parser.add_argument(
        "--activate-admins",
        action="store_true",
        help="Activer automatiquement les comptes super_admin inactifs"
    )
    
    args = parser.parse_args()
    
    asyncio.run(verify_and_align_users(
        fix=args.fix,
        activate_admins=args.activate_admins
    ))
