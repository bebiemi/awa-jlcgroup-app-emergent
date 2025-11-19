"""
Script 9: Nettoyage des références orphelines
Supprime les IDs de permissions qui n'existent plus des profils et bundles
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def cleanup_orphan_references():
    """Nettoyer les références orphelines dans profils et bundles"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🧹 NETTOYAGE DES RÉFÉRENCES ORPHELINES")
    print("=" * 80)
    
    # Récupérer tous les IDs de permissions valides
    all_perms = await db.permissions.find({}, {"_id": 0, "id": 1}).to_list(10000)
    valid_perm_ids = {p['id'] for p in all_perms}
    
    print(f"\n📊 Permissions valides: {len(valid_perm_ids)}")
    
    # Nettoyer les profils
    profiles = await db.profiles.find({}, {"_id": 0}).to_list(1000)
    
    print(f"\n🔍 Vérification des profils...")
    profiles_cleaned = 0
    refs_removed = 0
    
    for profile in profiles:
        perm_ids = profile.get('permission_ids', [])
        original_count = len(perm_ids)
        
        # Filtrer pour ne garder que les IDs valides
        cleaned_perm_ids = [pid for pid in perm_ids if pid in valid_perm_ids]
        orphan_ids = [pid for pid in perm_ids if pid not in valid_perm_ids]
        
        if len(cleaned_perm_ids) < original_count:
            # Il y a des orphelins à nettoyer
            await db.profiles.update_one(
                {"code": profile['code']},
                {"$set": {"permission_ids": cleaned_perm_ids}}
            )
            
            removed = original_count - len(cleaned_perm_ids)
            refs_removed += removed
            profiles_cleaned += 1
            
            print(f"   ✓ Profil '{profile['code']}': {removed} référence(s) orpheline(s) supprimée(s)")
            for oid in orphan_ids[:3]:
                print(f"      → {oid}")
            if len(orphan_ids) > 3:
                print(f"      ... et {len(orphan_ids) - 3} autres")
    
    # Nettoyer les bundles
    bundles = await db.capability_bundles.find({}, {"_id": 0}).to_list(1000)
    
    print(f"\n🔍 Vérification des bundles...")
    bundles_cleaned = 0
    
    for bundle in bundles:
        perm_ids = bundle.get('permission_ids', [])
        original_count = len(perm_ids)
        
        # Filtrer pour ne garder que les IDs valides
        cleaned_perm_ids = [pid for pid in perm_ids if pid in valid_perm_ids]
        orphan_ids = [pid for pid in perm_ids if pid not in valid_perm_ids]
        
        if len(cleaned_perm_ids) < original_count:
            # Il y a des orphelins à nettoyer
            await db.capability_bundles.update_one(
                {"code": bundle['code']},
                {"$set": {"permission_ids": cleaned_perm_ids}}
            )
            
            removed = original_count - len(cleaned_perm_ids)
            refs_removed += removed
            bundles_cleaned += 1
            
            print(f"   ✓ Bundle '{bundle['code']}': {removed} référence(s) orpheline(s) supprimée(s)")
            for oid in orphan_ids[:3]:
                print(f"      → {oid}")
    
    print("\n" + "=" * 80)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 80)
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Profils nettoyés: {profiles_cleaned}")
    print(f"   • Bundles nettoyés: {bundles_cleaned}")
    print(f"   • Total références orphelines supprimées: {refs_removed}")
    
    # Vérification finale
    print(f"\n🔍 Vérification finale...")
    
    # Re-vérifier
    profiles = await db.profiles.find({}, {"_id": 0}).to_list(1000)
    bundles = await db.capability_bundles.find({}, {"_id": 0}).to_list(1000)
    
    orphans_found = 0
    for profile in profiles:
        for perm_id in profile.get('permission_ids', []):
            if perm_id not in valid_perm_ids:
                orphans_found += 1
    
    for bundle in bundles:
        for perm_id in bundle.get('permission_ids', []):
            if perm_id not in valid_perm_ids:
                orphans_found += 1
    
    if orphans_found == 0:
        print(f"   ✅ Aucune référence orpheline trouvée")
    else:
        print(f"   ⚠️  {orphans_found} référence(s) orpheline(s) restante(s)")
    
    client.close()
    
    return {
        "profiles_cleaned": profiles_cleaned,
        "bundles_cleaned": bundles_cleaned,
        "refs_removed": refs_removed,
        "orphans_remaining": orphans_found
    }


if __name__ == '__main__':
    asyncio.run(cleanup_orphan_references())
