#!/usr/bin/env python3
"""
Script de réinitialisation complète de la base de données locale IAM
- Nettoie toutes les permissions invalides
- Crée toutes les permissions modernes
- Crée le profil SuperAdmin avec toutes les permissions
- Crée/Réinitialise le compte superAdmin
- Peut supprimer les utilisateurs de test si demandé
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
import argparse

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent / "auth-microservice"))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")  # Base de données IAM (auth_db par défaut)

# Toutes les permissions IAM modernes
ALL_MODERN_PERMISSIONS = [
    # MISSIONS
    {"code": "missions.browse", "name": "Naviguer missions", "resource": "missions", "action": "browse", "scope": "organization", "category": "missions"},
    {"code": "missions.read.all", "name": "Lire toutes les missions", "resource": "missions", "action": "read", "scope": "all", "category": "missions"},
    {"code": "missions.read.own", "name": "Lire ses missions", "resource": "missions", "action": "read", "scope": "own", "category": "missions"},
    {"code": "missions.create.all", "name": "Créer missions (toutes)", "resource": "missions", "action": "create", "scope": "all", "category": "missions"},
    {"code": "missions.create.own", "name": "Créer ses missions", "resource": "missions", "action": "create", "scope": "own", "category": "missions"},
    {"code": "missions.edit.all", "name": "Éditer toutes les missions", "resource": "missions", "action": "edit", "scope": "all", "category": "missions"},
    {"code": "missions.edit.own", "name": "Éditer ses missions", "resource": "missions", "action": "edit", "scope": "own", "category": "missions"},
    {"code": "missions.delete.all", "name": "Supprimer toutes les missions", "resource": "missions", "action": "delete", "scope": "all", "category": "missions"},
    {"code": "missions.delete.own", "name": "Supprimer ses missions", "resource": "missions", "action": "delete", "scope": "own", "category": "missions"},
    {"code": "missions.manage.all", "name": "Gérer toutes les missions", "resource": "missions", "action": "manage", "scope": "all", "category": "missions"},
    {"code": "missions.read", "name": "Lire missions (générique)", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    {"code": "missions.create", "name": "Créer missions (générique)", "resource": "missions", "action": "create", "scope": "organization", "category": "missions"},
    {"code": "missions.update", "name": "Mettre à jour missions", "resource": "missions", "action": "update", "scope": "organization", "category": "missions"},
    {"code": "missions.delete", "name": "Supprimer missions", "resource": "missions", "action": "delete", "scope": "organization", "category": "missions"},
    {"code": "missions.manage", "name": "Gérer missions", "resource": "missions", "action": "manage", "scope": "organization", "category": "missions"},
    
    # BESOINS
    {"code": "besoins.view.all", "name": "Voir tous les besoins", "resource": "besoins", "action": "view", "scope": "all", "category": "besoins"},
    {"code": "besoins.view.own", "name": "Voir ses besoins", "resource": "besoins", "action": "view", "scope": "own", "category": "besoins"},
    {"code": "besoins.create.all", "name": "Créer besoins (tous)", "resource": "besoins", "action": "create", "scope": "all", "category": "besoins"},
    {"code": "besoins.create.own", "name": "Créer ses besoins", "resource": "besoins", "action": "create", "scope": "own", "category": "besoins"},
    {"code": "besoins.edit.all", "name": "Éditer tous les besoins", "resource": "besoins", "action": "edit", "scope": "all", "category": "besoins"},
    {"code": "besoins.edit.own", "name": "Éditer ses besoins", "resource": "besoins", "action": "edit", "scope": "own", "category": "besoins"},
    {"code": "besoins.delete.all", "name": "Supprimer tous les besoins", "resource": "besoins", "action": "delete", "scope": "all", "category": "besoins"},
    {"code": "besoins.delete.own", "name": "Supprimer ses besoins", "resource": "besoins", "action": "delete", "scope": "own", "category": "besoins"},
    {"code": "besoins.read", "name": "Lire besoins", "resource": "besoins", "action": "read", "scope": "organization", "category": "besoins"},
    {"code": "besoins.create", "name": "Créer besoins", "resource": "besoins", "action": "create", "scope": "organization", "category": "besoins"},
    {"code": "besoins.edit", "name": "Éditer besoins", "resource": "besoins", "action": "edit", "scope": "organization", "category": "besoins"},
    {"code": "besoins.delete", "name": "Supprimer besoins", "resource": "besoins", "action": "delete", "scope": "organization", "category": "besoins"},
    {"code": "besoins.submit", "name": "Soumettre besoins", "resource": "besoins", "action": "submit", "scope": "organization", "category": "besoins"},
    {"code": "besoins.validate", "name": "Valider besoins", "resource": "besoins", "action": "validate", "scope": "organization", "category": "besoins"},
    {"code": "besoins.convert_to_mission", "name": "Convertir en mission", "resource": "besoins", "action": "convert_to_mission", "scope": "organization", "category": "besoins"},
    {"code": "besoins.comment", "name": "Commenter besoins", "resource": "besoins", "action": "comment", "scope": "organization", "category": "besoins"},
    
    # APPLICATIONS
    {"code": "applications.read.all", "name": "Lire toutes les candidatures", "resource": "applications", "action": "read", "scope": "all", "category": "applications"},
    {"code": "applications.read.own", "name": "Lire ses candidatures", "resource": "applications", "action": "read", "scope": "own", "category": "applications"},
    {"code": "applications.create.all", "name": "Créer candidatures (toutes)", "resource": "applications", "action": "create", "scope": "all", "category": "applications"},
    {"code": "applications.create.own", "name": "Créer ses candidatures", "resource": "applications", "action": "create", "scope": "own", "category": "applications"},
    {"code": "applications.update.all", "name": "Mettre à jour toutes les candidatures", "resource": "applications", "action": "update", "scope": "all", "category": "applications"},
    {"code": "applications.update.own", "name": "Mettre à jour ses candidatures", "resource": "applications", "action": "update", "scope": "own", "category": "applications"},
    {"code": "applications.delete.all", "name": "Supprimer toutes les candidatures", "resource": "applications", "action": "delete", "scope": "all", "category": "applications"},
    {"code": "applications.delete.own", "name": "Supprimer ses candidatures", "resource": "applications", "action": "delete", "scope": "own", "category": "applications"},
    {"code": "applications.manage.all", "name": "Gérer toutes les candidatures", "resource": "applications", "action": "manage", "scope": "all", "category": "applications"},
    {"code": "applications.read", "name": "Lire candidatures", "resource": "applications", "action": "read", "scope": "organization", "category": "applications"},
    {"code": "applications.create", "name": "Créer candidatures", "resource": "applications", "action": "create", "scope": "organization", "category": "applications"},
    {"code": "applications.manage", "name": "Gérer candidatures", "resource": "applications", "action": "manage", "scope": "organization", "category": "applications"},
    
    # PROFILE
    {"code": "profile.view.all", "name": "Voir tous les profils", "resource": "profile", "action": "view", "scope": "all", "category": "profile"},
    {"code": "profile.view.own", "name": "Voir son profil", "resource": "profile", "action": "view", "scope": "own", "category": "profile"},
    {"code": "profile.edit.all", "name": "Éditer tous les profils", "resource": "profile", "action": "edit", "scope": "all", "category": "profile"},
    {"code": "profile.edit.own", "name": "Éditer son profil", "resource": "profile", "action": "edit", "scope": "own", "category": "profile"},
    {"code": "profile.manage.all", "name": "Gérer tous les profils", "resource": "profile", "action": "manage", "scope": "all", "category": "profile"},
    {"code": "profile.manage.own", "name": "Gérer son profil", "resource": "profile", "action": "manage", "scope": "own", "category": "profile"},
    {"code": "profile.read", "name": "Lire profils", "resource": "profile", "action": "read", "scope": "organization", "category": "profile"},
    {"code": "profile.manage", "name": "Gérer profils", "resource": "profile", "action": "manage", "scope": "organization", "category": "profile"},
    
    # ENTREPRISES
    {"code": "entreprises.view.all", "name": "Voir toutes les entreprises", "resource": "entreprises", "action": "view", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.view.own", "name": "Voir son entreprise", "resource": "entreprises", "action": "view", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.edit.all", "name": "Éditer toutes les entreprises", "resource": "entreprises", "action": "edit", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.edit.own", "name": "Éditer son entreprise", "resource": "entreprises", "action": "edit", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.read", "name": "Lire entreprises", "resource": "entreprises", "action": "read", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.create", "name": "Créer entreprises", "resource": "entreprises", "action": "create", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.edit", "name": "Éditer entreprises", "resource": "entreprises", "action": "edit", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.delete", "name": "Supprimer entreprises", "resource": "entreprises", "action": "delete", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.validate", "name": "Valider entreprises", "resource": "entreprises", "action": "validate", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.link_existing", "name": "Lier entreprise existante", "resource": "entreprises", "action": "link_existing", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.group_request", "name": "Demander groupe entreprise", "resource": "entreprises", "action": "group_request", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.group_approve", "name": "Approuver groupe entreprise", "resource": "entreprises", "action": "group_approve", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.invite_user", "name": "Inviter utilisateur", "resource": "entreprises", "action": "invite_user", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.manage", "name": "Gérer entreprises", "resource": "entreprises", "action": "manage", "scope": "organization", "category": "entreprises"},
    
    # DOCUMENTS
    {"code": "documents.read.all", "name": "Lire tous les documents", "resource": "documents", "action": "read", "scope": "all", "category": "documents"},
    {"code": "documents.read.own", "name": "Lire ses documents", "resource": "documents", "action": "read", "scope": "own", "category": "documents"},
    {"code": "documents.create.all", "name": "Créer documents (tous)", "resource": "documents", "action": "create", "scope": "all", "category": "documents"},
    {"code": "documents.create.own", "name": "Créer ses documents", "resource": "documents", "action": "create", "scope": "own", "category": "documents"},
    {"code": "documents.update.all", "name": "Mettre à jour tous les documents", "resource": "documents", "action": "update", "scope": "all", "category": "documents"},
    {"code": "documents.update.own", "name": "Mettre à jour ses documents", "resource": "documents", "action": "update", "scope": "own", "category": "documents"},
    {"code": "documents.delete.all", "name": "Supprimer tous les documents", "resource": "documents", "action": "delete", "scope": "all", "category": "documents"},
    {"code": "documents.delete.own", "name": "Supprimer ses documents", "resource": "documents", "action": "delete", "scope": "own", "category": "documents"},
    {"code": "documents.read", "name": "Lire documents", "resource": "documents", "action": "read", "scope": "organization", "category": "documents"},
    {"code": "documents.create", "name": "Créer documents", "resource": "documents", "action": "create", "scope": "organization", "category": "documents"},
    {"code": "documents.update", "name": "Mettre à jour documents", "resource": "documents", "action": "update", "scope": "organization", "category": "documents"},
    {"code": "documents.delete", "name": "Supprimer documents", "resource": "documents", "action": "delete", "scope": "organization", "category": "documents"},
    {"code": "documents.download", "name": "Télécharger documents", "resource": "documents", "action": "download", "scope": "organization", "category": "documents"},
    {"code": "documents.verify", "name": "Vérifier documents", "resource": "documents", "action": "verify", "scope": "organization", "category": "documents"},
    
    # USERS
    {"code": "users.read", "name": "Lire utilisateurs", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "users.create", "name": "Créer utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.update", "name": "Mettre à jour utilisateurs", "resource": "users", "action": "update", "scope": "organization", "category": "users"},
    {"code": "users.edit", "name": "Éditer utilisateurs", "resource": "users", "action": "edit", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "Supprimer utilisateurs", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    {"code": "users.manage", "name": "Gérer utilisateurs", "resource": "users", "action": "manage", "scope": "organization", "category": "users"},
    {"code": "users.manage_status", "name": "Gérer statut utilisateurs", "resource": "users", "action": "manage_status", "scope": "organization", "category": "users"},
    {"code": "users.password.update", "name": "Mettre à jour mot de passe", "resource": "users", "action": "password", "scope": "organization", "category": "users"},
    {"code": "users.reset_mfa", "name": "Réinitialiser MFA", "resource": "users", "action": "reset_mfa", "scope": "organization", "category": "users"},
    
    # CONFIG & FORMS
    {"code": "config.read", "name": "Lire configuration", "resource": "config", "action": "read", "scope": "organization", "category": "config"},
    {"code": "config.manage", "name": "Gérer configuration", "resource": "config", "action": "manage", "scope": "organization", "category": "config"},
    {"code": "forms.read", "name": "Lire formulaires", "resource": "forms", "action": "read", "scope": "organization", "category": "forms"},
    {"code": "forms.manage", "name": "Gérer formulaires", "resource": "forms", "action": "manage", "scope": "organization", "category": "forms"},
    {"code": "forms.enterprise.manage", "name": "Gérer formulaires entreprise", "resource": "forms", "action": "enterprise", "scope": "organization", "category": "forms"},
    {"code": "forms.enterprise.update", "name": "Mettre à jour formulaires entreprise", "resource": "forms", "action": "enterprise", "scope": "organization", "category": "forms"},
    
    # ADMIN
    {"code": "admin.dashboard", "name": "Tableau de bord admin", "resource": "admin", "action": "dashboard", "scope": "organization", "category": "admin"},
    {"code": "admin.access", "name": "Accès admin", "resource": "admin", "action": "access", "scope": "organization", "category": "admin"},
    {"code": "admin.settings", "name": "Paramètres admin", "resource": "admin", "action": "settings", "scope": "organization", "category": "admin"},
    
    # IAM
    {"code": "iam.profiles.read", "name": "Lire profils IAM", "resource": "iam", "action": "profiles", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.manage", "name": "Gérer profils IAM", "resource": "iam", "action": "profiles", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.create", "name": "Créer profils IAM", "resource": "iam", "action": "profiles", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.update", "name": "Mettre à jour profils IAM", "resource": "iam", "action": "profiles", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.delete", "name": "Supprimer profils IAM", "resource": "iam", "action": "profiles", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.read", "name": "Lire groupes IAM", "resource": "iam", "action": "groups", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.manage", "name": "Gérer groupes IAM", "resource": "iam", "action": "groups", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.create", "name": "Créer groupes IAM", "resource": "iam", "action": "groups", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.update", "name": "Mettre à jour groupes IAM", "resource": "iam", "action": "groups", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.delete", "name": "Supprimer groupes IAM", "resource": "iam", "action": "groups", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.read", "name": "Lire permissions IAM", "resource": "iam", "action": "permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.create", "name": "Créer permissions IAM", "resource": "iam", "action": "permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.update", "name": "Mettre à jour permissions IAM", "resource": "iam", "action": "permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.delete", "name": "Supprimer permissions IAM", "resource": "iam", "action": "permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.users.assign", "name": "Assigner utilisateurs IAM", "resource": "iam", "action": "users", "scope": "organization", "category": "iam"},
    {"code": "iam.manage", "name": "Gérer IAM", "resource": "iam", "action": "manage", "scope": "organization", "category": "iam"},
    
    # RBAC
    {"code": "rbac.read_roles", "name": "Lire rôles RBAC", "resource": "rbac", "action": "read_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.read_groups", "name": "Lire groupes RBAC", "resource": "rbac", "action": "read_groups", "scope": "organization", "category": "rbac"},
    {"code": "rbac.read_profiles", "name": "Lire profils RBAC", "resource": "rbac", "action": "read_profiles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.manage_profile_roles", "name": "Gérer rôles de profil", "resource": "rbac", "action": "manage_profile_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.manage_group_roles", "name": "Gérer rôles de groupe", "resource": "rbac", "action": "manage_group_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.assign_profiles", "name": "Assigner profils", "resource": "rbac", "action": "assign_profiles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.assign_groups", "name": "Assigner groupes", "resource": "rbac", "action": "assign_groups", "scope": "organization", "category": "rbac"},
    
    # VALIDATIONS
    {"code": "validations.manage", "name": "Gérer validations", "resource": "validations", "action": "manage", "scope": "organization", "category": "validations"},
    
    # LOCATIONS
    {"code": "locations.manage", "name": "Gérer localisations", "resource": "locations", "action": "manage", "scope": "organization", "category": "locations"},
    
    # REFERENCES
    {"code": "references.manage", "name": "Gérer références", "resource": "references", "action": "manage", "scope": "organization", "category": "references"},
    
    # RULES
    {"code": "rules.manage", "name": "Gérer règles", "resource": "rules", "action": "manage", "scope": "organization", "category": "rules"},
    
    # FLAGS
    {"code": "flags.manage", "name": "Gérer flags", "resource": "flags", "action": "manage", "scope": "organization", "category": "flags"},
    
    # EMAILS
    {"code": "emails.configure", "name": "Configurer emails", "resource": "emails", "action": "configure", "scope": "organization", "category": "emails"},
    {"code": "emails.read_config", "name": "Lire config emails", "resource": "emails", "action": "read_config", "scope": "organization", "category": "emails"},
    {"code": "emails.read_history", "name": "Lire historique emails", "resource": "emails", "action": "read_history", "scope": "organization", "category": "emails"},
    {"code": "emails.manage_templates", "name": "Gérer templates emails", "resource": "emails", "action": "manage_templates", "scope": "organization", "category": "emails"},
    {"code": "emails.test", "name": "Tester emails", "resource": "emails", "action": "test", "scope": "organization", "category": "emails"},
    {"code": "email.settings.read", "name": "Lire paramètres email", "resource": "email", "action": "settings", "scope": "organization", "category": "emails"},
    {"code": "email.settings.manage", "name": "Gérer paramètres email", "resource": "email", "action": "settings", "scope": "organization", "category": "emails"},
    
    # SECURITY
    {"code": "security.email_domains.read", "name": "Lire domaines email", "resource": "security", "action": "email_domains", "scope": "organization", "category": "security"},
    {"code": "security.email_domains.manage", "name": "Gérer domaines email", "resource": "security", "action": "email_domains", "scope": "organization", "category": "security"},
    {"code": "auth.mfa.manage", "name": "Gérer MFA", "resource": "auth", "action": "mfa", "scope": "organization", "category": "security"},
    
    # DASHBOARD
    {"code": "dashboard.access", "name": "Accès tableau de bord", "resource": "dashboard", "action": "access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.customize.own", "name": "Personnaliser son tableau de bord", "resource": "dashboard", "action": "customize", "scope": "own", "category": "dashboard"},
    
    # WILDCARD (SuperAdmin)
    {"code": "*.*", "name": "Toutes les permissions", "resource": "*", "action": "*", "scope": "organization", "category": "system", "is_system": True},
]


async def reset_database(delete_users: bool = False):
    """Réinitialise complètement la base de données IAM"""
    
    print("\n" + "="*80)
    print("🔄 RÉINITIALISATION COMPLÈTE DE LA BASE DE DONNÉES IAM")
    print("="*80 + "\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # ================================================================
        # ÉTAPE 1: Suppression optionnelle des utilisateurs de test
        # ================================================================
        if delete_users:
            print("🗑️  Suppression de tous les utilisateurs de test...")
            result = await db.users.delete_many({})
            print(f"   ✅ {result.deleted_count} utilisateurs supprimés\n")
        
        # ================================================================
        # ÉTAPE 2: Nettoyage des permissions
        # ================================================================
        print("🧹 Nettoyage des permissions invalides...")
        
        # Supprimer toutes les permissions existantes
        result = await db.permissions.delete_many({})
        print(f"   ✅ {result.deleted_count} permissions supprimées\n")
        
        # ================================================================
        # ÉTAPE 3: Création des permissions modernes
        # ================================================================
        print("✨ Création de toutes les permissions modernes...")
        
        permissions_to_insert = []
        for perm_data in ALL_MODERN_PERMISSIONS:
            perm = {
                "id": str(uuid4()),
                "code": perm_data["code"],
                "name": perm_data["name"],
                "description": perm_data.get("description"),
                "resource": perm_data["resource"],
                "action": perm_data["action"],
                "scope": perm_data["scope"],
                "is_system": perm_data.get("is_system", False),
                "category": perm_data["category"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            permissions_to_insert.append(perm)
        
        if permissions_to_insert:
            await db.permissions.insert_many(permissions_to_insert)
            print(f"   ✅ {len(permissions_to_insert)} permissions créées\n")
        
        # ================================================================
        # ÉTAPE 4: Création de l'index unique sur le code
        # ================================================================
        print("🔐 Création de l'index unique sur le champ 'code'...")
        await db.permissions.create_index("code", unique=True)
        print("   ✅ Index créé\n")
        
        # ================================================================
        # ÉTAPE 5: Création du profil SuperAdmin
        # ================================================================
        print("👑 Création du profil SuperAdmin avec toutes les permissions...")
        
        # Récupérer tous les IDs de permissions
        all_permissions = await db.permissions.find({}, {"_id": 0, "id": 1}).to_list(None)
        all_permission_ids = [p["id"] for p in all_permissions]
        
        superadmin_profile_id = str(uuid4())
        superadmin_profile = {
            "id": superadmin_profile_id,
            "code": "super_admin",
            "name": "Super Administrateur",
            "description": "Profil avec tous les droits système",
            "permission_ids": all_permission_ids,
            "capability_bundle_ids": [],
            "is_system_role": True,
            "is_protected": True,
            "priority": 1000,
            "category": "admin",
            "color": "#DC2626",
            "icon": "Shield",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        # Supprimer l'ancien profil super_admin s'il existe
        await db.profiles.delete_many({"code": "super_admin"})
        
        # Insérer le nouveau profil
        await db.profiles.insert_one(superadmin_profile)
        print(f"   ✅ Profil SuperAdmin créé avec {len(all_permission_ids)} permissions\n")
        
        # ================================================================
        # ÉTAPE 6: Création/Réinitialisation du compte superAdmin
        # ================================================================
        print("👤 Création/Réinitialisation du compte superAdmin...")
        
        superadmin_user_id = str(uuid4())
        hashed_password = pwd_context.hash("Awana2025!")
        
        superadmin_user = {
            "id": superadmin_user_id,
            "email": "admin@awana.fr",
            "username": "admin",
            "first_name": "Super",
            "last_name": "Admin",
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": True,
            "role": "super_admin",
            "profile_ids": [superadmin_profile_id],
            "group_ids": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        # Supprimer l'ancien compte admin s'il existe
        await db.users.delete_many({"$or": [{"email": "admin@awana.fr"}, {"username": "admin"}]})
        
        # Insérer le nouveau compte
        await db.users.insert_one(superadmin_user)
        print("   ✅ Compte superAdmin créé\n")
        
        # ================================================================
        # ÉTAPE 7: Statistiques finales
        # ================================================================
        print("📊 Statistiques finales:")
        perm_count = await db.permissions.count_documents({})
        profile_count = await db.profiles.count_documents({})
        user_count = await db.users.count_documents({})
        
        print(f"   - Permissions: {perm_count}")
        print(f"   - Profils: {profile_count}")
        print(f"   - Utilisateurs: {user_count}\n")
        
        print("="*80)
        print("✅ RÉINITIALISATION TERMINÉE AVEC SUCCÈS!")
        print("="*80)
        print("\n🔑 Identifiants SuperAdmin:")
        print("   Email: admin@awana.fr")
        print("   Username: admin")
        print("   Password: Awana2025!")
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
    parser = argparse.ArgumentParser(description="Réinitialisation complète de la base IAM")
    parser.add_argument(
        "--delete-users",
        action="store_true",
        help="Supprimer TOUS les utilisateurs (y compris les comptes de test)"
    )
    
    args = parser.parse_args()
    
    if args.delete_users:
        print("\n⚠️  ATTENTION: Vous allez supprimer TOUS les utilisateurs!")
        confirm = input("Tapez 'OUI' pour confirmer: ")
        if confirm != "OUI":
            print("❌ Opération annulée")
            sys.exit(1)
    
    success = asyncio.run(reset_database(delete_users=args.delete_users))
    sys.exit(0 if success else 1)
