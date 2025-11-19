"""
Script 10: Test d'intégrité IAM après nettoyage
Valide que le système IAM fonctionne correctement après la migration
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from collections import defaultdict


async def test_permissions_integrity():
    """Tester l'intégrité des permissions"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🔍 TEST D'INTÉGRITÉ DES PERMISSIONS")
    print("=" * 80)
    
    all_perms = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    
    issues = []
    
    # 1. Vérifier que toutes les permissions ont le format moderne
    legacy_format_count = 0
    for perm in all_perms:
        code = perm.get('code', '')
        has_resource = bool(perm.get('resource'))
        has_action = bool(perm.get('action'))
        
        if not ('.' in code and has_resource and has_action):
            legacy_format_count += 1
            issues.append(f"❌ Permission en format legacy: {code}")
    
    if legacy_format_count == 0:
        print(f"\n✅ Format: Toutes les {len(all_perms)} permissions sont au format moderne")
    else:
        print(f"\n⚠️  Format: {legacy_format_count} permissions en format legacy")
    
    # 2. Vérifier qu'il n'y a pas de doublons
    codes = [p.get('code') for p in all_perms]
    duplicates = [code for code in set(codes) if codes.count(code) > 1]
    
    if not duplicates:
        print(f"✅ Doublons: Aucun doublon trouvé")
    else:
        print(f"⚠️  Doublons: {len(duplicates)} codes dupliqués")
        for dup in duplicates[:5]:
            issues.append(f"❌ Permission dupliquée: {dup}")
    
    # 3. Vérifier que toutes les permissions ont les champs requis
    incomplete = []
    for perm in all_perms:
        if not all([
            perm.get('id'),
            perm.get('code'),
            perm.get('name'),
            perm.get('resource'),
            perm.get('action')
        ]):
            incomplete.append(perm.get('code', 'UNKNOWN'))
    
    if not incomplete:
        print(f"✅ Complétude: Toutes les permissions ont les champs requis")
    else:
        print(f"⚠️  Complétude: {len(incomplete)} permissions incomplètes")
        for inc in incomplete[:5]:
            issues.append(f"❌ Permission incomplète: {inc}")
    
    client.close()
    return issues


async def test_profiles_integrity():
    """Tester l'intégrité des profils"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🔍 TEST D'INTÉGRITÉ DES PROFILS")
    print("=" * 80)
    
    profiles = await db.profiles.find({}, {"_id": 0}).to_list(1000)
    all_perms = await db.permissions.find({}, {"_id": 0, "id": 1}).to_list(10000)
    valid_perm_ids = {p['id'] for p in all_perms}
    
    issues = []
    
    # 1. Vérifier les références orphelines
    total_orphans = 0
    for profile in profiles:
        orphans = []
        for perm_id in profile.get('permission_ids', []):
            if perm_id not in valid_perm_ids:
                orphans.append(perm_id)
        
        if orphans:
            total_orphans += len(orphans)
            issues.append(f"❌ Profil '{profile['code']}' a {len(orphans)} référence(s) orpheline(s)")
    
    if total_orphans == 0:
        print(f"\n✅ Références: Aucune référence orpheline dans les profils")
    else:
        print(f"\n⚠️  Références: {total_orphans} référence(s) orpheline(s) trouvée(s)")
    
    # 2. Statistiques par profil
    print(f"\n📊 STATISTIQUES PAR PROFIL:")
    print(f"{'Code':<30} {'Permissions':<15} {'Bundles':<10}")
    print("-" * 60)
    
    for profile in sorted(profiles, key=lambda p: len(p.get('permission_ids', [])), reverse=True)[:10]:
        code = profile.get('code', 'unknown')
        perm_count = len(profile.get('permission_ids', []))
        bundle_count = len(profile.get('capability_bundle_ids', []))
        print(f"{code:<30} {perm_count:<15} {bundle_count:<10}")
    
    client.close()
    return issues


async def test_bundles_integrity():
    """Tester l'intégrité des bundles"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🔍 TEST D'INTÉGRITÉ DES BUNDLES")
    print("=" * 80)
    
    bundles = await db.capability_bundles.find({}, {"_id": 0}).to_list(1000)
    all_perms = await db.permissions.find({}, {"_id": 0, "id": 1}).to_list(10000)
    valid_perm_ids = {p['id'] for p in all_perms}
    
    issues = []
    
    # 1. Vérifier les références orphelines
    total_orphans = 0
    for bundle in bundles:
        orphans = []
        for perm_id in bundle.get('permission_ids', []):
            if perm_id not in valid_perm_ids:
                orphans.append(perm_id)
        
        if orphans:
            total_orphans += len(orphans)
            issues.append(f"❌ Bundle '{bundle['code']}' a {len(orphans)} référence(s) orpheline(s)")
    
    if total_orphans == 0:
        print(f"\n✅ Références: Aucune référence orpheline dans les bundles")
    else:
        print(f"\n⚠️  Références: {total_orphans} référence(s) orpheline(s) trouvée(s)")
    
    # 2. Statistiques
    print(f"\n📊 Total bundles: {len(bundles)}")
    if bundles:
        total_perms = sum(len(b.get('permission_ids', [])) for b in bundles)
        avg_perms = total_perms / len(bundles) if bundles else 0
        print(f"   • Permissions totales: {total_perms}")
        print(f"   • Moyenne par bundle: {avg_perms:.1f}")
    
    client.close()
    return issues


