#!/usr/bin/env python3
"""
Fix permissions : ajouter le champ 'code' manquant
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_permissions():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        print(f"🔌 Connexion à MongoDB: {mongo_url}\n")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        print("=" * 70)
        print(" 🔧 CORRECTION DES PERMISSIONS - Ajout du champ 'code'")
        print("=" * 70 + "\n")
        
        # Collection permissions (legacy)
        print("📋 Collection 'permissions' (legacy):\n")
        
        permissions = await db.permissions.find({}).to_list(None)
        
        updated_count = 0
        skipped_count = 0
        
        for perm in permissions:
            perm_id = perm.get('id')
            
            # Si le champ 'code' existe déjà, skip
            if 'code' in perm and perm['code']:
                print(f"  ⏭  {perm.get('name', perm_id)}: code déjà présent")
                skipped_count += 1
                continue
            
            # Utiliser 'name' comme 'code' si disponible
            code = perm.get('name', perm.get('id', 'unknown'))
            
            # Mettre à jour
            await db.permissions.update_one(
                {"id": perm_id},
                {"$set": {"code": code}}
            )
            
            print(f"  ✅ {perm.get('name', perm_id)}: code = '{code}'")
            updated_count += 1
        
        print(f"\n✅ Permissions (legacy): {updated_count} mises à jour, {skipped_count} déjà OK")
        
        # Collection iam_permissions
        print("\n" + "=" * 70)
        print("🔐 Collection 'iam_permissions':\n")
        
        iam_permissions = await db.iam_permissions.find({}).to_list(None)
        
        iam_updated_count = 0
        iam_skipped_count = 0
        
        for perm in iam_permissions:
            perm_id = perm.get('id')
            
            # Si le champ 'code' existe déjà, skip
            if 'code' in perm and perm['code']:
                iam_skipped_count += 1
                continue
            
            # Utiliser 'name' comme 'code' si disponible
            code = perm.get('name', perm.get('id', 'unknown'))
            
            # Mettre à jour
            await db.iam_permissions.update_one(
                {"id": perm_id},
                {"$set": {"code": code}}
            )
            
            print(f"  ✅ {perm.get('name', perm_id)}: code = '{code}'")
            iam_updated_count += 1
        
        if iam_updated_count == 0 and iam_skipped_count == 0:
            print("  ℹ️  Aucune permission IAM à mettre à jour")
        else:
            print(f"\n✅ Permissions IAM: {iam_updated_count} mises à jour, {iam_skipped_count} déjà OK")
        
        # Résumé
        print("\n" + "=" * 70)
        print(" ✅ CORRECTION TERMINÉE")
        print("=" * 70)
        print(f"\n📊 Total:")
        print(f"   - Permissions (legacy): {updated_count} corrigées")
        print(f"   - Permissions IAM: {iam_updated_count} corrigées")
        print(f"\n💡 Vous pouvez maintenant recharger l'interface IAM")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_permissions())
