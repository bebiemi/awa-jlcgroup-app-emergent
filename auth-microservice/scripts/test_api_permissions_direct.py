#!/usr/bin/env python3
"""
Test direct de l'API permissions pour diagnostiquer l'erreur 500
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_permissions():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client.auth_db
        
        print("=" * 70)
        print(" 🧪 TEST DIRECT DES PERMISSIONS")
        print("=" * 70 + "\n")
        
        print("1️⃣ Récupération des permissions depuis MongoDB...\n")
        
        # Récupérer comme le fait l'API
        permissions_collection = db.permissions
        cursor = permissions_collection.find({}, {"_id": 0})
        
        permissions = []
        errors = []
        
        async for perm in cursor:
            # Vérifier les champs requis
            if 'code' not in perm:
                errors.append(f"❌ Permission sans 'code': {perm.get('name', perm.get('id', 'unknown'))}")
                continue
            
            if 'id' not in perm:
                errors.append(f"❌ Permission sans 'id': {perm.get('code')}")
                continue
            
            permissions.append(perm)
        
        print(f"✅ Permissions récupérées: {len(permissions)}")
        
        if errors:
            print(f"\n⚠️ Erreurs détectées: {len(errors)}\n")
            for error in errors[:10]:  # Afficher les 10 premières
                print(f"   {error}")
        
        # Vérifier quelques permissions
        print("\n2️⃣ Vérification de quelques permissions...\n")
        
        for i, perm in enumerate(permissions[:5], 1):
            print(f"   {i}. {perm.get('code'):40s}")
            print(f"      - id: {perm.get('id')}")
            print(f"      - name: {perm.get('name')}")
            print(f"      - resource: {perm.get('resource')}")
            print(f"      - action: {perm.get('action')}")
            
            # Vérifier tous les champs requis par Pydantic
            required_fields = ['id', 'code', 'name', 'resource', 'action']
            missing = [f for f in required_fields if f not in perm or perm[f] is None]
            
            if missing:
                print(f"      ⚠️ Champs manquants: {missing}")
            else:
                print(f"      ✅ Tous les champs requis présents")
            print()
        
        # Statistiques complètes
        print("=" * 70)
        print(" 📊 STATISTIQUES")
        print("=" * 70 + "\n")
        
        # Compter les permissions par catégorie
        categories = {}
        for perm in permissions:
            cat = perm.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("Permissions par catégorie:")
        for cat, count in sorted(categories.items()):
            print(f"   - {cat:20s}: {count:3d}")
        
        print(f"\n📦 TOTAL: {len(permissions)} permissions")
        
        if len(errors) == 0:
            print("\n✅ Toutes les permissions sont valides!")
            print("   L'erreur 500 doit venir d'ailleurs...")
        else:
            print(f"\n❌ {len(errors)} permission(s) invalide(s) trouvée(s)")
            print("   Ces permissions causent probablement l'erreur 500")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_permissions())
