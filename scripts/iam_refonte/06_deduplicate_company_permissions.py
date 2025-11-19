"""
Script 6: Déduplication Intelligente des Permissions du Profil Entreprise
Retire les permissions redondantes qui sont déjà couvertes par les bundles
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone


# Permissions à CONSERVER en direct (non couvertes par bundles)
KEEP_DIRECT_PERMISSIONS = [
    # Besoins - permissions spécifiques entreprise
    "besoins.validate",  # Validation JLC (pas dans bundle)
    "besoins.convert_to_mission",  # Conversion JLC (pas dans bundle)
    "besoins.view_all",  # Voir tous (pas dans bundle own)
    
    # Entreprises - permissions étendues
    "entreprises.delete",  # Supprimer (pas dans bundle)
    "entreprises.invite_user",  # Inviter (pas dans bundle)
    
    # Documents - permissions étendues
    "documents.view_all",  # Voir tous (pas dans bundle own)
    "documents.validate",  # Valider (pas dans bundle)
    
    # Missions
    "missions.view_own",
    "missions.edit_own", 
    "missions.delete_own",
    
    # Builtin - permissions admin/système
    "emargements.view.all",
    "entreprises.view.all",
    "entreprises.transfer.validate",
    "entreprises.archive",
    "entreprises.edit.all",
    "besoins.approve",
    "besoins.edit.all",
    "besoins.view.all",
    "applications.view.all",
    "applications.prescreen",
    
    # Dashboard, Messages, Notifications, Matching
    "dashboard.view_own",
    "dashboard.customize",
    "messages.read_own",
    "messages.send_own",
    "notifications.read_own",
    "notifications.manage_own",
    "matching.view_recommendations",
]


async def deduplicate_company_profile():
    """Déduplique les permissions du profil Entreprise"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🧹 DÉDUPLICATION DU PROFIL ENTREPRISE")
    print("=" * 80)
    
    # 1. Récupérer le profil
    profile = await db.profiles.find_one({"code": "profile.company"}, {"_id": 0})
    
    if not profile:
        print("❌ Profil 'profile.company' non trouvé")
        return
    
    print(f"\n📋 Profil: {profile.get('name')}")
    print(f"   Permissions directes actuelles: {len(profile.get('permission_ids', []))}")
    print(f"   Bundles: {len(profile.get('capability_bundle_ids', []))}")
    
    # 2. Récupérer toutes les permissions des bundles
    bundle_permission_codes = set()
    
    for bundle_id in profile.get('capability_bundle_ids', []):
        bundle = await db.capability_bundles.find_one({'id': bundle_id}, {'_id': 0})
        if bundle:
            print(f"   🧩 Bundle: {bundle.get('name')} ({len(bundle.get('permission_ids', []))} perms)")
            
            # Récupérer les codes des permissions de ce bundle
            for perm_id in bundle.get('permission_ids', []):
                perm = await db.permissions.find_one({'id': perm_id}, {'_id': 0, 'code': 1})
                if perm:
                    bundle_permission_codes.add(perm.get('code'))
    
    print(f"\n📊 Permissions via bundles: {len(bundle_permission_codes)}")
    
    # 3. Analyser les permissions directes
    permissions_to_keep = []
    permissions_to_remove = []
    
    for perm_id in profile.get('permission_ids', []):
        perm = await db.permissions.find_one({'id': perm_id}, {'_id': 0})
        if perm:
            code = perm.get('code')
            
            # Vérifier si la permission est dans la liste à conserver
            if code in KEEP_DIRECT_PERMISSIONS:
                permissions_to_keep.append(perm_id)
            # Vérifier si elle est déjà dans un bundle
            elif code in bundle_permission_codes:
                permissions_to_remove.append({
                    'id': perm_id,
                    'code': code,
                    'reason': 'Déjà dans un bundle'
                })
            # Permissions redondantes (ex: profile.view_own vs profile.edit_own)
            elif code in ['profile.view_own', 'users.view_own', 'documents.read_own']:
                # Ces permissions sont déjà couvertes par des permissions plus larges
                permissions_to_remove.append({
                    'id': perm_id,
                    'code': code,
                    'reason': 'Redondante avec permission plus large'
                })
            else:
                # Garder par défaut si pas sûr
                permissions_to_keep.append(perm_id)
                print(f"   ℹ️  Conservée (non catégorisée): {code}")
    
    print(f"\n📊 ANALYSE:")
    print(f"   À conserver: {len(permissions_to_keep)}")
    print(f"   À retirer: {len(permissions_to_remove)}")
    
    if permissions_to_remove:
        print(f"\n🗑️  Permissions à retirer:")
        for perm in permissions_to_remove[:15]:
            print(f"      - {perm['code']}")
            print(f"        Raison: {perm['reason']}")
        if len(permissions_to_remove) > 15:
            print(f"      ... et {len(permissions_to_remove) - 15} autres")
    
    # 4. Demander confirmation
    if len(permissions_to_remove) == 0:
        print("\n✅ Aucune permission à retirer")
        client.close()
        return
    
    print(f"\n⚠️  Cette opération va retirer {len(permissions_to_remove)} permissions redondantes")
    print(f"   Les permissions restantes: {len(permissions_to_keep)}")
    
    # 5. Appliquer les changements
    await db.profiles.update_one(
        {"code": "profile.company"},
        {
            "$set": {
                "permission_ids": permissions_to_keep,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    print(f"\n✅ Profil mis à jour:")
    print(f"   Avant: {len(profile.get('permission_ids', []))} permissions directes")
    print(f"   Après: {len(permissions_to_keep)} permissions directes")
    print(f"   Retirées: {len(permissions_to_remove)} permissions redondantes")
    
    # 6. Calculer le total effectif
    bundle_perms = set()
    for bundle_id in profile.get('capability_bundle_ids', []):
        bundle = await db.capability_bundles.find_one({'id': bundle_id}, {'_id': 0, 'permission_ids': 1})
        if bundle:
            bundle_perms.update(bundle.get('permission_ids', []))
    
    total_effective = len(set(permissions_to_keep) | bundle_perms)
    
    print(f"\n📊 NOUVEAU TOTAL EFFECTIF:")
    print(f"   Permissions directes: {len(permissions_to_keep)}")
    print(f"   Permissions via bundles: {len(bundle_perms)}")
    print(f"   Total unique: {total_effective}")
    print(f"   Réduction: {len(profile.get('permission_ids', [])) - len(permissions_to_keep)} permissions")
    
    client.close()


async def main():
    print("🚀 Démarrage de la déduplication\n")
    await deduplicate_company_profile()
    
    print("\n" + "=" * 80)
    print("✅ DÉDUPLICATION TERMINÉE")
    print("=" * 80)
    print("\n💡 ACTIONS SUIVANTES:")
    print("   1. Vérifier le profil Entreprise dans l'UI")
    print("   2. Tester que toutes les fonctionnalités marchent")
    print("   3. Le profil devrait maintenant avoir ~35-40 permissions au lieu de 79")


if __name__ == '__main__':
    asyncio.run(main())
