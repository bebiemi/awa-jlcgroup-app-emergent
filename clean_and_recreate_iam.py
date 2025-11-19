#!/usr/bin/env python3
"""
Script de nettoyage et recréation complète des Groupes IAM
Crée une structure propre et cohérente avec IAMService
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from uuid import uuid4
import os

# Définition des groupes nécessaires
REQUIRED_GROUPS = [
    {
        "id": str(uuid4()),
        "code": "grp.super_admin",
        "name": "Super Administrateurs",
        "description": "Groupe des super administrateurs avec accès complet",
        "profile_ids": [],  # Sera rempli avec le profil Super Admin
        "user_ids": [],  # Sera synchronisé avec les users ayant role super_admin
        "is_system_group": True,
        "is_protected": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid4()),
        "code": "grp.admin",
        "name": "Administrateurs",
        "description": "Groupe des administrateurs système",
        "profile_ids": [],  # Profil Admin
        "user_ids": [],
        "is_system_group": True,
        "is_protected": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid4()),
        "code": "grp.company",
        "name": "Entreprises",
        "description": "Groupe des représentants d'entreprises",
        "profile_ids": [],  # Profil Entreprise
        "user_ids": [],
        "is_system_group": True,
        "is_protected": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid4()),
        "code": "grp.commercial",
        "name": "Commerciaux",
        "description": "Groupe des commerciaux",
        "profile_ids": [],  # Profil Commercial
        "user_ids": [],
        "is_system_group": True,
        "is_protected": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid4()),
        "code": "grp.applicant",
        "name": "Candidats",
        "description": "Groupe des candidats/postulants",
        "profile_ids": [],  # Profil Candidat
        "user_ids": [],
        "is_system_group": True,
        "is_protected": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
]

async def clean_and_recreate():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("="*80)
    print("NETTOYAGE ET RECRÉATION IAM")
    print("="*80)
    
    # 1. BACKUP des informations importantes
    print("\n📦 1. BACKUP DES DONNÉES IMPORTANTES")
    print("-"*80)
    
    # Mapper profils par code
    profiles = await db.profiles.find({}, {"_id": 0, "id": 1, "code": 1, "name": 1}).to_list(100)
    profile_map = {p['code']: p for p in profiles}
    
    print(f"   ✅ {len(profiles)} profils identifiés")
    
    # Mapper utilisateurs par rôle
    users = await db.users.find({}, {"_id": 0, "id": 1, "username": 1, "roles": 1}).to_list(100)
    users_by_role = {}
    for u in users:
        for role in u.get('roles', []):
            if role not in users_by_role:
                users_by_role[role] = []
            users_by_role[role].append(u['id'])
    
    print(f"   ✅ {len(users)} utilisateurs identifiés")
    
    # 2. SUPPRESSION de tous les groupes
    print("\n🗑️  2. SUPPRESSION DE TOUS LES GROUPES")
    print("-"*80)
    
    result = await db.groups.delete_many({})
    print(f"   ✅ {result.deleted_count} groupes supprimés")
    
    # 3. ASSIGNATION des profils aux groupes
    print("\n🔗 3. PRÉPARATION DES GROUPES AVEC PROFILS")
    print("-"*80)
    
    profile_assignments = {
        "grp.super_admin": "profile.super_admin",
        "grp.admin": "profile.admin",
        "grp.company": "profile.company",
        "grp.commercial": "profile.commercial",
        "grp.applicant": "profile.candidat_confirmed"
    }
    
    for group in REQUIRED_GROUPS:
        profile_code = profile_assignments.get(group['code'])
        if profile_code and profile_code in profile_map:
            group['profile_ids'] = [profile_map[profile_code]['id']]
            print(f"   ✅ {group['name']}: Profil {profile_map[profile_code]['name']}")
        else:
            print(f"   ⚠️  {group['name']}: Aucun profil assigné")
    
    # 4. ASSIGNATION des utilisateurs aux groupes
    print("\n👥 4. ASSIGNATION DES UTILISATEURS AUX GROUPES")
    print("-"*80)
    
    role_to_group = {
        "super_admin": "grp.super_admin",
        "admin": "grp.admin",
        "company": "grp.company",
        "commercial": "grp.commercial",
        "applicant": "grp.applicant"
    }
    
    for role, group_code in role_to_group.items():
        user_ids = users_by_role.get(role, [])
        for group in REQUIRED_GROUPS:
            if group['code'] == group_code:
                group['user_ids'] = user_ids
                print(f"   ✅ {group['name']}: {len(user_ids)} utilisateur(s)")
                break
    
    # 5. CRÉATION des nouveaux groupes
    print("\n✨ 5. CRÉATION DES GROUPES")
    print("-"*80)
    
    for group in REQUIRED_GROUPS:
        await db.groups.insert_one(group)
        print(f"   ✅ {group['name']} créé")
        print(f"      - Code: {group['code']}")
        print(f"      - ID: {group['id']}")
        print(f"      - Profils: {len(group['profile_ids'])}")
        print(f"      - Utilisateurs: {len(group['user_ids'])}")
    
    # 6. SYNCHRONISATION bidirectionnelle Users ↔ Groupes
    print("\n🔄 6. SYNCHRONISATION USERS ↔ GROUPES")
    print("-"*80)
    
    # Récupérer tous les groupes créés
    created_groups = await db.groups.find({}, {"_id": 0, "id": 1, "code": 1, "user_ids": 1}).to_list(100)
    
    # Pour chaque groupe, ajouter group_id aux utilisateurs
    for group in created_groups:
        if group['user_ids']:
            result = await db.users.update_many(
                {"id": {"$in": group['user_ids']}},
                {"$addToSet": {"group_ids": group['id']}}
            )
            print(f"   ✅ {group['code']}: {result.modified_count} utilisateur(s) synchronisé(s)")
    
    # 7. VÉRIFICATION FINALE
    print("\n📊 7. VÉRIFICATION FINALE")
    print("-"*80)
    
    final_groups = await db.groups.find({}).to_list(100)
    print(f"   Groupes créés: {len(final_groups)}")
    
    for group in final_groups:
        print(f"\n   📁 {group['name']}")
        print(f"      Code: {group['code']}")
        print(f"      ID: {group['id']}")
        print(f"      Profils: {len(group.get('profile_ids', []))}")
        print(f"      Utilisateurs: {len(group.get('user_ids', []))}")
        print(f"      Protégé: {group.get('is_protected', False)}")
        print(f"      Système: {group.get('is_system_group', False)}")
        
        # Vérifier cohérence bidirectionnelle
        if group.get('user_ids'):
            users_with_group = await db.users.count_documents({"group_ids": group['id']})
            if users_with_group == len(group['user_ids']):
                print(f"      ✅ Cohérence bidirectionnelle OK")
            else:
                print(f"      ⚠️  Incohérence: {users_with_group} users ont le groupe vs {len(group['user_ids'])} dans group.user_ids")
    
    print("\n" + "="*80)
    print("✅ NETTOYAGE ET RECRÉATION TERMINÉS")
    print("="*80)
    print("\n💡 Prochaines étapes:")
    print("   1. Redémarrer le backend pour invalider les caches")
    print("   2. Tester l'assignation de profils aux groupes")
    print("   3. Vérifier les permissions des utilisateurs")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clean_and_recreate())
