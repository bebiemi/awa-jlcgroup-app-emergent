"""
Diagnostic Script for Login Issue
Tests user "lala" and verifies all IAM components
"""
import asyncio
import os

import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

from awana_auth.core.iam_constants import IAMGroups

async def diagnose_login_issue():
    print("\n" + "="*80)
    print("🔍 DIAGNOSTIC COMPLET - Problème de Login")
    print("="*80)
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://mongodb:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['jlc_interim']
    
    username = "lala"
    test_password = "azerty123456!!"
    
    print(f"\n🔍 Recherche de l'utilisateur: {username}")
    print("-" * 80)
    
    # 1. Check if user exists
    user = await db.users.find_one({"username": username})
    
    if not user:
        print(f"❌ ERREUR: Utilisateur '{username}' introuvable dans la base !")
        client.close()
        return
    
    print(f"✅ Utilisateur trouvé")
    print(f"   - ID: {user.get('id')}")
    print(f"   - Email: {user.get('email')}")
    print(f"   - Status: {user.get('status')}")
    print(f"   - Roles: {user.get('roles')}")
    print(f"   - Is Collaborator: {user.get('is_collaborator', False)}")
    print(f"   - Created: {user.get('created_at')}")
    
    # 2. Test password hash
    print(f"\n🔐 Test du Hash du Mot de Passe")
    print("-" * 80)
    
    password_hash = user.get('password_hash')
    if not password_hash:
        print("❌ ERREUR CRITIQUE: Pas de password_hash dans la base !")
    else:
        print(f"✅ Password hash présent (longueur: {len(password_hash)})")
        
        # Test the password
        try:
            # Ensure password and hash are bytes
            password_bytes = test_password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8') if isinstance(password_hash, str) else password_hash
            
            is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
            
            if is_valid:
                print(f"✅ LE MOT DE PASSE CORRESPOND AU HASH !")
            else:
                print(f"❌ ERREUR CRITIQUE: Le mot de passe NE correspond PAS au hash !")
                print(f"   Password testé: '{test_password}'")
                print(f"   Hash stocké: {password_hash[:50]}...")
                
                # Try to create a new hash to compare
                new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
                print(f"\n   Hash généré pour test: {new_hash[:50]}...")
                print(f"   Format identique: {len(new_hash) == len(password_hash)}")
                
        except Exception as e:
            print(f"❌ ERREUR lors de la vérification: {e}")
    
    # 3. Check IAM group assignment
    print(f"\n👥 Vérification de l'Assignation aux Groupes IAM")
    print("-" * 80)
    
    user_id = user.get('id')
    groups_with_user = await db.iam_groups.find({"user_ids": user_id}).to_list(None)
    
    if not groups_with_user:
        print(f"❌ ERREUR CRITIQUE: L'utilisateur n'est dans AUCUN groupe IAM !")
        print(f"   User ID recherché: {user_id}")
    else:
        print(f"✅ Utilisateur trouvé dans {len(groups_with_user)} groupe(s):")
        for group in groups_with_user:
            print(f"   - {group.get('code')}: {group.get('name')}")
            print(f"     Profils: {len(group.get('profile_ids', []))} profil(s)")
            print(f"     Users: {len(group.get('user_ids', []))} utilisateur(s)")
    
    # 4. Check candidat group specifically
    candidat_group_code = IAMGroups.CANDIDAT

    print(f"\n📋 Vérification du Groupe '{candidat_group_code}'")
    print("-" * 80)

    candidat_group = await db.iam_groups.find_one({"code": candidat_group_code})
    
    if not candidat_group:
        print(f"❌ ERREUR: Le groupe '{candidat_group_code}' n'existe pas !")
    else:
        print(f"✅ Groupe '{candidat_group_code}' existe")
        print(f"   - ID: {candidat_group.get('id')}")
        print(f"   - Nom: {candidat_group.get('name')}")
        print(f"   - Profile IDs: {candidat_group.get('profile_ids')}")
        print(f"   - User IDs: {len(candidat_group.get('user_ids', []))} utilisateur(s)")
        
        if user_id in candidat_group.get('user_ids', []):
            print(f"   ✅ L'utilisateur '{username}' EST dans ce groupe")
        else:
            print(f"   ❌ L'utilisateur '{username}' N'EST PAS dans ce groupe !")
            print(f"      User ID: {user_id}")
            print(f"      User IDs dans le groupe: {candidat_group.get('user_ids', [])}")
    
    # 5. Check profiles and permissions
    print(f"\n🔑 Vérification des Profils et Permissions")
    print("-" * 80)
    
    if candidat_group and candidat_group.get('profile_ids'):
        for profile_id in candidat_group.get('profile_ids', []):
            profile = await db.iam_profiles.find_one({"id": profile_id})
            if profile:
                print(f"\n   Profil: {profile.get('code')} - {profile.get('name')}")
                print(f"   - Permissions: {len(profile.get('permission_ids', []))}")
                
                # List permissions
                for perm_id in profile.get('permission_ids', [])[:5]:  # First 5
                    perm = await db.iam_permissions.find_one({"id": perm_id})
                    if perm:
                        print(f"     • {perm.get('code')}: {perm.get('name')}")
                
                if len(profile.get('permission_ids', [])) > 5:
                    print(f"     ... et {len(profile.get('permission_ids', [])) - 5} autres")
            else:
                print(f"   ❌ Profil ID '{profile_id}' introuvable !")
    else:
        print("   ⚠️ Aucun profil associé au groupe candidat")
    
    # 6. Check validation record
    print(f"\n📝 Vérification du Record de Validation")
    print("-" * 80)
    
    validation = await db.validations.find_one({"user_id": user_id})
    if validation:
        print("✅ Record de validation trouvé")
        print(f"   - Type: {validation.get('validation_type')}")
        print(f"   - Status: {validation.get('status')}")
    else:
        print("⚠️ Aucun record de validation (normal pour candidats actifs)")
    
    # 7. Summary
    print(f"\n" + "="*80)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("="*80)
    
    issues = []
    
    if not password_hash:
        issues.append("❌ Pas de password hash")
    elif not is_valid:
        issues.append("❌ Mot de passe ne correspond pas au hash")
    
    if not groups_with_user:
        issues.append("❌ Utilisateur pas dans de groupe IAM")
    elif candidat_group and user_id not in candidat_group.get('user_ids', []):
        issues.append(f"❌ Utilisateur pas dans {candidat_group_code}")
    
    if candidat_group and not candidat_group.get('profile_ids'):
        issues.append("⚠️ Groupe candidat sans profils")
    
    if issues:
        print("\n🚨 PROBLÈMES IDENTIFIÉS:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ TOUT SEMBLE CORRECT !")
        print("   Le problème peut venir du code de login lui-même.")
    
    print("\n" + "="*80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(diagnose_login_issue())
