#!/usr/bin/env python3
"""
Migrer les permissions vers le nouveau format avec scopes (.own, .all)
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Mapping des anciennes permissions vers les nouvelles
PERMISSION_MIGRATION_MAP = {
    # Missions
    "missions.view_own": "missions.read.own",
    "missions.view_all": "missions.read.all",
    "missions.edit_own": "missions.update.own",
    "missions.edit_all": "missions.update.all",
    "missions.delete_own": "missions.delete.own",
    "missions.delete_all": "missions.delete.all",
    "missions.create": "missions.create.own",  # Par défaut .own
    "missions.read": "missions.read.all",      # missions.read générique → .all pour admin
    
    # Besoins
    "besoins.view_own": "besoins.read.own",
    "besoins.view_all": "besoins.read.all",
    "besoins.edit_own": "besoins.update.own",
    "besoins.edit_all": "besoins.update.all",
    "besoins.delete_own": "besoins.delete.own",
    "besoins.delete_all": "besoins.delete.all",
    "besoins.create": "besoins.create.own",
    
    # Entreprises
    "entreprises.view_own": "entreprises.read.own",
    "entreprises.view_all": "entreprises.read.all",
    "entreprises.edit_own": "entreprises.update.own",
    "entreprises.edit_all": "entreprises.update.all",
}

async def main():
    print("=" * 80)
    print("🔄 MIGRATION DES PERMISSIONS VERS FORMAT SCOPED")
    print("=" * 80)
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # 1. Créer les nouvelles permissions
    print("\n1️⃣ Création des nouvelles permissions...")
    created_count = 0
    for old_code, new_code in PERMISSION_MIGRATION_MAP.items():
        # Vérifier si elle existe déjà
        existing = await db.permissions.find_one({"code": new_code})
        if existing:
            print(f"   ℹ️  {new_code} existe déjà")
            continue
        
        # Récupérer l'ancienne permission pour copier les métadonnées
        old_perm = await db.permissions.find_one({"code": old_code})
        
        if not old_perm:
            print(f"   ⚠️  Ancienne permission {old_code} non trouvée, création générique")
            # Extraire resource et action du code
            parts = new_code.split('.')
            resource = parts[0]
            action = parts[1]
            scope = parts[2] if len(parts) > 2 else "all"
            
            from uuid import uuid4
            new_perm = {
                "id": str(uuid4()),
                "code": new_code,
                "resource": resource,
                "action": action,
                "scope": scope,
                "description": f"Permission {new_code}",
                "category": "application",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        else:
            # Copier depuis l'ancienne
            from uuid import uuid4
            parts = new_code.split('.')
            scope = parts[2] if len(parts) > 2 else "all"
            
            new_perm = {
                "id": str(uuid4()),
                "code": new_code,
                "resource": old_perm.get("resource", parts[0]),
                "action": old_perm.get("action", parts[1]),
                "scope": scope,
                "description": old_perm.get("description", f"Permission {new_code}"),
                "category": old_perm.get("category", "application"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        
        await db.permissions.insert_one(new_perm)
        print(f"   ✅ Créé: {new_code}")
        created_count += 1
    
    print(f"\n   📊 {created_count} nouvelles permissions créées")
    
    # 2. Mettre à jour les profils
    print("\n2️⃣ Mise à jour des profils...")
    profiles = await db.profiles.find({}).to_list(1000)
    
    for profile in profiles:
        old_perm_ids = profile.get("permission_ids", [])
        if not old_perm_ids:
            continue
        
        # Récupérer les permissions
        perms = await db.permissions.find({"id": {"$in": old_perm_ids}}, {"_id": 0}).to_list(1000)
        
        new_perm_ids = set(old_perm_ids)  # Conserver les anciennes aussi
        
        for perm in perms:
            old_code = perm["code"]
            if old_code in PERMISSION_MIGRATION_MAP:
                new_code = PERMISSION_MIGRATION_MAP[old_code]
                new_perm = await db.permissions.find_one({"code": new_code})
                if new_perm:
                    new_perm_ids.add(new_perm["id"])
                    print(f"   🔄 {profile['name']}: {old_code} → {new_code}")
        
        # Mettre à jour le profil
        if len(new_perm_ids) > len(old_perm_ids):
            await db.profiles.update_one(
                {"id": profile["id"]},
                {"$set": {"permission_ids": list(new_perm_ids)}}
            )
            print(f"   ✅ Profil {profile['name']} mis à jour ({len(old_perm_ids)} → {len(new_perm_ids)} permissions)")
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION TERMINÉE")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
