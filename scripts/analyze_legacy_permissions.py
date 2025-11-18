#!/usr/bin/env python3
"""
Script pour analyser les permissions legacy et identifier celles qui doivent être migrées ou supprimées.
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

# Connexion MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client['auth_db']

# Collections
permissions_col = db['permissions']
profiles_col = db['profiles']
groups_col = db['groups']
users_col = db['users']

print("=" * 80)
print("ANALYSE DES PERMISSIONS LEGACY")
print("=" * 80)
print()

# 1. Récupérer toutes les permissions
all_permissions = list(permissions_col.find({}, {'_id': 0}))
print(f"📊 Total permissions : {len(all_permissions)}")
print()

# 2. Identifier les permissions par structure
# Nouveau système : a des champs 'resource', 'action', 'scope', 'category'
# Ancien système : peut avoir 'module' ou structure différente

new_permissions = []
legacy_permissions = []
ambiguous_permissions = []

for perm in all_permissions:
    # Vérifier si c'est une permission du nouveau système
    has_resource = 'resource' in perm
    has_action = 'action' in perm
    has_scope = 'scope' in perm
    has_category = 'category' in perm
    
    # Vérifier si c'est une permission legacy
    has_module = 'module' in perm
    has_label = 'label' in perm and not has_category
    
    if has_resource and has_action and has_scope and has_category:
        new_permissions.append(perm)
    elif has_module or (has_label and not has_category):
        legacy_permissions.append(perm)
    else:
        ambiguous_permissions.append(perm)

print(f"✅ Permissions nouveau système : {len(new_permissions)}")
print(f"⚠️  Permissions legacy : {len(legacy_permissions)}")
print(f"❓ Permissions ambiguës : {len(ambiguous_permissions)}")
print()

# 3. Analyser les permissions legacy en détail
if legacy_permissions:
    print("=" * 80)
    print("DÉTAILS DES PERMISSIONS LEGACY")
    print("=" * 80)
    print()
    
    for perm in legacy_permissions:
        print(f"ID: {perm.get('id', 'N/A')}")
        print(f"  Code: {perm.get('code', perm.get('name', 'N/A'))}")
        print(f"  Name: {perm.get('name', 'N/A')}")
        print(f"  Module: {perm.get('module', 'N/A')}")
        print(f"  Label: {perm.get('label', 'N/A')}")
        print(f"  Description: {perm.get('description', 'N/A')}")
        
        # Vérifier si utilisée dans des profils
        profiles_using = list(profiles_col.find(
            {'permission_ids': perm['id']},
            {'_id': 0, 'id': 1, 'name': 1, 'code': 1}
        ))
        
        if profiles_using:
            print(f"  🔗 Utilisée par {len(profiles_using)} profil(s):")
            for profile in profiles_using:
                print(f"     - {profile.get('name', 'N/A')} ({profile.get('code', 'N/A')})")
        else:
            print(f"  ✨ Non utilisée (peut être supprimée)")
        
        print()

# 4. Analyser les profils legacy
print("=" * 80)
print("ANALYSE DES PROFILS")
print("=" * 80)
print()

all_profiles = list(profiles_col.find({}, {'_id': 0}))
print(f"📊 Total profils : {len(all_profiles)}")

legacy_profiles = []
new_profiles = []

for profile in all_profiles:
    # Un profil legacy a soit 'permissions' (liste de strings), soit 'is_system' sans 'is_system_role'
    has_old_permissions = 'permissions' in profile and isinstance(profile.get('permissions'), list)
    has_old_is_system = 'is_system' in profile and 'is_system_role' not in profile
    
    if has_old_permissions or has_old_is_system:
        legacy_profiles.append(profile)
    else:
        new_profiles.append(profile)

print(f"✅ Profils nouveau système : {len(new_profiles)}")
print(f"⚠️  Profils legacy : {len(legacy_profiles)}")
print()

if legacy_profiles:
    print("DÉTAILS DES PROFILS LEGACY:")
    print()
    for profile in legacy_profiles:
        print(f"ID: {profile.get('id', 'N/A')}")
        print(f"  Code: {profile.get('code', 'N/A')}")
        print(f"  Name: {profile.get('name', 'N/A')}")
        print(f"  Category: {profile.get('category', 'N/A')}")
        
        # Vérifier les champs legacy
        if 'permissions' in profile:
            print(f"  ⚠️  Champ 'permissions' trouvé (legacy) : {len(profile['permissions'])} permissions")
        if 'permission_ids' in profile:
            print(f"  ✅ Champ 'permission_ids' trouvé : {len(profile.get('permission_ids', []))} permissions")
        
        # Vérifier si utilisé par des utilisateurs
        users_with_profile = users_col.count_documents({'profile_ids': profile['id']})
        groups_with_profile = groups_col.count_documents({'profile_ids': profile['id']})
        
        print(f"  👥 Utilisé par {users_with_profile} utilisateur(s)")
        print(f"  👥 Utilisé par {groups_with_profile} groupe(s)")
        print()

# 5. Recommandations
print("=" * 80)
print("RECOMMANDATIONS")
print("=" * 80)
print()

# Permissions legacy non utilisées
unused_legacy_perms = [p for p in legacy_permissions 
                       if profiles_col.count_documents({'permission_ids': p['id']}) == 0]

if unused_legacy_perms:
    print(f"🗑️  {len(unused_legacy_perms)} permission(s) legacy non utilisée(s) peuvent être supprimées :")
    for perm in unused_legacy_perms:
        print(f"   - {perm.get('code', perm.get('name', 'N/A'))} (ID: {perm['id']})")
    print()

# Permissions legacy utilisées
used_legacy_perms = [p for p in legacy_permissions 
                     if profiles_col.count_documents({'permission_ids': p['id']}) > 0]

if used_legacy_perms:
    print(f"⚠️  {len(used_legacy_perms)} permission(s) legacy encore utilisée(s) - nécessite migration :")
    for perm in used_legacy_perms:
        profiles_count = profiles_col.count_documents({'permission_ids': perm['id']})
        print(f"   - {perm.get('code', perm.get('name', 'N/A'))} (utilisée par {profiles_count} profil(s))")
    print()

# Profils legacy
if legacy_profiles:
    print(f"⚠️  {len(legacy_profiles)} profil(s) legacy nécessite(nt) migration :")
    for profile in legacy_profiles:
        print(f"   - {profile.get('name', 'N/A')} (Code: {profile.get('code', 'N/A')})")
    print()

print("=" * 80)
print("FIN DE L'ANALYSE")
print("=" * 80)
