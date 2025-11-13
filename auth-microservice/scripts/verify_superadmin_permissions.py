#!/usr/bin/env python3
"""
Vérifier que le compte super_admin possède bien tous les droits
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def verify_superadmin():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        print("=" * 70)
        print(" 🔍 VÉRIFICATION DU COMPTE SUPER ADMIN")
        print("=" * 70 + "\n")
        
        # 1. Trouver l'utilisateur admin/adminbe
        print("1️⃣ Recherche de l'utilisateur admin...\n")
        
        admin_user = await db.users.find_one({"roles": "super_admin"}, {"_id": 0})
        
        if not admin_user:
            print("❌ Aucun utilisateur avec le rôle 'super_admin' trouvé!")
            client.close()
            return
        
        print(f"✅ Utilisateur trouvé:")
        print(f"   - ID: {admin_user.get('id')}")
        print(f"   - Username: {admin_user.get('username')}")
        print(f"   - Email: {admin_user.get('email')}")
        print(f"   - Roles: {admin_user.get('roles')}")
        print(f"   - Status: {admin_user.get('status')}")
        print(f"   - Active: {admin_user.get('is_active')}")
        
        # 2. Vérifier le profil super_admin
        print("\n" + "=" * 70)
        print("2️⃣ Vérification du profil 'super_admin'...\n")
        
        super_admin_profile = await db.profiles.find_one({"code": "super_admin"}, {"_id": 0})
        
        if not super_admin_profile:
            print("❌ Profil 'super_admin' non trouvé!")
        else:
            print(f"✅ Profil super_admin trouvé:")
            print(f"   - ID: {super_admin_profile.get('id')}")
            print(f"   - Name: {super_admin_profile.get('name')}")
            print(f"   - Permissions: {len(super_admin_profile.get('permission_ids', []))}")
        
        # 3. Compter les permissions totales
        print("\n" + "=" * 70)
        print("3️⃣ Permissions disponibles dans le système...\n")
        
        total_perms = await db.permissions.count_documents({})
        print(f"📊 Total permissions en base: {total_perms}")
        
        if super_admin_profile:
            profile_perm_count = len(super_admin_profile.get('permission_ids', []))
            print(f"👤 Permissions du profil super_admin: {profile_perm_count}")
            
            if profile_perm_count < total_perms:
                print(f"\n⚠️ Il manque {total_perms - profile_perm_count} permissions au profil super_admin!")
                print("   Le profil devrait avoir TOUTES les permissions.")
            else:
                print(f"\n✅ Le profil super_admin possède toutes les permissions!")
        
        # 4. Vérifier les groupes IAM
        print("\n" + "=" * 70)
        print("4️⃣ Vérification des groupes IAM...\n")
        
        super_admin_group = await db.iam_groups.find_one({"code": "grp.super_admin"}, {"_id": 0})
        
        if super_admin_group:
            user_ids = super_admin_group.get('user_ids', [])
            print(f"✅ Groupe IAM 'grp.super_admin' trouvé:")
            print(f"   - Utilisateurs: {len(user_ids)}")
            
            if admin_user.get('id') in user_ids:
                print(f"   ✅ L'utilisateur '{admin_user.get('username')}' est dans le groupe")
            else:
                print(f"   ⚠️ L'utilisateur '{admin_user.get('username')}' N'EST PAS dans le groupe!")
                print(f"      Il devrait être ajouté au groupe grp.super_admin")
        else:
            print("⚠️ Groupe IAM 'grp.super_admin' non trouvé")
        
        # 5. Vérifier la permission spéciale *:*
        print("\n" + "=" * 70)
        print("5️⃣ Vérification de la permission spéciale '*:*'...\n")
        
        all_perm = await db.permissions.find_one({"code": "*:*"}, {"_id": 0})
        
        if all_perm:
            print("✅ Permission '*:*' (toutes permissions) existe")
            
            if super_admin_profile:
                perm_ids = super_admin_profile.get('permission_ids', [])
                if all_perm.get('id') in perm_ids:
                    print("   ✅ Le profil super_admin possède la permission '*:*'")
                else:
                    print("   ⚠️ Le profil super_admin NE possède PAS la permission '*:*'")
        else:
            print("⚠️ Permission '*:*' non trouvée")
        
        # 6. Résumé et recommandations
        print("\n" + "=" * 70)
        print(" 📋 RÉSUMÉ ET RECOMMANDATIONS")
        print("=" * 70 + "\n")
        
        issues = []
        
        if admin_user.get('status') != 'active':
            issues.append(f"❌ Status de l'utilisateur est '{admin_user.get('status')}' au lieu de 'active'")
        
        if not admin_user.get('is_active'):
            issues.append("❌ L'utilisateur n'est pas actif (is_active = False)")
        
        if not super_admin_profile:
            issues.append("❌ Profil super_admin manquant")
        elif len(super_admin_profile.get('permission_ids', [])) < total_perms:
            issues.append(f"❌ Le profil super_admin ne possède pas toutes les permissions ({profile_perm_count}/{total_perms})")
        
        if super_admin_group:
            if admin_user.get('id') not in super_admin_group.get('user_ids', []):
                issues.append("❌ L'utilisateur n'est pas dans le groupe IAM super_admin")
        
        if issues:
            print("⚠️ PROBLÈMES DÉTECTÉS:\n")
            for issue in issues:
                print(f"   {issue}")
            
            print("\n💡 ACTIONS RECOMMANDÉES:")
            print("   1. Exécutez: python scripts/fix_superadmin_permissions.py")
            print("   2. Reconnectez-vous à l'interface")
        else:
            print("✅ Tout est OK! Le compte super_admin possède tous les droits.")
            print(f"\n🎯 Permissions système: {total_perms}")
            print(f"🎯 L'utilisateur '{admin_user.get('username')}' peut tout faire!")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_superadmin())
