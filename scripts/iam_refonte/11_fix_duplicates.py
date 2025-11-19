"""
Script 11: Correction des permissions dupliquées
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def fix_duplicate_permissions():
    """Corriger les permissions dupliquées"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🔧 CORRECTION DES PERMISSIONS DUPLIQUÉES")
    print("=" * 80)
    
    # Récupérer toutes les permissions
    all_perms = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    
    # Trouver les doublons
    from collections import defaultdict
    perms_by_code = defaultdict(list)
    
    for perm in all_perms:
        code = perm.get('code')
        perms_by_code[code].append(perm)
    
    duplicates = {code: perms for code, perms in perms_by_code.items() if len(perms) > 1}
    
    print(f"\n📊 Permissions dupliquées trouvées: {len(duplicates)}")
    
    for code, perms in duplicates.items():
        print(f"\n🔍 Code: {code} ({len(perms)} occurrences)")
        
        # Analyser les différences
        for i, perm in enumerate(perms, 1):
            print(f"   {i}. ID: {perm['id']}")
            print(f"      Name: {perm.get('name')}")
            print(f"      Resource: {perm.get('resource')}")
            print(f"      Action: {perm.get('action')}")
            print(f"      Category: {perm.get('category')}")
        
        # Garder la meilleure version (la plus complète)
        best_perm = max(perms, key=lambda p: (
            len(p.get('description', '')),
            len(p.get('name', '')),
            p.get('category') != 'builtin'  # Préférer non-builtin
        ))
        
        print(f"\n   ✅ Meilleure version: {best_perm['id']}")
        
        # Récupérer profils et bundles
        profiles = await db.profiles.find({}, {"_id": 0}).to_list(1000)
        bundles = await db.capability_bundles.find({}, {"_id": 0}).to_list(1000)
        
        # Remplacer tous les IDs par le meilleur
        best_id = best_perm['id']
        ids_to_remove = [p['id'] for p in perms if p['id'] != best_id]
        
        print(f"   🗑️  IDs à supprimer: {ids_to_remove}")
        
        # Mise à jour des profils
        for profile in profiles:
            perm_ids = profile.get('permission_ids', [])
            updated = False
            
            for old_id in ids_to_remove:
                if old_id in perm_ids:
                    perm_ids.remove(old_id)
                    if best_id not in perm_ids:
                        perm_ids.append(best_id)
                    updated = True
            
            if updated:
                await db.profiles.update_one(
                    {"code": profile['code']},
                    {"$set": {"permission_ids": perm_ids}}
                )
                print(f"      ✓ Profil '{profile['code']}' mis à jour")
        
        # Mise à jour des bundles
        for bundle in bundles:
            perm_ids = bundle.get('permission_ids', [])
            updated = False
            
            for old_id in ids_to_remove:
                if old_id in perm_ids:
                    perm_ids.remove(old_id)
                    if best_id not in perm_ids:
                        perm_ids.append(best_id)
                    updated = True
            
            if updated:
                await db.capability_bundles.update_one(
                    {"code": bundle['code']},
                    {"$set": {"permission_ids": perm_ids}}
                )
                print(f"      ✓ Bundle '{bundle['code']}' mis à jour")
        
        # Supprimer les doublons
        for old_id in ids_to_remove:
            result = await db.permissions.delete_one({"id": old_id})
            if result.deleted_count > 0:
                print(f"      ✓ Permission {old_id} supprimée")
    
    print("\n" + "=" * 80)
    print("✅ CORRECTION TERMINÉE")
    print("=" * 80)
    
    # Vérification finale
    all_perms_after = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    codes_after = [p.get('code') for p in all_perms_after]
    duplicates_after = [code for code in set(codes_after) if codes_after.count(code) > 1]
    
    print(f"\n📊 Permissions restantes: {len(all_perms_after)}")
    print(f"   • Doublons restants: {len(duplicates_after)}")
    
    if not duplicates_after:
        print(f"\n✅ Aucun doublon restant")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(fix_duplicate_permissions())
