#!/usr/bin/env python3
"""
Corriger les permissions du profil Entreprise
Remplacer .all par .own pour les permissions où c'est nécessaire
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def main():
    print("=" * 80)
    print("🔧 CORRECTION DU PROFIL ENTREPRISE")
    print("=" * 80)
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # Permissions à corriger : remplacer .all par .own
    corrections = {
        "missions.read.all": "missions.read.own",
        "missions.update.all": "missions.update.own",
        "missions.delete.all": "missions.delete.own",
        "besoins.read.all": "besoins.read.own",
        "besoins.update.all": "besoins.update.own",
        "besoins.delete.all": "besoins.delete.own",
        "entreprises.read.all": "entreprises.read.own",
        "entreprises.update.all": "entreprises.update.own",
    }
    
    # Permissions génériques à supprimer (sans scope)
    to_remove = [
        "missions.read",
        "missions.create",
        "besoins.read",
        "besoins.create",
    ]
    
    # 1. Traiter le profil Entreprise
    print("\n1️⃣ Correction du profil 'Entreprise'...")
    profile = await db.profiles.find_one({"code": "profile.company"})
    
    if not profile:
        print("   ⚠️  Profil Entreprise non trouvé")
    else:
        await fix_profile(db, profile, corrections, to_remove)
    
    # 2. Traiter le profil Admin Société (au cas où)
    print("\n2️⃣ Vérification du profil 'Admin Société'...")
    profile_admin = await db.profiles.find_one({"code": "company_admin"})
    
    if profile_admin:
        await fix_profile(db, profile_admin, corrections, to_remove)
    
    # 3. Invalider le cache
    print("\n3️⃣ Invalidation du cache...")
    from awana_auth.services.iam_cache_service import get_cache_service
    cache = await get_cache_service()
    
    # Trouver tous les utilisateurs avec ces profils
    profile_ids = []
    if profile:
        profile_ids.append(profile["id"])
    if profile_admin:
        profile_ids.append(profile_admin["id"])
    
    if profile_ids:
        users = await db.users.find({"profile_ids": {"$in": profile_ids}}).to_list(1000)
        for user in users:
            await cache.invalidate_user_permissions(user["id"])
            print(f"   🗑️  Cache invalidé: {user.get('username')}")
    
    print("\n" + "=" * 80)
    print("✅ CORRECTION TERMINÉE")
    print("=" * 80)
    
    client.close()


async def fix_profile(db, profile, corrections, to_remove):
    """Corriger un profil donné"""
    print(f"   Profil: {profile['name']}")
    
    current_perm_ids = set(profile.get("permission_ids", []))
    perms = await db.permissions.find({"id": {"$in": list(current_perm_ids)}}).to_list(1000)
    
    new_perm_ids = set()
    changes_made = False
    
    for perm in perms:
        code = perm["code"]
        
        # Supprimer les permissions génériques
        if code in to_remove:
            print(f"   ❌ Supprimé: {code}")
            changes_made = True
            continue
        
        # Corriger .all → .own
        if code in corrections:
            new_code = corrections[code]
            new_perm = await db.permissions.find_one({"code": new_code})
            if new_perm:
                new_perm_ids.add(new_perm["id"])
                print(f"   🔄 Corrigé: {code} → {new_code}")
                changes_made = True
            else:
                # Si la permission .own n'existe pas, garder l'ancienne
                new_perm_ids.add(perm["id"])
                print(f"   ⚠️  {code} (permission .own non trouvée, conservée)")
        else:
            # Garder les autres permissions
            new_perm_ids.add(perm["id"])
    
    if changes_made:
        # Mettre à jour le profil
        await db.profiles.update_one(
            {"id": profile["id"]},
            {
                "$set": {
                    "permission_ids": list(new_perm_ids),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        print(f"   ✅ Profil mis à jour: {len(current_perm_ids)} → {len(new_perm_ids)} permissions")
    else:
        print(f"   ℹ️  Aucune correction nécessaire")


if __name__ == "__main__":
    asyncio.run(main())
