#!/usr/bin/env python3
"""
Script de réparation complète des données IAM
Corrige les incohérences critiques identifiées
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def fix_iam_data():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("="*80)
    print("RÉPARATION DONNÉES IAM")
    print("="*80)
    
    # 1. Ajouter besoins.create.own au profil Entreprise
    print("\n🔧 1. AJOUT PERMISSIONS MANQUANTES AU PROFIL ENTREPRISE")
    print("-"*80)
    
    profil_entreprise = await db.profiles.find_one({"code": "profile.company"})
    if profil_entreprise:
        # Récupérer les permissions besoins
        besoins_perms = await db.permissions.find(
            {"code": {"$regex": "^besoins\\.(create|read|update)\\.(own|all)", "$options": "i"}},
            {"_id": 0, "id": 1, "code": 1}
        ).to_list(20)
        
        print(f"   Permissions besoins trouvées: {len(besoins_perms)}")
        for perm in besoins_perms:
            print(f"   - {perm['code']} ({perm['id']})")
        
        # Ajouter les permissions manquantes
        new_perm_ids = [p['id'] for p in besoins_perms]
        result = await db.profiles.update_one(
            {"id": profil_entreprise['id']},
            {"$addToSet": {"permission_ids": {"$each": new_perm_ids}}}
        )
        
        print(f"   ✅ {len(new_perm_ids)} permissions ajoutées au profil Entreprise")
    
    # 2. Assigner profil Entreprise au groupe Equipe Entreprise
    print("\n🔧 2. ASSIGNATION PROFIL AU GROUPE")
    print("-"*80)
    
    groupe_entreprise = await db.groups.find_one({"name": {"$regex": "Entreprise", "$options": "i"}})
    if groupe_entreprise and profil_entreprise:
        result = await db.groups.update_one(
            {"id": groupe_entreprise['id']},
            {"$addToSet": {"profile_ids": profil_entreprise['id']}}
        )
        print(f"   ✅ Profil Entreprise assigné au groupe")
    
    # 3. Synchroniser bidirectionnellement groupe <-> utilisateurs
    print("\n🔧 3. SYNCHRONISATION BIDIRECTIONNELLE GROUPE-UTILISATEURS")
    print("-"*80)
    
    if groupe_entreprise:
        user_ids_in_group = groupe_entreprise.get('user_ids', [])
        print(f"   Groupe contient {len(user_ids_in_group)} user_ids")
        
        # Ajouter le groupe à chaque utilisateur
        for user_id in user_ids_in_group:
            result = await db.users.update_one(
                {"id": user_id},
                {"$addToSet": {"group_ids": groupe_entreprise['id']}}
            )
            user = await db.users.find_one({"id": user_id}, {"username": 1})
            if user:
                print(f"   ✅ Groupe ajouté à {user.get('username')}")
        
        # Vérifier tous les utilisateurs qui ont le groupe dans group_ids
        users_with_group = await db.users.find(
            {"group_ids": groupe_entreprise['id']},
            {"_id": 0, "id": 1, "username": 1}
        ).to_list(100)
        
        user_ids_with_group = [u['id'] for u in users_with_group]
        
        # Mettre à jour user_ids du groupe pour être cohérent
        result = await db.groups.update_one(
            {"id": groupe_entreprise['id']},
            {"$set": {"user_ids": user_ids_with_group}}
        )
        
        print(f"   ✅ Synchronisation complète: {len(user_ids_with_group)} utilisateurs")
    
    # 4. Vérification finale
    print("\n📊 4. VÉRIFICATION FINALE")
    print("-"*80)
    
    # Vérifier Admin TechCorp
    techcorp = await db.users.find_one({"username": "techcorp_admin"}, {"_id": 0})
    if techcorp:
        print(f"   Admin TechCorp:")
        print(f"   - Group IDs: {techcorp.get('group_ids', [])}")
        print(f"   - Profile IDs: {techcorp.get('profile_ids', [])}")
        
        # Vérifier les permissions du profil
        if techcorp.get('profile_ids'):
            profile = await db.profiles.find_one(
                {"id": techcorp['profile_ids'][0]},
                {"_id": 0, "name": 1, "permission_ids": 1, "capability_bundle_ids": 1}
            )
            if profile:
                print(f"   - Profil: {profile.get('name')}")
                print(f"   - Permissions directes: {len(profile.get('permission_ids', []))}")
                print(f"   - Bundles: {len(profile.get('capability_bundle_ids', []))}")
                
                # Vérifier si besoins.create est présent
                all_perms = set(profile.get('permission_ids', []))
                
                # Ajouter permissions des bundles
                for bundle_id in profile.get('capability_bundle_ids', []):
                    bundle = await db.bundles.find_one({"id": bundle_id})
                    if bundle:
                        all_perms.update(bundle.get('permission_ids', []))
                
                # Chercher besoins.create
                besoins_create = await db.permissions.find_one(
                    {"code": {"$regex": "^besoins\\.create", "$options": "i"}},
                    {"_id": 0, "id": 1, "code": 1}
                )
                
                if besoins_create:
                    has_perm = besoins_create['id'] in all_perms
                    status = "✅" if has_perm else "❌"
                    print(f"   {status} Permission {besoins_create['code']}: {has_perm}")
    
    # Vérifier le groupe
    groupe = await db.groups.find_one(
        {"name": {"$regex": "Entreprise", "$options": "i"}},
        {"_id": 0, "name": 1, "user_ids": 1, "profile_ids": 1}
    )
    if groupe:
        print(f"\n   Groupe {groupe.get('name')}:")
        print(f"   - User IDs: {len(groupe.get('user_ids', []))}")
        print(f"   - Profile IDs: {len(groupe.get('profile_ids', []))}")
    
    print("\n" + "="*80)
    print("✅ RÉPARATION TERMINÉE")
    print("="*80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_iam_data())
