#!/usr/bin/env python3
"""
Script de Migration des Permissions vers le Format Moderne
Migre toutes les permissions du format underscore (_own, _all) vers le format point (.own, .all)
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime, timezone

def main():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("MIGRATION DES PERMISSIONS VERS LE FORMAT MODERNE")
    print("=" * 80)
    
    # 1. Identifier toutes les permissions legacy
    all_perms = list(db.permissions.find({}, {'_id': 0}))
    legacy_perms = [p for p in all_perms if '_' in p.get('code', '')]
    
    print(f"\n📊 Permissions à migrer: {len(legacy_perms)}")
    print(f"📊 Profils à mettre à jour: En cours de comptage...")
    
    # 2. Créer le mapping de migration
    migration_map = {}
    permissions_to_rename = []
    permissions_to_replace = []
    
    for perm in legacy_perms:
        old_code = perm['code']
        old_id = perm['id']
        
        # Convertir vers format moderne
        new_code = old_code.replace('_own', '.own').replace('_all', '.all')
        
        # Vérifier si la version moderne existe déjà
        modern_perm = db.permissions.find_one({'code': new_code})
        
        if modern_perm and modern_perm['id'] != old_id:
            # La moderne existe déjà → On va remplacer dans les profils puis supprimer legacy
            migration_map[old_id] = {
                'action': 'replace',
                'old_id': old_id,
                'old_code': old_code,
                'new_id': modern_perm['id'],
                'new_code': new_code
            }
            permissions_to_replace.append(migration_map[old_id])
        else:
            # Pas de version moderne → On renomme directement
            migration_map[old_id] = {
                'action': 'rename',
                'old_id': old_id,
                'old_code': old_code,
                'new_code': new_code
            }
            permissions_to_rename.append(migration_map[old_id])
    
    print(f"\n   - À renommer directement: {len(permissions_to_rename)}")
    print(f"   - À remplacer puis supprimer: {len(permissions_to_replace)}")
    
    # 3. Confirmer avant de continuer
    print(f"\n{'=' * 80}")
    print("APERÇU DES CHANGEMENTS")
    print("=" * 80)
    
    if permissions_to_rename:
        print(f"\n📝 Permissions à RENOMMER ({len(permissions_to_rename)}):")
        for info in permissions_to_rename[:5]:
            print(f"   {info['old_code']:40} → {info['new_code']}")
        if len(permissions_to_rename) > 5:
            print(f"   ... et {len(permissions_to_rename) - 5} autres")
    
    if permissions_to_replace:
        print(f"\n🔄 Permissions à REMPLACER puis SUPPRIMER ({len(permissions_to_replace)}):")
        for info in permissions_to_replace[:5]:
            print(f"   {info['old_code']:40} → {info['new_code']} (existe déjà)")
        if len(permissions_to_replace) > 5:
            print(f"   ... et {len(permissions_to_replace) - 5} autres")
    
    # Demander confirmation
    print(f"\n{'=' * 80}")
    response = input("\n⚠️  Voulez-vous continuer avec la migration ? (yes/no): ")
    if response.lower() not in ['yes', 'y', 'oui', 'o']:
        print("❌ Migration annulée")
        return 1
    
    # 4. Exécuter la migration
    print(f"\n{'=' * 80}")
    print("EXÉCUTION DE LA MIGRATION")
    print("=" * 80)
    
    # Étape 1: Renommer les permissions sans doublon
    print(f"\n1️⃣ Renommage des permissions...")
    renamed_count = 0
    for info in permissions_to_rename:
        result = db.permissions.update_one(
            {'id': info['old_id']},
            {'$set': {
                'code': info['new_code'],
                'updated_at': datetime.now(timezone.utc)
            }}
        )
        if result.modified_count > 0:
            renamed_count += 1
            print(f"   ✅ {info['old_code']} → {info['new_code']}")
    
    print(f"\n   Total renommé: {renamed_count}")
    
    # Étape 2: Remplacer dans les profils
    print(f"\n2️⃣ Remplacement dans les profils...")
    profiles_updated = 0
    
    for info in permissions_to_replace:
        old_id = info['old_id']
        new_id = info['new_id']
        
        # Trouver tous les profils contenant l'ancien ID
        profiles_with_old = db.profiles.find({'permission_ids': old_id})
        
        for profile in profiles_with_old:
            # Remplacer l'ancien ID par le nouveau
            new_perm_ids = [new_id if pid == old_id else pid for pid in profile['permission_ids']]
            
            # Dédupliquer (au cas où le nouveau ID existe déjà)
            new_perm_ids = list(dict.fromkeys(new_perm_ids))
            
            db.profiles.update_one(
                {'id': profile['id']},
                {'$set': {
                    'permission_ids': new_perm_ids,
                    'updated_at': datetime.now(timezone.utc)
                }}
            )
            profiles_updated += 1
            print(f"   ✅ Profil '{profile['name']}': {info['old_code']} → {info['new_code']}")
    
    print(f"\n   Total profils mis à jour: {profiles_updated}")
    
    # Étape 3: Supprimer les permissions legacy en doublon
    print(f"\n3️⃣ Suppression des permissions legacy en doublon...")
    deleted_count = 0
    
    legacy_ids_to_delete = [info['old_id'] for info in permissions_to_replace]
    
    for perm_id in legacy_ids_to_delete:
        perm = db.permissions.find_one({'id': perm_id})
        if perm:
            # Vérifier qu'elle n'est plus utilisée
            still_used = db.profiles.find_one({'permission_ids': perm_id})
            if not still_used:
                db.permissions.delete_one({'id': perm_id})
                deleted_count += 1
                print(f"   ✅ Supprimé: {perm.get('code')}")
            else:
                print(f"   ⚠️  Encore utilisée: {perm.get('code')}")
    
    print(f"\n   Total supprimé: {deleted_count}")
    
    # 5. Vérification finale
    print(f"\n{'=' * 80}")
    print("VÉRIFICATION FINALE")
    print("=" * 80)
    
    remaining_legacy = list(db.permissions.find({'code': {'$regex': '_(own|all)'}}, {'code': 1}))
    print(f"\n📊 Permissions legacy restantes: {len(remaining_legacy)}")
    
    if remaining_legacy:
        print("\n⚠️  Permissions legacy restantes (à vérifier manuellement):")
        for p in remaining_legacy[:10]:
            print(f"   - {p['code']}")
    else:
        print("\n✅ Aucune permission legacy restante !")
    
    # Statistiques finales
    total_modern = db.permissions.count_documents({'code': {'$regex': '\.(own|all)$'}})
    total_perms = db.permissions.count_documents({})
    
    print(f"\n📊 Total permissions: {total_perms}")
    print(f"📊 Permissions modernes (.own/.all): {total_modern}")
    
    print(f"\n{'=' * 80}")
    print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
