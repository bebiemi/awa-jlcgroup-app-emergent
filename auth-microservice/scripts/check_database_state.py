#!/usr/bin/env python3
"""
Vérification de l'état de la base de données
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_state():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        print(f"🔌 Connexion à MongoDB: {mongo_url}\n")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        print("=" * 70)
        print(" 📊 ÉTAT DES COLLECTIONS")
        print("=" * 70)
        
        collections_to_check = [
            ("users", "Utilisateurs"),
            ("permissions", "Permissions (Legacy)"),
            ("profiles", "Profils (Legacy)"),
            ("groups", "Groupes (Legacy)"),
            ("iam_permissions", "Permissions IAM"),
            ("iam_profiles", "Profils IAM"),
            ("iam_groups", "Groupes IAM"),
            ("system_references", "Références Système"),
            ("audit_logs", "Journaux d'Audit"),
            ("sessions", "Sessions"),
            ("locations", "Locations"),
            ("validations", "Validations"),
        ]
        
        collection_names = await db.list_collection_names()
        
        for coll_name, coll_label in collections_to_check:
            if coll_name in collection_names:
                count = await db[coll_name].count_documents({})
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {coll_label:30s} : {count:4d} documents")
            else:
                print(f"❌ {coll_label:30s} : Collection manquante")
        
        print("\n" + "=" * 70)
        print(" 🔍 DÉTAILS DES PERMISSIONS")
        print("=" * 70)
        
        # Check permissions collection
        print("\n📋 Permissions (Legacy):")
        perm_count = await db.permissions.count_documents({})
        print(f"   Total: {perm_count}")
        
        if perm_count > 0:
            sample_perms = await db.permissions.find({}, {"_id": 0, "code": 1, "name": 1}).limit(5).to_list(5)
            print("   Exemples:")
            for perm in sample_perms:
                print(f"     - {perm.get('code')}: {perm.get('name')}")
        
        # Check IAM permissions
        print("\n🔐 Permissions IAM:")
        iam_perm_count = await db.iam_permissions.count_documents({})
        print(f"   Total: {iam_perm_count}")
        
        if iam_perm_count > 0:
            sample_perms = await db.iam_permissions.find({}, {"_id": 0, "code": 1, "name": 1}).limit(5).to_list(5)
            print("   Exemples:")
            for perm in sample_perms:
                print(f"     - {perm.get('code')}: {perm.get('name')}")
        
        print("\n" + "=" * 70)
        print(" 👥 DÉTAILS DES PROFILS")
        print("=" * 70)
        
        # Check profiles
        print("\n👤 Profils (Legacy):")
        profile_count = await db.profiles.count_documents({})
        print(f"   Total: {profile_count}")
        
        if profile_count > 0:
            profiles = await db.profiles.find({}, {"_id": 0, "code": 1, "name": 1, "permission_ids": 1}).to_list(100)
            for prof in profiles:
                perm_count = len(prof.get('permission_ids', []))
                print(f"     - {prof.get('code'):20s} : {prof.get('name'):30s} ({perm_count} permissions)")
        
        # Check IAM profiles
        print("\n🆔 Profils IAM:")
        iam_profile_count = await db.iam_profiles.count_documents({})
        print(f"   Total: {iam_profile_count}")
        
        if iam_profile_count > 0:
            profiles = await db.iam_profiles.find({}, {"_id": 0, "code": 1, "name": 1, "permission_ids": 1}).to_list(100)
            for prof in profiles:
                perm_count = len(prof.get('permission_ids', []))
                print(f"     - {prof.get('code'):20s} : {prof.get('name'):30s} ({perm_count} permissions)")
        
        print("\n" + "=" * 70)
        print(" 🏢 DÉTAILS DES GROUPES")
        print("=" * 70)
        
        # Check groups
        print("\n🏢 Groupes (Legacy):")
        group_count = await db.groups.count_documents({})
        print(f"   Total: {group_count}")
        
        if group_count > 0:
            groups = await db.groups.find({}, {"_id": 0, "code": 1, "name": 1, "user_ids": 1}).to_list(100)
            for grp in groups:
                user_count = len(grp.get('user_ids', []))
                print(f"     - {grp.get('code'):20s} : {grp.get('name'):30s} ({user_count} utilisateurs)")
        
        # Check IAM groups
        print("\n🏛️ Groupes IAM:")
        iam_group_count = await db.iam_groups.count_documents({})
        print(f"   Total: {iam_group_count}")
        
        if iam_group_count > 0:
            groups = await db.iam_groups.find({}, {"_id": 0, "code": 1, "name": 1, "user_ids": 1}).to_list(100)
            for grp in groups:
                user_count = len(grp.get('user_ids', []))
                print(f"     - {grp.get('code'):20s} : {grp.get('name'):30s} ({user_count} utilisateurs)")
        
        print("\n" + "=" * 70)
        print(" 🎯 DIAGNOSTIC")
        print("=" * 70)
        
        issues = []
        
        if perm_count == 0:
            issues.append("❌ Aucune permission (legacy) trouvée")
        
        if iam_perm_count == 0:
            issues.append("❌ Aucune permission IAM trouvée")
        
        if profile_count == 0:
            issues.append("❌ Aucun profil (legacy) trouvé")
        
        if iam_profile_count == 0:
            issues.append("❌ Aucun profil IAM trouvé")
        
        if group_count == 0:
            issues.append("⚠️ Aucun groupe (legacy) trouvé")
        
        if iam_group_count == 0:
            issues.append("❌ Aucun groupe IAM trouvé")
        
        if issues:
            print("\n⚠️ PROBLÈMES DÉTECTÉS:\n")
            for issue in issues:
                print(f"   {issue}")
            
            print("\n💡 SOLUTION:")
            print("   Le script d'initialisation n'a pas créé les données.")
            print("   Cause possible: Erreur lors de l'exécution ou collections déjà existantes mais vides.")
            print("\n   Exécutez à nouveau:")
            print("   docker exec jlc-auth-dev python /app/auth-microservice/scripts/complete_database_initialization.py")
        else:
            print("\n✅ Toutes les collections sont correctement initialisées!")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_state())
