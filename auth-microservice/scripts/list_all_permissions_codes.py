#!/usr/bin/env python3
"""
Liste toutes les permissions avec leurs codes pour comparaison
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def list_permissions():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        print("=" * 70)
        print(" 📋 TOUTES LES PERMISSIONS DANS LA BASE DE DONNÉES")
        print("=" * 70 + "\n")
        
        # Permissions Legacy
        print("🔹 PERMISSIONS (LEGACY) - Collection 'permissions'")
        print("-" * 70)
        
        legacy_perms = await db.permissions.find({}, {"_id": 0, "code": 1, "name": 1}).sort("code", 1).to_list(None)
        
        if legacy_perms:
            for i, perm in enumerate(legacy_perms, 1):
                code = perm.get('code', 'N/A')
                name = perm.get('name', 'N/A')
                print(f"{i:3d}. {code:40s} | {name}")
            print(f"\nTotal: {len(legacy_perms)} permissions\n")
        else:
            print("  Aucune permission trouvée\n")
        
        # Permissions IAM
        print("🔹 PERMISSIONS IAM - Collection 'iam_permissions'")
        print("-" * 70)
        
        iam_perms = await db.iam_permissions.find({}, {"_id": 0, "code": 1, "name": 1}).sort("code", 1).to_list(None)
        
        if iam_perms:
            for i, perm in enumerate(iam_perms, 1):
                code = perm.get('code', 'N/A')
                name = perm.get('name', 'N/A')
                print(f"{i:3d}. {code:40s} | {name}")
            print(f"\nTotal: {len(iam_perms)} permissions\n")
        else:
            print("  Aucune permission trouvée\n")
        
        # Total combiné
        total = len(legacy_perms) + len(iam_perms)
        print("=" * 70)
        print(f" 📊 TOTAL: {total} permissions (Legacy: {len(legacy_perms)}, IAM: {len(iam_perms)})")
        print("=" * 70)
        
        if total < 102:
            print(f"\n⚠️  Il manque ~{102 - total} permissions par rapport à Emergent!")
            print("    Ces permissions doivent être ajoutées.")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(list_permissions())
