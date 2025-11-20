#!/usr/bin/env python3
"""
Migration IAM pour les Candidats
- Crée les permissions nécessaires
- Met à jour le profil candidat
- Renomme "postulant" en "candidat"
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")

# Permissions nécessaires pour les candidats
CANDIDAT_PERMISSIONS = [
    # Dashboard
    {"code": "dashboard.candidat.access", "name": "Accès tableau de bord candidat", "resource": "dashboard", "action": "candidat", "scope": "own", "category": "dashboard"},
    
    # Missions - Consultation des offres
    {"code": "missions.browse", "name": "Naviguer missions", "resource": "missions", "action": "browse", "scope": "organization", "category": "missions"},
    {"code": "missions.read", "name": "Lire missions (générique)", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    
    # Applications - Candidatures
    {"code": "applications.read.own", "name": "Lire ses candidatures", "resource": "applications", "action": "read", "scope": "own", "category": "applications"},
    {"code": "applications.create.own", "name": "Créer ses candidatures", "resource": "applications", "action": "create", "scope": "own", "category": "applications"},
    {"code": "applications.update.own", "name": "Mettre à jour ses candidatures", "resource": "applications", "action": "update", "scope": "own", "category": "applications"},
    {"code": "applications.delete.own", "name": "Supprimer ses candidatures", "resource": "applications", "action": "delete", "scope": "own", "category": "applications"},
    
    # Profil
    {"code": "profile.view.own", "name": "Voir son profil", "resource": "profile", "action": "view", "scope": "own", "category": "profile"},
    {"code": "profile.edit.own", "name": "Éditer son profil", "resource": "profile", "action": "edit", "scope": "own", "category": "profile"},
    {"code": "profile.manage.own", "name": "Gérer son profil", "resource": "profile", "action": "manage", "scope": "own", "category": "profile"},
    
    # Documents
    {"code": "documents.read.own", "name": "Lire ses documents", "resource": "documents", "action": "read", "scope": "own", "category": "documents"},
    {"code": "documents.create.own", "name": "Créer ses documents", "resource": "documents", "action": "create", "scope": "own", "category": "documents"},
    {"code": "documents.update.own", "name": "Mettre à jour ses documents", "resource": "documents", "action": "update", "scope": "own", "category": "documents"},
    {"code": "documents.delete.own", "name": "Supprimer ses documents", "resource": "documents", "action": "delete", "scope": "own", "category": "documents"},
]


async def migrate():
    print("\n" + "="*80)
    print("🔄 MIGRATION IAM CANDIDATS")
    print("="*80 + "\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # ================================================================
        # ÉTAPE 1: Créer les permissions nécessaires
        # ================================================================
        print("1️⃣ Création des permissions candidat...")
        
        created_perms = []
        for perm_data in CANDIDAT_PERMISSIONS:
            existing = await db.permissions.find_one({"code": perm_data["code"]}, {"_id": 0, "id": 1})
            
            if existing:
                print(f"   ℹ️  Permission existe déjà: {perm_data['code']}")
                created_perms.append(existing["id"])
            else:
                perm = {
                    "id": str(uuid4()),
                    "code": perm_data["code"],
                    "name": perm_data["name"],
                    "resource": perm_data["resource"],
                    "action": perm_data["action"],
                    "scope": perm_data["scope"],
                    "category": perm_data["category"],
                    "is_system": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                await db.permissions.insert_one(perm)
                created_perms.append(perm["id"])
                print(f"   ✅ Créée: {perm_data['code']}")
        
        print(f"\n   Total permissions: {len(created_perms)}\n")
        
        # ================================================================
        # ÉTAPE 2: Créer/Mettre à jour le profil candidat
        # ================================================================
        print("2️⃣ Création/Mise à jour du profil Candidat...")
        
        candidat_profile = {
            "id": str(uuid4()),
            "code": "candidat",
            "name": "Candidat",
            "description": "Profil pour les candidats (anciennement postulants)",
            "permission_ids": created_perms,
            "capability_bundle_ids": [],
            "is_system_role": False,
            "is_protected": False,
            "priority": 100,
            "category": "candidat",
            "color": "#3B82F6",
            "icon": "UserCircle",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        existing_profile = await db.profiles.find_one({"code": "candidat"})
        if existing_profile:
            await db.profiles.update_one(
                {"code": "candidat"},
                {"$set": {
                    "permission_ids": created_perms,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            candidat_profile_id = existing_profile["id"]
            print(f"   ✅ Profil mis à jour avec {len(created_perms)} permissions\n")
        else:
            await db.profiles.insert_one(candidat_profile)
            candidat_profile_id = candidat_profile["id"]
            print(f"   ✅ Profil créé avec {len(created_perms)} permissions\n")
        
        # ================================================================
        # ÉTAPE 3: Migrer les utilisateurs "applicant" vers "candidat"
        # ================================================================
        print("3️⃣ Migration des utilisateurs...")
        
        # Trouver tous les utilisateurs avec le rôle "applicant" ou "postulant"
        users_to_migrate = await db.users.find({
            "$or": [
                {"roles": {"$in": ["applicant", "postulant"]}},
                {"role": {"$in": ["applicant", "postulant"]}}
            ]
        }, {"_id": 0, "id": 1, "username": 1, "email": 1, "roles": 1}).to_list(None)
        
        if users_to_migrate:
            print(f"   Trouvé {len(users_to_migrate)} utilisateur(s) à migrer:")
            
            for user in users_to_migrate:
                # Mettre à jour le rôle et ajouter le profil candidat
                update_result = await db.users.update_one(
                    {"id": user["id"]},
                    {
                        "$set": {
                            "role": "candidat",
                            "roles": ["candidat"],
                            "updated_at": datetime.now(timezone.utc)
                        },
                        "$addToSet": {"profile_ids": candidat_profile_id}
                    }
                )
                
                if update_result.modified_count > 0:
                    print(f"   ✅ {user['username']} ({user['email']}) → candidat")
                else:
                    print(f"   ℹ️  {user['username']} déjà à jour")
        else:
            print("   ℹ️  Aucun utilisateur à migrer\n")
        
        # ================================================================
        # ÉTAPE 4: Renommer le profil "applicant" en "candidat_legacy"
        # ================================================================
        print("\n4️⃣ Renommage du profil legacy...")
        
        legacy_profile = await db.profiles.find_one({"code": "applicant"})
        if legacy_profile:
            await db.profiles.update_one(
                {"code": "applicant"},
                {"$set": {
                    "code": "candidat_legacy",
                    "name": "Candidat (Legacy - Ne plus utiliser)",
                    "is_protected": True,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            print("   ✅ Profil 'applicant' renommé en 'candidat_legacy'\n")
        else:
            print("   ℹ️  Profil 'applicant' non trouvé\n")
        
        # ================================================================
        # STATISTIQUES FINALES
        # ================================================================
        print("="*80)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS!")
        print("="*80)
        
        print("\n📊 Résumé:")
        print(f"   - Permissions créées/vérifiées: {len(created_perms)}")
        print(f"   - Profil 'candidat': ✅ Opérationnel")
        print(f"   - Utilisateurs migrés: {len(users_to_migrate)}")
        
        print("\n📝 Prochaines étapes:")
        print("   1. Migrer la Sidebar pour utiliser 'dashboard.candidat.access'")
        print("   2. Nettoyer les références à 'postulant' dans le code")
        print("   3. Tester la connexion avec candidat1")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(migrate())
    sys.exit(0 if success else 1)
