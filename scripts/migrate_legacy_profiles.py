#!/usr/bin/env python3
"""
Script de migration des profils legacy vers le nouveau système IAM.
Supprime ou désactive les profils legacy non utilisés.
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime, timezone

# Connexion MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client['auth_db']

# Collections
profiles_col = db['profiles']
users_col = db['users']
groups_col = db['groups']

print("=" * 80)
print("MIGRATION DES PROFILS LEGACY")
print("=" * 80)
print()

# Mode dry-run par défaut
DRY_RUN = '--execute' not in sys.argv

if DRY_RUN:
    print("🔍 MODE DRY-RUN (simulation)")
    print("   Ajoutez --execute pour appliquer les changements")
    print()
else:
    print("⚠️  MODE EXECUTION - Les changements seront appliqués !")
    print()

# 1. Identifier les profils legacy
legacy_profiles = []

all_profiles = list(profiles_col.find({}, {'_id': 0}))

for profile in all_profiles:
    # Un profil est legacy s'il a l'ancien champ 'permissions' (liste de strings)
    # ou s'il a 'is_system' sans 'is_system_role'
    has_old_permissions = 'permissions' in profile and isinstance(profile.get('permissions'), list)
    has_old_is_system = 'is_system' in profile and 'is_system_role' not in profile
    missing_protection = 'is_protected' not in profile
    
    if has_old_permissions or has_old_is_system or missing_protection:
        legacy_profiles.append(profile)

print(f"📊 Profils legacy trouvés : {len(legacy_profiles)}")
print()

# 2. Analyser et traiter chaque profil legacy
actions = {
    'delete': [],
    'update': [],
    'keep': []
}

for profile in legacy_profiles:
    profile_id = profile.get('id')
    profile_name = profile.get('name', 'N/A')
    profile_code = profile.get('code', 'N/A')
    
    # Vérifier l'utilisation
    users_count = users_col.count_documents({'profile_ids': profile_id})
    groups_count = groups_col.count_documents({'profile_ids': profile_id})
    
    print(f"Profil: {profile_name} (Code: {profile_code})")
    print(f"  ID: {profile_id}")
    print(f"  Utilisé par {users_count} utilisateur(s) et {groups_count} groupe(s)")
    
    # Décision
    if users_count == 0 and groups_count == 0:
        # Profil non utilisé - peut être supprimé
        if profile.get('category') == 'legacy':
            print(f"  ✅ Action: SUPPRESSION (non utilisé et catégorie legacy)")
            actions['delete'].append(profile)
        else:
            print(f"  ⚠️  Action: MISE À JOUR (non utilisé mais pas catégorie legacy)")
            actions['update'].append(profile)
    else:
        # Profil utilisé - doit être migré
        print(f"  ⚠️  Action: MISE À JOUR (utilisé par des utilisateurs/groupes)")
        actions['update'].append(profile)
    
    print()

# 3. Afficher le résumé des actions
print("=" * 80)
print("RÉSUMÉ DES ACTIONS")
print("=" * 80)
print()

print(f"🗑️  Profils à supprimer : {len(actions['delete'])}")
for profile in actions['delete']:
    print(f"   - {profile.get('name')} ({profile.get('code')})")
print()

print(f"🔄 Profils à mettre à jour : {len(actions['update'])}")
for profile in actions['update']:
    print(f"   - {profile.get('name')} ({profile.get('code')})")
print()

# 4. Exécuter les actions si mode --execute
if not DRY_RUN:
    print("=" * 80)
    print("EXECUTION DES ACTIONS")
    print("=" * 80)
    print()
    
    # Supprimer les profils non utilisés
    for profile in actions['delete']:
        profile_id = profile.get('id')
        result = profiles_col.delete_one({'id': profile_id})
        if result.deleted_count > 0:
            print(f"✅ Supprimé : {profile.get('name')} ({profile.get('code')})")
        else:
            print(f"❌ Échec suppression : {profile.get('name')} ({profile.get('code')})")
    
    # Mettre à jour les profils utilisés
    for profile in actions['update']:
        profile_id = profile.get('id')
        
        updates = {}
        
        # Supprimer l'ancien champ 'permissions' s'il existe
        unset_fields = {}
        if 'permissions' in profile:
            unset_fields['permissions'] = ""
        
        if 'is_system' in profile and 'is_system_role' not in profile:
            unset_fields['is_system'] = ""
            # Ajouter le nouveau champ
            updates['is_system_role'] = profile.get('is_system', False)
        
        # Ajouter le champ is_protected s'il manque
        if 'is_protected' not in profile:
            updates['is_protected'] = False
        
        # S'assurer que permission_ids existe
        if 'permission_ids' not in profile:
            updates['permission_ids'] = []
        
        # Mettre à jour updated_at
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Exécuter la mise à jour
        update_doc = {}
        if updates:
            update_doc['$set'] = updates
        if unset_fields:
            update_doc['$unset'] = unset_fields
        
        if update_doc:
            result = profiles_col.update_one({'id': profile_id}, update_doc)
            if result.modified_count > 0:
                print(f"✅ Mis à jour : {profile.get('name')} ({profile.get('code')})")
                if unset_fields:
                    print(f"   - Champs supprimés : {', '.join(unset_fields.keys())}")
                if updates:
                    print(f"   - Champs ajoutés/modifiés : {', '.join(updates.keys())}")
            else:
                print(f"⚠️  Aucune modification : {profile.get('name')} ({profile.get('code')})")
        else:
            print(f"ℹ️  Aucune action nécessaire : {profile.get('name')} ({profile.get('code')})")
    
    print()
    print("=" * 80)
    print("MIGRATION TERMINÉE")
    print("=" * 80)
else:
    print()
    print("=" * 80)
    print("Pour appliquer ces changements, exécutez :")
    print("  python3 scripts/migrate_legacy_profiles.py --execute")
    print("=" * 80)
