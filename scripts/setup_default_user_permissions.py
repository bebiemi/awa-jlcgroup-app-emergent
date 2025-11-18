#!/usr/bin/env python3
"""
Script pour implémenter les droits utilisateur par défaut.
Chaque utilisateur doit pouvoir :
1. Modifier son propre profil
2. Accéder à un tableau de bord par défaut
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
permissions_col = db['permissions']
profiles_col = db['profiles']

print("=" * 80)
print("CONFIGURATION DES PERMISSIONS PAR DÉFAUT")
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

# 1. Vérifier les permissions nécessaires
required_permissions = [
    {
        'code': 'profile.view_own',
        'name': 'Voir son propre profil',
        'description': 'Permet à un utilisateur de consulter son propre profil',
        'resource': 'profile',
        'action': 'view',
        'scope': '_own',
        'category': 'user',
        'is_system': True
    },
    {
        'code': 'profile.edit_own',
        'name': 'Modifier son propre profil',
        'description': 'Permet à un utilisateur de modifier son propre profil',
        'resource': 'profile',
        'action': 'edit',
        'scope': '_own',
        'category': 'user',
        'is_system': True
    },
    {
        'code': 'dashboard.access',
        'name': 'Accéder au tableau de bord',
        'description': 'Permet à un utilisateur d\'accéder à son tableau de bord',
        'resource': 'dashboard',
        'action': 'view',
        'scope': 'global',
        'category': 'system',
        'is_system': True
    }
]

print("📋 Vérification des permissions par défaut...")
print()

permissions_to_create = []
existing_permission_ids = []

for perm_data in required_permissions:
    # Vérifier si la permission existe
    existing = permissions_col.find_one({'code': perm_data['code']})
    
    if existing:
        print(f"✅ Permission existe : {perm_data['code']}")
        existing_permission_ids.append(existing['id'])
    else:
        print(f"⚠️  Permission manquante : {perm_data['code']}")
        permissions_to_create.append(perm_data)
        existing_permission_ids.append(None)  # Placeholder

print()

# 2. Créer les permissions manquantes
if permissions_to_create:
    print(f"📝 {len(permissions_to_create)} permission(s) à créer")
    print()
    
    if not DRY_RUN:
        import uuid
        
        for i, perm_data in enumerate(permissions_to_create):
            perm_id = str(uuid.uuid4())
            perm_doc = {
                'id': perm_id,
                **perm_data,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            permissions_col.insert_one(perm_doc)
            print(f"✅ Créée : {perm_data['code']} (ID: {perm_id})")
            
            # Mettre à jour l'ID dans la liste
            idx = [p['code'] for p in required_permissions].index(perm_data['code'])
            existing_permission_ids[idx] = perm_id
        
        print()

# 3. Récupérer les IDs des permissions (après création si nécessaire)
if not DRY_RUN or not permissions_to_create:
    final_permission_ids = []
    for perm_data in required_permissions:
        perm = permissions_col.find_one({'code': perm_data['code']})
        if perm:
            final_permission_ids.append(perm['id'])
    
    print(f"📊 Permissions par défaut identifiées : {len(final_permission_ids)}")
    for perm_id in final_permission_ids:
        perm = permissions_col.find_one({'id': perm_id})
        print(f"   - {perm['code']}")
    print()
else:
    final_permission_ids = []

# 4. Vérifier les profils de base
print("=" * 80)
print("VÉRIFICATION DES PROFILS DE BASE")
print("=" * 80)
print()

# Profils qui doivent avoir les permissions par défaut
base_profiles = [
    {
        'code': 'candidat',
        'name': 'Candidat',
        'category': 'business',
        'description': 'Profil de base pour un candidat/intérimaire'
    },
    {
        'code': 'interimaire',
        'name': 'Intérimaire',
        'category': 'business',
        'description': 'Profil de base pour un intérimaire actif'
    },
    {
        'code': 'company_user',
        'name': 'Utilisateur Entreprise',
        'category': 'business',
        'description': 'Profil de base pour un utilisateur d\'entreprise'
    }
]

profiles_to_update = []

for profile_data in base_profiles:
    profile = profiles_col.find_one({'code': profile_data['code']})
    
    if profile:
        print(f"✅ Profil trouvé : {profile_data['code']}")
        
        # Vérifier si les permissions par défaut sont présentes
        current_perms = set(profile.get('permission_ids', []))
        missing_perms = [p for p in final_permission_ids if p not in current_perms]
        
        if missing_perms:
            print(f"   ⚠️  {len(missing_perms)} permission(s) par défaut manquante(s)")
            profiles_to_update.append({
                'profile': profile,
                'missing_perms': missing_perms
            })
        else:
            print(f"   ✅ Toutes les permissions par défaut présentes")
    else:
        print(f"⚠️  Profil non trouvé : {profile_data['code']}")
    
    print()

# 5. Mettre à jour les profils
if profiles_to_update and not DRY_RUN:
    print("=" * 80)
    print("MISE À JOUR DES PROFILS")
    print("=" * 80)
    print()
    
    for item in profiles_to_update:
        profile = item['profile']
        missing_perms = item['missing_perms']
        
        # Ajouter les permissions manquantes
        new_perms = list(set(profile.get('permission_ids', []) + missing_perms))
        
        result = profiles_col.update_one(
            {'id': profile['id']},
            {
                '$set': {
                    'permission_ids': new_perms,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Mis à jour : {profile['name']} ({profile['code']})")
            print(f"   - Ajouté {len(missing_perms)} permission(s)")
        else:
            print(f"⚠️  Échec mise à jour : {profile['name']} ({profile['code']})")
    
    print()

# 6. Résumé
print("=" * 80)
print("RÉSUMÉ")
print("=" * 80)
print()

if DRY_RUN:
    print(f"📝 Permissions à créer : {len(permissions_to_create)}")
    print(f"🔄 Profils à mettre à jour : {len(profiles_to_update)}")
    print()
    print("=" * 80)
    print("Pour appliquer ces changements, exécutez :")
    print("  python3 scripts/setup_default_user_permissions.py --execute")
    print("=" * 80)
else:
    print(f"✅ Permissions créées : {len(permissions_to_create)}")
    print(f"✅ Profils mis à jour : {len(profiles_to_update)}")
    print()
    print("=" * 80)
    print("CONFIGURATION TERMINÉE")
    print("=" * 80)
