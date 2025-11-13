#!/usr/bin/env python3
"""
Test des API IAM pour vérifier pourquoi les permissions sont à 0 dans l'interface
"""
import asyncio
import sys
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

async def test_iam_api():
    try:
        # 1. Se connecter et obtenir un token
        print("=" * 70)
        print(" 🔐 CONNEXION ET OBTENTION DU TOKEN")
        print("=" * 70 + "\n")
        
        api_url = "http://localhost:8001/auth-api"
        
        async with httpx.AsyncClient() as client:
            # Login
            login_response = await client.post(
                f"{api_url}/auth/local/login",
                json={"username": "adminbe", "password": "Awana2025!"}
            )
            
            if login_response.status_code != 200:
                print(f"❌ Erreur de connexion: {login_response.status_code}")
                print(login_response.text)
                return
            
            login_data = login_response.json()
            token = login_data.get("access_token")
            print(f"✅ Token obtenu: {token[:50]}...\n")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. Tester l'API des permissions
            print("=" * 70)
            print(" 📋 TEST API PERMISSIONS")
            print("=" * 70 + "\n")
            
            permissions_response = await client.get(
                f"{api_url}/iam/permissions",
                headers=headers
            )
            
            print(f"Status: {permissions_response.status_code}")
            
            if permissions_response.status_code == 200:
                permissions = permissions_response.json()
                print(f"✅ Nombre de permissions retournées: {len(permissions)}")
                
                if len(permissions) > 0:
                    print("\n📝 Exemples de permissions (5 premières):")
                    for perm in permissions[:5]:
                        print(f"  - {perm.get('code')}: {perm.get('name')}")
                else:
                    print("\n⚠️ L'API retourne une liste vide!")
            else:
                print(f"❌ Erreur API: {permissions_response.status_code}")
                print(permissions_response.text)
            
            # 3. Tester l'API des profils
            print("\n" + "=" * 70)
            print(" 👥 TEST API PROFILS")
            print("=" * 70 + "\n")
            
            profiles_response = await client.get(
                f"{api_url}/iam/profiles",
                headers=headers
            )
            
            print(f"Status: {profiles_response.status_code}")
            
            if profiles_response.status_code == 200:
                profiles = profiles_response.json()
                print(f"✅ Nombre de profils retournés: {len(profiles)}")
                
                if len(profiles) > 0:
                    print("\n📝 Profils:")
                    for profile in profiles:
                        perm_count = len(profile.get('permission_ids', []))
                        print(f"  - {profile.get('name')}: {perm_count} permissions")
                else:
                    print("\n⚠️ L'API retourne une liste vide!")
            else:
                print(f"❌ Erreur API: {profiles_response.status_code}")
                print(profiles_response.text)
            
            # 4. Tester l'API des groupes
            print("\n" + "=" * 70)
            print(" 🏢 TEST API GROUPES")
            print("=" * 70 + "\n")
            
            groups_response = await client.get(
                f"{api_url}/iam/groups",
                headers=headers
            )
            
            print(f"Status: {groups_response.status_code}")
            
            if groups_response.status_code == 200:
                groups = groups_response.json()
                print(f"✅ Nombre de groupes retournés: {len(groups)}")
                
                if len(groups) > 0:
                    print("\n📝 Groupes:")
                    for group in groups:
                        user_count = len(group.get('user_ids', []))
                        print(f"  - {group.get('name')}: {user_count} utilisateurs")
                else:
                    print("\n⚠️ L'API retourne une liste vide!")
            else:
                print(f"❌ Erreur API: {groups_response.status_code}")
                print(groups_response.text)
        
        # 5. Vérifier directement dans la base de données
        print("\n" + "=" * 70)
        print(" 🗄️ VÉRIFICATION BASE DE DONNÉES")
        print("=" * 70 + "\n")
        
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        # Compter dans chaque collection
        perm_count = await db.permissions.count_documents({})
        iam_perm_count = await db.iam_permissions.count_documents({})
        profile_count = await db.profiles.count_documents({})
        iam_profile_count = await db.iam_profiles.count_documents({})
        group_count = await db.groups.count_documents({})
        iam_group_count = await db.iam_groups.count_documents({})
        
        print(f"Base de données (auth_db):")
        print(f"  - permissions (legacy): {perm_count}")
        print(f"  - iam_permissions: {iam_perm_count}")
        print(f"  - profiles (legacy): {profile_count}")
        print(f"  - iam_profiles: {iam_profile_count}")
        print(f"  - groups (legacy): {group_count}")
        print(f"  - iam_groups: {iam_group_count}")
        
        # Vérifier quelle collection l'API IAM utilise
        print("\n" + "=" * 70)
        print(" 🎯 DIAGNOSTIC")
        print("=" * 70 + "\n")
        
        print("💡 L'API IAM utilise probablement les collections avec préfixe 'iam_'")
        print("   (iam_permissions, iam_profiles, iam_groups)")
        print("\n📊 Résumé:")
        print(f"   - Base de données IAM: {iam_perm_count} permissions, {iam_profile_count} profils, {iam_group_count} groupes")
        print(f"   - Base de données Legacy: {perm_count} permissions, {profile_count} profils, {group_count} groupes")
        
        if iam_perm_count < 100:
            print("\n⚠️ Il manque des permissions IAM!")
            print(f"   - Actuellement: {iam_perm_count}")
            print(f"   - Sur Emergent: 102")
            print(f"   - Manquant: ~{102 - iam_perm_count}")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_iam_api())
