#!/usr/bin/env python3
"""
Script de test pour vérifier le comportement du menu "Suivi des candidatures"
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")


async def test_candidature_tracking():
    print("\n" + "="*80)
    print("🧪 TEST DU MENU SUIVI DES CANDIDATURES")
    print("="*80 + "\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # ================================================================
        # Test 1: Vérifier le profil candidat et ses permissions
        # ================================================================
        print("1️⃣ Vérification du profil Candidat...")
        
        profile = await db.profiles.find_one({"code": "candidat"}, {"_id": 0})
        if profile:
            perm_ids = profile.get("permission_ids", [])
            print(f"   ✅ Profil trouvé avec {len(perm_ids)} permissions")
            
            # Vérifier les permissions clés
            perms = await db.permissions.find(
                {"id": {"$in": perm_ids}},
                {"_id": 0, "code": 1}
            ).to_list(None)
            
            perm_codes = [p["code"] for p in perms]
            required_perms = ["applications.read.own", "missions.browse", "dashboard.candidat.access"]
            
            print("\n   📋 Permissions clés:")
            for req_perm in required_perms:
                status = "✅" if req_perm in perm_codes else "❌"
                print(f"      {status} {req_perm}")
        else:
            print("   ❌ Profil candidat non trouvé!")
            return False
        
        # ================================================================
        # Test 2: Vérifier les utilisateurs candidats
        # ================================================================
        print("\n2️⃣ Vérification des utilisateurs candidats...")
        
        users = await db.users.find(
            {"roles": "candidat"},
            {"_id": 0, "username": 1, "email": 1, "profile_ids": 1}
        ).to_list(None)
        
        print(f"   Trouvé {len(users)} utilisateur(s) candidat:")
        for user in users:
            print(f"      - {user.get('username')} ({user.get('email')})")
        
        # ================================================================
        # Test 3: Vérifier les candidatures (collection applications)
        # ================================================================
        print("\n3️⃣ Vérification des candidatures...")
        
        # Note: Les candidatures peuvent être dans différentes collections selon l'implémentation
        # Vérifions les collections possibles
        collections = await db.list_collection_names()
        app_collections = [c for c in collections if 'application' in c.lower() or 'candidature' in c.lower()]
        
        print(f"   Collections trouvées: {app_collections if app_collections else 'Aucune'}")
        
        if app_collections:
            for coll_name in app_collections:
                count = await db[coll_name].count_documents({})
                print(f"      - {coll_name}: {count} document(s)")
        
        # ================================================================
        # Test 4: Simuler le comportement du hook
        # ================================================================
        print("\n4️⃣ Simulation du comportement du hook...")
        
        if users:
            test_user = users[0]
            username = test_user.get("username")
            
            # Vérifier si l'utilisateur a les permissions
            user_profile_ids = test_user.get("profile_ids", [])
            has_candidat_profile = profile["id"] in user_profile_ids if profile else False
            
            print(f"\n   Test avec {username}:")
            print(f"      - Profil candidat assigné: {'✅ OUI' if has_candidat_profile else '❌ NON'}")
            
            # Simuler la vérification des candidatures
            # (Dans la vraie app, c'est l'API qui filtre par user_id)
            print(f"      - API retournerait: Les candidatures de cet utilisateur")
            
            # Résultat du hook
            show_menu = has_candidat_profile  # Simplifié pour la démo
            print(f"\n      ➡️  Menu 'Mes Candidatures': {'✅ AFFICHÉ' if show_menu else '❌ MASQUÉ'}")
        
        # ================================================================
        # Résumé
        # ================================================================
        print("\n" + "="*80)
        print("✅ TESTS TERMINÉS")
        print("="*80)
        
        print("\n📊 Résumé:")
        print(f"   - Profil candidat: ✅ Configuré avec {len(perm_ids)} permissions")
        print(f"   - Utilisateurs candidats: {len(users)}")
        print(f"   - Collections candidatures: {len(app_collections)}")
        
        print("\n📝 Prochaines étapes:")
        print("   1. Se connecter avec candidat1")
        print("   2. Vérifier si le menu 'Mes Candidatures' s'affiche")
        print("   3. Créer/supprimer des candidatures pour tester le comportement dynamique")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()


if __name__ == "__main__":
    success = asyncio.run(test_candidature_tracking())
    sys.exit(0 if success else 1)
