#!/usr/bin/env python3
"""
Script to update IAM permissions with all required codes from migration
Adds missing permissions that were not in initial setup
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

async def update_permissions():
    """Add all missing permissions required by the migration"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    # Additional permissions needed for the migration
    new_permissions = [
        # Admin & Dashboard
        {
            "code": "admin.dashboard",
            "name": "Accès Tableau de Bord Admin",
            "description": "Accéder au tableau de bord administrateur",
            "resource": "admin",
            "action": "dashboard",
            "scope": "global",
            "category": "admin"
        },
        
        # Users Management
        {
            "code": "users.manage_status",
            "name": "Gérer Statut Utilisateur",
            "description": "Modifier le statut des utilisateurs",
            "resource": "users",
            "action": "manage_status",
            "scope": "global",
            "category": "users"
        },
        {
            "code": "users.reset_mfa",
            "name": "Réinitialiser MFA",
            "description": "Réinitialiser l'authentification multi-facteurs",
            "resource": "users",
            "action": "reset_mfa",
            "scope": "global",
            "category": "users"
        },
        
        # Groups Management
        {
            "code": "groups.manage",
            "name": "Gérer Groupes",
            "description": "Créer, modifier et supprimer des groupes",
            "resource": "groups",
            "action": "manage",
            "scope": "global",
            "category": "groups"
        },
        
        # Profiles (old system)
        {
            "code": "profiles.manage",
            "name": "Gérer Profils (Ancien)",
            "description": "Gérer les profils de l'ancien système",
            "resource": "profiles",
            "action": "manage",
            "scope": "global",
            "category": "legacy"
        },
        
        # Locations
        {
            "code": "locations.manage",
            "name": "Gérer Localisations",
            "description": "Gérer les localisations géographiques",
            "resource": "locations",
            "action": "manage",
            "scope": "global",
            "category": "configuration"
        },
        
        # References & Rules
        {
            "code": "references.manage",
            "name": "Gérer Référentiels",
            "description": "Gérer les données référentielles",
            "resource": "references",
            "action": "manage",
            "scope": "global",
            "category": "configuration"
        },
        {
            "code": "rules.manage",
            "name": "Gérer Règles Métier",
            "description": "Gérer les règles métier du système",
            "resource": "rules",
            "action": "manage",
            "scope": "global",
            "category": "configuration"
        },
        
        # Configuration
        {
            "code": "config.manage",
            "name": "Gérer Configuration",
            "description": "Gérer la configuration du système",
            "resource": "config",
            "action": "manage",
            "scope": "global",
            "category": "configuration"
        },
        {
            "code": "flags.manage",
            "name": "Gérer Feature Flags",
            "description": "Gérer les feature flags",
            "resource": "flags",
            "action": "manage",
            "scope": "global",
            "category": "configuration"
        },
        
        # Emails
        {
            "code": "emails.read_config",
            "name": "Lire Configuration Email",
            "description": "Consulter la configuration email",
            "resource": "emails",
            "action": "read_config",
            "scope": "global",
            "category": "emails"
        },
        {
            "code": "emails.configure",
            "name": "Configurer Emails",
            "description": "Modifier la configuration email SMTP",
            "resource": "emails",
            "action": "configure",
            "scope": "global",
            "category": "emails"
        },
        {
            "code": "emails.test",
            "name": "Tester Emails",
            "description": "Envoyer des emails de test",
            "resource": "emails",
            "action": "test",
            "scope": "global",
            "category": "emails"
        },
        {
            "code": "emails.read_history",
            "name": "Consulter Historique Emails",
            "description": "Voir l'historique des emails envoyés",
            "resource": "emails",
            "action": "read_history",
            "scope": "global",
            "category": "emails"
        },
        {
            "code": "emails.manage_templates",
            "name": "Gérer Templates Email",
            "description": "Créer et modifier les templates d'email",
            "resource": "emails",
            "action": "manage_templates",
            "scope": "global",
            "category": "emails"
        },
        
        # Missions
        {
            "code": "missions.browse",
            "name": "Parcourir Missions",
            "description": "Consulter les offres de mission disponibles",
            "resource": "missions",
            "action": "browse",
            "scope": "global",
            "category": "missions"
        },
        {
            "code": "missions.publish",
            "name": "Publier Missions",
            "description": "Publier des missions",
            "resource": "missions",
            "action": "publish",
            "scope": "global",
            "category": "missions"
        },
        
        # Applications
        {
            "code": "applications.read_own",
            "name": "Consulter Mes Candidatures",
            "description": "Voir ses propres candidatures",
            "resource": "applications",
            "action": "read_own",
            "scope": "own",
            "category": "applications"
        },
        {
            "code": "applications.create",
            "name": "Postuler",
            "description": "Créer une candidature à une mission",
            "resource": "applications",
            "action": "create",
            "scope": "own",
            "category": "applications"
        },
        {
            "code": "applications.review",
            "name": "Examiner Candidatures",
            "description": "Examiner et évaluer les candidatures",
            "resource": "applications",
            "action": "review",
            "scope": "global",
            "category": "applications"
        },
        
        # Validations
        {
            "code": "validations.perform",
            "name": "Effectuer Validations",
            "description": "Effectuer des validations",
            "resource": "validations",
            "action": "perform",
            "scope": "global",
            "category": "validations"
        },
        {
            "code": "validations.approve",
            "name": "Approuver",
            "description": "Approuver des éléments",
            "resource": "validations",
            "action": "approve",
            "scope": "global",
            "category": "validations"
        },
        {
            "code": "validations.reject",
            "name": "Rejeter",
            "description": "Rejeter des éléments",
            "resource": "validations",
            "action": "reject",
            "scope": "global",
            "category": "validations"
        },
        
        # Profile (Own)
        {
            "code": "profile.manage_own",
            "name": "Gérer Mon Profil",
            "description": "Modifier son propre profil",
            "resource": "profile",
            "action": "manage_own",
            "scope": "own",
            "category": "profile"
        },
    ]
    
    print(f"🔄 Updating IAM permissions...")
    added_count = 0
    updated_count = 0
    
    for perm_data in new_permissions:
        # Check if permission exists
        existing = await db.permissions.find_one({"code": perm_data["code"]})
        
        if not existing:
            # Add new permission
            perm_data.update({
                "id": str(uuid.uuid4()),
                "is_system": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            await db.permissions.insert_one(perm_data)
            print(f"  ✅ Added: {perm_data['code']}")
            added_count += 1
        else:
            # Update existing permission metadata
            await db.permissions.update_one(
                {"code": perm_data["code"]},
                {"$set": {
                    "name": perm_data["name"],
                    "description": perm_data["description"],
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            print(f"  🔄 Updated: {perm_data['code']}")
            updated_count += 1
    
    # Update Admin profile with all new permissions
    all_permissions = await db.permissions.find({}).to_list(length=None)
    all_permission_ids = [p["id"] for p in all_permissions]
    
    await db.profiles.update_one(
        {"code": "admin"},
        {"$set": {
            "permission_ids": all_permission_ids,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    print(f"\n✅ Updated Admin profile with all {len(all_permission_ids)} permissions")
    
    print(f"\n📊 Summary:")
    print(f"  - Added: {added_count} new permissions")
    print(f"  - Updated: {updated_count} existing permissions")
    print(f"  - Total permissions: {len(all_permissions)}")
    
    client.close()
    print("\n✅ IAM permissions update complete!")

if __name__ == "__main__":
    asyncio.run(update_permissions())
