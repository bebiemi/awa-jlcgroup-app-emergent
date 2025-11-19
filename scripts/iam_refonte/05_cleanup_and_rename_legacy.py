"""
Script 5: Nettoyage et Renommage Legacy → BuiltIn
1. Renommer catégorie "legacy" → "builtin" 
2. Nettoyer les permissions obsolètes du profil Entreprise
3. Identifier les permissions vraiment utilisées vs obsolètes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

# Permissions legacy qui sont VRAIMENT des built-in (à conserver)
BUILTIN_PERMISSIONS = [
    "users.read",
    "users.write", 
    "users.delete",
    "roles.read",
    "roles.write",
    "roles.delete",
    "content.read",
    "content.write",
    "content.delete",
    "analytics.read",
    "audit.read",
]

# Permissions legacy OBSOLÈTES (à retirer du profil Entreprise)
OBSOLETE_FOR_COMPANY = [
    "*.*",  # Wildcard admin
    "gestion_utilisateurs",
    "gestion_groupes", 
    "gestion_profils",
    "voir_utilisateurs",
    "gestion_interim",
    "voir_interimaires",
    # Permissions admin qui n'ont rien à faire dans le profil Entreprise
]


async def rename_legacy_to_builtin():
    """Renomme toutes les permissions 'legacy' en 'builtin'"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🔄 RENOMMAGE LEGACY → BUILTIN")
    print("=" * 80)
    
    # 1. Compter les permissions legacy
    legacy_count = await db.permissions.count_documents({"category": "legacy"})
    print(f"\n📊 Permissions 'legacy' trouvées: {legacy_count}")
    
    if legacy_count == 0:
        print("✅ Aucune permission 'legacy' à renommer")
        return
    
    # 2. Renommer
    result = await db.permissions.update_many(
        {"category": "legacy"},
        {
            "$set": {
                "category": "builtin",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    print(f"✅ {result.modified_count} permissions renommées en 'builtin'")
    
    # 3. Vérifier
    builtin_count = await db.permissions.count_documents({"category": "builtin"})
    print(f"✅ Total permissions 'builtin': {builtin_count}")
    
    client.close()


async def cleanup_company_profile():
    """Nettoie les permissions obsolètes du profil Entreprise"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🧹 NETTOYAGE DU PROFIL ENTREPRISE")
    print("=" * 80)
    
    # 1. Récupérer le profil Entreprise
    profile = await db.profiles.find_one({"code": "profile.company"}, {"_id": 0})
    
    if not profile:
        print("❌ Profil 'profile.company' non trouvé")
        return
    
    print(f"\n📋 Profil: {profile.get('name')}")
    print(f"   Permissions directes actuelles: {len(profile.get('permission_ids', []))}")
    
    # 2. Identifier les permissions obsolètes
    obsolete_perm_ids = []
    
    for perm_id in profile.get('permission_ids', []):
        perm = await db.permissions.find_one({'id': perm_id}, {'_id': 0, 'code': 1, 'name': 1, 'category': 1})
        if perm:
            code = perm.get('code', '')
            
            # Vérifier si c'est une permission obsolète
            if any(obs in code for obs in OBSOLETE_FOR_COMPANY):
                obsolete_perm_ids.append(perm_id)
                print(f"   ⚠️  Obsolète: {code}")
    
    print(f"\n📊 Permissions obsolètes identifiées: {len(obsolete_perm_ids)}")
    
    if len(obsolete_perm_ids) == 0:
        print("✅ Aucune permission obsolète à retirer")
        client.close()
        return
    
    # 3. Demander confirmation (simulation)
    print(f"\n⚠️  Action: Retirer {len(obsolete_perm_ids)} permissions obsolètes du profil Entreprise")
    print("   Ces permissions sont principalement des permissions admin/système")
    print("   Le profil Entreprise devrait se concentrer sur : besoins, émargements, documents")
    
    # 4. Nettoyer
    new_permission_ids = [p for p in profile.get('permission_ids', []) if p not in obsolete_perm_ids]
    
    await db.profiles.update_one(
        {"code": "profile.company"},
        {
            "$set": {
                "permission_ids": new_permission_ids,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    print(f"✅ Profil nettoyé:")
    print(f"   Avant: {len(profile.get('permission_ids', []))} permissions")
    print(f"   Après: {len(new_permission_ids)} permissions")
    print(f"   Retirées: {len(obsolete_perm_ids)} permissions obsolètes")
    
    # 5. Afficher le nouveau total avec bundles
    bundle_perms = set()
    for bundle_id in profile.get('capability_bundle_ids', []):
        bundle = await db.capability_bundles.find_one({'id': bundle_id}, {'_id': 0, 'permission_ids': 1})
        if bundle:
            bundle_perms.update(bundle.get('permission_ids', []))
    
    total_effective = len(set(new_permission_ids) | bundle_perms)
    print(f"\n📊 NOUVEAU TOTAL EFFECTIF:")
    print(f"   Directes: {len(new_permission_ids)}")
    print(f"   Via bundles: {len(bundle_perms)}")
    print(f"   Total unique: {total_effective}")
    
    client.close()


async def analyze_builtin_usage():
    """Analyse l'utilisation des permissions builtin"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("📊 ANALYSE DES PERMISSIONS BUILTIN")
    print("=" * 80)
    
    builtin_perms = await db.permissions.find(
        {"category": "builtin"},
        {"_id": 0, "id": 1, "code": 1}
    ).to_list(1000)
    
    print(f"\nTotal permissions builtin: {len(builtin_perms)}")
    
    # Compter l'utilisation
    used_count = 0
    unused_builtin = []
    
    for perm in builtin_perms:
        # Chercher dans les profils
        profile_usage = await db.profiles.count_documents({
            "$or": [
                {"permission_ids": perm['id']},
            ]
        })
        
        # Chercher dans les bundles
        bundle_usage = await db.capability_bundles.count_documents({
            "permission_ids": perm['id']
        })
        
        if profile_usage > 0 or bundle_usage > 0:
            used_count += 1
        else:
            unused_builtin.append(perm['code'])
    
    print(f"   Utilisées: {used_count}")
    print(f"   Non utilisées: {len(unused_builtin)}")
    
    if unused_builtin[:10]:
        print(f"\n⚠️  Exemples de builtin non utilisées (10 premiers):")
        for code in unused_builtin[:10]:
            print(f"      - {code}")
    
    client.close()


async def main():
    """Exécute toutes les tâches de nettoyage"""
    print("🚀 Démarrage du nettoyage et renommage IAM\n")
    
    # Étape 1: Renommer legacy → builtin
    await rename_legacy_to_builtin()
    
    # Étape 2: Nettoyer le profil Entreprise
    await cleanup_company_profile()
    
    # Étape 3: Analyser l'utilisation des builtin
    await analyze_builtin_usage()
    
    print("\n" + "=" * 80)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 80)
    print("\n📋 ACTIONS EFFECTUÉES:")
    print("   1. ✅ Catégorie 'legacy' renommée en 'builtin'")
    print("   2. ✅ Profil Entreprise nettoyé (permissions obsolètes retirées)")
    print("   3. ✅ Analyse des permissions builtin utilisées")
    print("\n💡 PROCHAINES ÉTAPES:")
    print("   - Vérifier le profil Entreprise dans l'UI")
    print("   - Vérifier que les permissions sont toujours fonctionnelles")
    print("   - Considérer supprimer les builtin non utilisées (optionnel)")


if __name__ == '__main__':
    asyncio.run(main())
