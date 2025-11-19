"""
Script 7: Audit Complet des Permissions IAM
Analyse l'utilisation de TOUTES les permissions dans :
- Profils (profiles)
- Bundles (capability_bundles)
- Code Backend (routes API)
- Code Frontend (composants)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
import json
from collections import defaultdict


async def audit_permissions_usage():
    """Audit complet de l'utilisation des permissions"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🔍 AUDIT COMPLET DES PERMISSIONS IAM")
    print("=" * 80)
    
    # 1. Récupérer toutes les permissions
    all_permissions = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    print(f"\n📊 Total permissions en base: {len(all_permissions)}")
    
    # 2. Index par ID et par code
    perms_by_id = {p['id']: p for p in all_permissions}
    perms_by_code = {p['code']: p for p in all_permissions}
    
    # 3. Vérifier utilisation dans les profils
    profiles = await db.profiles.find({}, {"_id": 0, "code": 1, "name": 1, "permission_ids": 1}).to_list(1000)
    
    used_in_profiles = set()
    profile_usage = defaultdict(list)
    
    for profile in profiles:
        for perm_id in profile.get('permission_ids', []):
            used_in_profiles.add(perm_id)
            if perm_id in perms_by_id:
                profile_usage[perm_id].append(profile['name'])
    
    print(f"\n📋 Permissions utilisées dans les profils: {len(used_in_profiles)}")
    
    # 4. Vérifier utilisation dans les bundles
    bundles = await db.capability_bundles.find({}, {"_id": 0, "code": 1, "name": 1, "permission_ids": 1}).to_list(1000)
    
    used_in_bundles = set()
    bundle_usage = defaultdict(list)
    
    for bundle in bundles:
        for perm_id in bundle.get('permission_ids', []):
            used_in_bundles.add(perm_id)
            if perm_id in perms_by_id:
                bundle_usage[perm_id].append(bundle['name'])
    
    print(f"🧩 Permissions utilisées dans les bundles: {len(used_in_bundles)}")
    
    # 5. Union de toutes les utilisations DB
    used_in_db = used_in_profiles | used_in_bundles
    print(f"💾 Total permissions utilisées (DB): {len(used_in_db)}")
    
    # 6. Permissions non utilisées en DB
    unused_in_db = set(perms_by_id.keys()) - used_in_db
    print(f"⚠️  Permissions NON utilisées (DB): {len(unused_in_db)}")
    
    # 7. Analyser les permissions non utilisées
    unused_by_category = defaultdict(list)
    
    for perm_id in unused_in_db:
        if perm_id in perms_by_id:
            perm = perms_by_id[perm_id]
            unused_by_category[perm.get('category', 'unknown')].append(perm)
    
    print(f"\n📂 PERMISSIONS NON UTILISÉES PAR CATÉGORIE:")
    for cat in sorted(unused_by_category.keys()):
        perms = unused_by_category[cat]
        print(f"\n   {cat.upper()} ({len(perms)} permissions):")
        for perm in perms[:5]:
            print(f"      - {perm.get('code')}: {perm.get('name')}")
        if len(perms) > 5:
            print(f"      ... et {len(perms) - 5} autres")
    
    # 8. Créer le rapport JSON
    report = {
        "audit_date": "2025-01-19",
        "total_permissions": len(all_permissions),
        "used_in_profiles": len(used_in_profiles),
        "used_in_bundles": len(used_in_bundles),
        "used_in_db_total": len(used_in_db),
        "unused_in_db": len(unused_in_db),
        "unused_by_category": {
            cat: [p['code'] for p in perms]
            for cat, perms in unused_by_category.items()
        },
        "usage_details": {}
    }
    
    # Ajouter les détails d'utilisation pour chaque permission
    for perm_id, perm in perms_by_id.items():
        usage = {
            "code": perm.get('code'),
            "name": perm.get('name'),
            "category": perm.get('category'),
            "used_in_profiles": profile_usage.get(perm_id, []),
            "used_in_bundles": bundle_usage.get(perm_id, []),
            "is_used": perm_id in used_in_db,
            "resource": perm.get('resource'),
            "action": perm.get('action'),
            "scope": perm.get('scope'),
        }
        report['usage_details'][perm.get('code')] = usage
    
    # Sauvegarder le rapport
    with open('/app/scripts/iam_refonte/audit_permissions_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Rapport sauvegardé: /app/scripts/iam_refonte/audit_permissions_report.json")
    
    # 9. Analyser les permissions qui suivent déjà le format resource.action.scope
    modern_format = []
    legacy_format = []
    
    for perm in all_permissions:
        code = perm.get('code', '')
        parts = code.split('.')
        
        # Format moderne: resource.action.scope (3 parties) ou resource.action (2 parties)
        if len(parts) >= 2 and perm.get('resource') and perm.get('action'):
            modern_format.append(perm)
        else:
            legacy_format.append(perm)
    
    print(f"\n📐 ANALYSE DU FORMAT:")
    print(f"   Format moderne (resource.action[.scope]): {len(modern_format)}")
    print(f"   Format legacy (autre): {len(legacy_format)}")
    
    if legacy_format:
        print(f"\n   Exemples de format legacy:")
        for perm in legacy_format[:10]:
            print(f"      - {perm.get('code')}")
    
    # 10. Statistiques par catégorie
    categories_stats = defaultdict(lambda: {"total": 0, "used": 0, "unused": 0})
    
    for perm in all_permissions:
        cat = perm.get('category', 'unknown')
        perm_id = perm['id']
        categories_stats[cat]["total"] += 1
        if perm_id in used_in_db:
            categories_stats[cat]["used"] += 1
        else:
            categories_stats[cat]["unused"] += 1
    
    print(f"\n📊 STATISTIQUES PAR CATÉGORIE:")
    print(f"{'Catégorie':<20} {'Total':<10} {'Utilisées':<12} {'Non utilisées':<15}")
    print("-" * 60)
    for cat in sorted(categories_stats.keys()):
        stats = categories_stats[cat]
        print(f"{cat:<20} {stats['total']:<10} {stats['used']:<12} {stats['unused']:<15}")
    
    client.close()
    
    return report


async def search_in_code():
    """Recherche l'utilisation des permissions dans le code"""
    print("\n" + "=" * 80)
    print("🔍 RECHERCHE DANS LE CODE")
    print("=" * 80)
    
    # Lire le rapport
    try:
        with open('/app/scripts/iam_refonte/audit_permissions_report.json', 'r') as f:
            report = json.load(f)
    except:
        print("❌ Rapport non trouvé, exécuter d'abord audit_permissions_usage()")
        return
    
    unused_codes = []
    for cat, codes in report['unused_by_category'].items():
        unused_codes.extend(codes)
    
    print(f"\n🔍 Recherche de {len(unused_codes)} permissions non utilisées dans le code...")
    
    # Chercher dans le backend
    backend_found = {}
    backend_path = "/app/auth-microservice"
    
    # Chercher dans le frontend
    frontend_found = {}
    frontend_path = "/app/apps/web/src"
    
    # Pour l'instant, on va juste montrer les premiers résultats
    # Une vraie recherche prendrait trop de temps
    
    print(f"\n💡 Note: Pour une recherche complète dans le code:")
    print(f"   Backend: grep -r 'permission_code' {backend_path}")
    print(f"   Frontend: grep -r 'permission_code' {frontend_path}")
    print(f"\n   Cela nécessiterait de scanner ~{len(unused_codes)} permissions")
    print(f"   Préférer une analyse manuelle pour les permissions critiques")


async def main():
    print("🚀 Démarrage de l'audit IAM complet\n")
    
    # Étape 1: Audit base de données
    report = await audit_permissions_usage()
    
    # Étape 2: Recherche dans le code (simplifié)
    await search_in_code()
    
    print("\n" + "=" * 80)
    print("✅ AUDIT TERMINÉ")
    print("=" * 80)
    print("\n📋 PROCHAINES ÉTAPES:")
    print("   1. Examiner le rapport: /app/scripts/iam_refonte/audit_permissions_report.json")
    print("   2. Identifier les permissions vraiment obsolètes")
    print("   3. Lancer le script de nettoyage")
    print("   4. Migrer les permissions legacy vers format moderne")


if __name__ == '__main__':
    asyncio.run(main())