async def test_users_integrity():
    """Tester l'intégrité des utilisateurs"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🔍 TEST D'INTÉGRITÉ DES UTILISATEURS")
    print("=" * 80)
    
    users = await db.users.find({}, {"_id": 0, "username": 1, "roles": 1, "profile_codes": 1}).to_list(10000)
    profiles = await db.profiles.find({}, {"_id": 0, "code": 1}).to_list(1000)
    valid_profile_codes = {p['code'] for p in profiles}
    
    issues = []
    
    # Vérifier que les utilisateurs ont des profils valides
    users_without_profiles = 0
    users_with_invalid_profiles = 0
    
    for user in users:
        profile_codes = user.get('profile_codes', [])
        
        if not profile_codes:
            users_without_profiles += 1
        
        for code in profile_codes:
            if code not in valid_profile_codes:
                users_with_invalid_profiles += 1
                issues.append(f"❌ User '{user.get('username')}' a un profil invalide: {code}")
                break
    
    print(f"\n📊 Total utilisateurs: {len(users)}")
    print(f"   • Sans profil: {users_without_profiles}")
    print(f"   • Avec profil invalide: {users_with_invalid_profiles}")
    
    if users_without_profiles == 0 and users_with_invalid_profiles == 0:
        print(f"\n✅ Tous les utilisateurs ont des profils valides")
    
    client.close()
    return issues


async def generate_summary_report():
    """Générer un rapport de résumé"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ GLOBAL DU SYSTÈME IAM")
    print("=" * 80)
    
    # Compter les éléments
    perms_count = await db.permissions.count_documents({})
    profiles_count = await db.profiles.count_documents({})
    bundles_count = await db.capability_bundles.count_documents({})
    users_count = await db.users.count_documents({})
    
    print(f"\n📈 STATISTIQUES:")
    print(f"   • Permissions: {perms_count}")
    print(f"   • Profils: {profiles_count}")
    print(f"   • Bundles: {bundles_count}")
    print(f"   • Utilisateurs: {users_count}")
    
    # Vérifier l'utilisation
    profiles = await db.profiles.find({}, {"_id": 0, "permission_ids": 1}).to_list(1000)
    bundles = await db.capability_bundles.find({}, {"_id": 0, "permission_ids": 1}).to_list(1000)
    
    used_in_profiles = set()
    for p in profiles:
        used_in_profiles.update(p.get('permission_ids', []))
    
    used_in_bundles = set()
    for b in bundles:
        used_in_bundles.update(b.get('permission_ids', []))
    
    total_used = len(used_in_profiles | used_in_bundles)
    
    print(f"\n🎯 UTILISATION:")
    print(f"   • Permissions utilisées: {total_used}/{perms_count} ({100*total_used/perms_count:.1f}%)")
    print(f"   • Dans profils: {len(used_in_profiles)}")
    print(f"   • Dans bundles: {len(used_in_bundles)}")
    
    client.close()


async def main():
    print("🚀 DÉMARRAGE DES TESTS D'INTÉGRITÉ IAM\n")
    
    all_issues = []
    
    # Exécuter tous les tests
    issues_perms = await test_permissions_integrity()
    issues_profiles = await test_profiles_integrity()
    issues_bundles = await test_bundles_integrity()
    issues_users = await test_users_integrity()
    
    all_issues.extend(issues_perms)
    all_issues.extend(issues_profiles)
    all_issues.extend(issues_bundles)
    all_issues.extend(issues_users)
    
    # Rapport de résumé
    await generate_summary_report()
    
    # Résultat final
    print("\n" + "=" * 80)
    if not all_issues:
        print("✅ TOUS LES TESTS SONT PASSÉS - SYSTÈME IAM INTÈGRE")
    else:
        print(f"⚠️  {len(all_issues)} PROBLÈME(S) DÉTECTÉ(S)")
        print("\nDÉTAILS:")
        for issue in all_issues[:10]:
            print(f"   {issue}")
        if len(all_issues) > 10:
            print(f"   ... et {len(all_issues) - 10} autres problèmes")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
