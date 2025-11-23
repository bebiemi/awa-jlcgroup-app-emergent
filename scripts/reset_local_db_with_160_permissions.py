#!/usr/bin/env python3
"""
Script de réinitialisation complète de la base de données locale IAM
- Nettoie toutes les permissions invalides
- Crée toutes les 160 permissions modernes (138 de base + 22 supplémentaires)
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
import bcrypt

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "auth_db")

# Toutes les 160 permissions IAM modernes (138 de base + 22 supplémentaires)
ALL_MODERN_PERMISSIONS = [
    # MISSIONS (15)
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
    
    # BESOINS (21 - incluant les 5 supplémentaires)
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
    # +5 supplémentaires
    {"code": "besoins.comment.all", "name": "Commenter tous les besoins", "resource": "besoins", "action": "comment", "scope": "all", "category": "besoins"},
    {"code": "besoins.read.all", "name": "Lire tous les besoins", "resource": "besoins", "action": "read", "scope": "all", "category": "besoins"},
    {"code": "besoins.read.own", "name": "Lire ses besoins", "resource": "besoins", "action": "read", "scope": "own", "category": "besoins"},
    {"code": "besoins.submit.own", "name": "Soumettre ses besoins", "resource": "besoins", "action": "submit", "scope": "own", "category": "besoins"},
    {"code": "besoins.validate.all", "name": "Valider tous les besoins", "resource": "besoins", "action": "validate", "scope": "all", "category": "besoins"},
    
    # APPLICATIONS (13 + 1 supplémentaire = 14)
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
    {"code": "applications.track", "name": "Suivre candidatures", "resource": "applications", "action": "track", "scope": "organization", "category": "applications"},
    # +1 supplémentaire
    {"code": "applications.edit.own", "name": "Éditer ses candidatures", "resource": "applications", "action": "edit", "scope": "own", "category": "applications"},
    
    # PROFILE (10 + 2 supplémentaires = 12)
    {"code": "profile.view.all", "name": "Voir tous les profils", "resource": "profile", "action": "view", "scope": "all", "category": "profile"},
    {"code": "profile.view.own", "name": "Voir son profil", "resource": "profile", "action": "view", "scope": "own", "category": "profile"},
    {"code": "profile.edit.all", "name": "Éditer tous les profils", "resource": "profile", "action": "edit", "scope": "all", "category": "profile"},
    {"code": "profile.edit.own", "name": "Éditer son profil", "resource": "profile", "action": "edit", "scope": "own", "category": "profile"},
    {"code": "profile.manage.all", "name": "Gérer tous les profils", "resource": "profile", "action": "manage", "scope": "all", "category": "profile"},
    {"code": "profile.manage.own", "name": "Gérer son profil", "resource": "profile", "action": "manage", "scope": "own", "category": "profile"},
    {"code": "profile.read", "name": "Lire profils", "resource": "profile", "action": "read", "scope": "organization", "category": "profile"},
    {"code": "profile.manage", "name": "Gérer profils", "resource": "profile", "action": "manage", "scope": "organization", "category": "profile"},
    {"code": "profile.create", "name": "Créer profils", "resource": "profile", "action": "create", "scope": "organization", "category": "profile"},
    {"code": "profile.delete", "name": "Supprimer profils", "resource": "profile", "action": "delete", "scope": "organization", "category": "profile"},
    # +2 supplémentaires
    {"code": "profile.read.all", "name": "Lire tous les profils", "resource": "profile", "action": "read", "scope": "all", "category": "profile"},
    {"code": "profile.read.own", "name": "Lire son profil", "resource": "profile", "action": "read", "scope": "own", "category": "profile"},
    
    # ENTREPRISES (14 + 2 supplémentaires = 16)
    {"code": "entreprises.view.all", "name": "Voir toutes les entreprises", "resource": "entreprises", "action": "view", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.view.own", "name": "Voir son entreprise", "resource": "entreprises", "action": "view", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.edit.all", "name": "Éditer toutes les entreprises", "resource": "entreprises", "action": "edit", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.edit.own", "name": "Éditer son entreprise", "resource": "entreprises", "action": "edit", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.read", "name": "Lire entreprises", "resource": "entreprises", "action": "read", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.create", "name": "Créer entreprises", "resource": "entreprises", "action": "create", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.edit", "name": "Éditer entreprises", "resource": "entreprises", "action": "edit", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.delete", "name": "Supprimer entreprises", "resource": "entreprises", "action": "delete", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.manage", "name": "Gérer entreprises", "resource": "entreprises", "action": "manage", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.validate", "name": "Valider entreprises", "resource": "entreprises", "action": "validate", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.approve", "name": "Approuver entreprises", "resource": "entreprises", "action": "approve", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.grouping.manage", "name": "Gérer regroupement entreprises", "resource": "entreprises", "action": "grouping.manage", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.grouping.approve", "name": "Approuver regroupement", "resource": "entreprises", "action": "grouping.approve", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.grouping.reject", "name": "Rejeter regroupement", "resource": "entreprises", "action": "grouping.reject", "scope": "organization", "category": "entreprises"},
    # +2 supplémentaires
    {"code": "entreprises.create.own", "name": "Créer son entreprise", "resource": "entreprises", "action": "create", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.read.all", "name": "Lire toutes les entreprises", "resource": "entreprises", "action": "read", "scope": "all", "category": "entreprises"},
    
    # DOCUMENTS (14 + 1 supplémentaire = 15)
    {"code": "documents.read", "name": "Lire documents", "resource": "documents", "action": "read", "scope": "organization", "category": "documents"},
    {"code": "documents.create", "name": "Créer documents", "resource": "documents", "action": "create", "scope": "organization", "category": "documents"},
    {"code": "documents.edit", "name": "Éditer documents", "resource": "documents", "action": "edit", "scope": "organization", "category": "documents"},
    {"code": "documents.delete", "name": "Supprimer documents", "resource": "documents", "action": "delete", "scope": "organization", "category": "documents"},
    {"code": "documents.manage", "name": "Gérer documents", "resource": "documents", "action": "manage", "scope": "organization", "category": "documents"},
    {"code": "documents.download", "name": "Télécharger documents", "resource": "documents", "action": "download", "scope": "organization", "category": "documents"},
    {"code": "documents.approve", "name": "Approuver documents", "resource": "documents", "action": "approve", "scope": "organization", "category": "documents"},
    {"code": "documents.reject", "name": "Rejeter documents", "resource": "documents", "action": "reject", "scope": "organization", "category": "documents"},
    {"code": "documents.view_cv.own", "name": "Voir son CV", "resource": "documents", "action": "view_cv", "scope": "own", "category": "documents"},
    {"code": "documents.upload_cv.own", "name": "Téléverser son CV", "resource": "documents", "action": "upload_cv", "scope": "own", "category": "documents"},
    {"code": "documents.view_contracts.all", "name": "Voir tous les contrats", "resource": "documents", "action": "view_contracts", "scope": "all", "category": "documents"},
    {"code": "documents.view_contracts.own", "name": "Voir ses contrats", "resource": "documents", "action": "view_contracts", "scope": "own", "category": "documents"},
    {"code": "documents.upload_contracts.all", "name": "Téléverser tous les contrats", "resource": "documents", "action": "upload_contracts", "scope": "all", "category": "documents"},
    {"code": "documents.upload_contracts.own", "name": "Téléverser ses contrats", "resource": "documents", "action": "upload_contracts", "scope": "own", "category": "documents"},
    # +1 supplémentaire
    {"code": "documents.view_cv.all", "name": "Voir tous les CV", "resource": "documents", "action": "view_cv", "scope": "all", "category": "documents"},
    
    # USERS (9 + 4 supplémentaires = 13)
    {"code": "users.view.all", "name": "Voir tous les utilisateurs", "resource": "users", "action": "view", "scope": "all", "category": "users"},
    {"code": "users.view.own", "name": "Voir son profil utilisateur", "resource": "users", "action": "view", "scope": "own", "category": "users"},
    {"code": "users.create", "name": "Créer utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.edit.own", "name": "Éditer son profil", "resource": "users", "action": "edit", "scope": "own", "category": "users"},
    {"code": "users.delete.all", "name": "Supprimer utilisateurs", "resource": "users", "action": "delete", "scope": "all", "category": "users"},
    {"code": "users.manage", "name": "Gérer utilisateurs", "resource": "users", "action": "manage", "scope": "organization", "category": "users"},
    {"code": "users.manage_status", "name": "Gérer statut utilisateurs", "resource": "users", "action": "manage_status", "scope": "organization", "category": "users"},
    {"code": "users.reset_password", "name": "Réinitialiser mots de passe", "resource": "users", "action": "reset_password", "scope": "organization", "category": "users"},
    {"code": "users.reset_mfa", "name": "Réinitialiser MFA", "resource": "users", "action": "reset_mfa", "scope": "organization", "category": "users"},
    # +4 supplémentaires
    {"code": "users.edit.all", "name": "Éditer tous les utilisateurs", "resource": "users", "action": "edit", "scope": "all", "category": "users"},
    {"code": "users.manage_status.all", "name": "Gérer statut de tous", "resource": "users", "action": "manage_status", "scope": "all", "category": "users"},
    {"code": "users.read.all", "name": "Lire tous les utilisateurs", "resource": "users", "action": "read", "scope": "all", "category": "users"},
    {"code": "users.reset_mfa.all", "name": "Réinitialiser MFA de tous", "resource": "users", "action": "reset_mfa", "scope": "all", "category": "users"},
    
    # IAM (16 + 2 supplémentaires = 18)
    {"code": "iam.permissions.read", "name": "Lire permissions IAM", "resource": "iam", "action": "permissions.read", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.create", "name": "Créer permissions IAM", "resource": "iam", "action": "permissions.create", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.edit", "name": "Éditer permissions IAM", "resource": "iam", "action": "permissions.edit", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.delete", "name": "Supprimer permissions IAM", "resource": "iam", "action": "permissions.delete", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.read", "name": "Lire profils IAM", "resource": "iam", "action": "profiles.read", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.create", "name": "Créer profils IAM", "resource": "iam", "action": "profiles.create", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.delete", "name": "Supprimer profils IAM", "resource": "iam", "action": "profiles.delete", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.read", "name": "Lire groupes IAM", "resource": "iam", "action": "groups.read", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.create", "name": "Créer groupes IAM", "resource": "iam", "action": "groups.create", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.delete", "name": "Supprimer groupes IAM", "resource": "iam", "action": "groups.delete", "scope": "organization", "category": "iam"},
    {"code": "iam.manage", "name": "Gérer IAM", "resource": "iam", "action": "manage", "scope": "organization", "category": "iam"},
    {"code": "iam.assign_permissions", "name": "Assigner permissions", "resource": "iam", "action": "assign_permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.revoke_permissions", "name": "Révoquer permissions", "resource": "iam", "action": "revoke_permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.audit", "name": "Auditer IAM", "resource": "iam", "action": "audit", "scope": "organization", "category": "iam"},
    {"code": "iam.access_control.read", "name": "Lire contrôle d'accès", "resource": "iam", "action": "access_control.read", "scope": "organization", "category": "iam"},
    {"code": "iam.access_control.manage", "name": "Gérer contrôle d'accès", "resource": "iam", "action": "access_control.manage", "scope": "organization", "category": "iam"},
    # +2 supplémentaires
    {"code": "iam.groups.edit", "name": "Éditer groupes IAM", "resource": "iam", "action": "groups.edit", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.edit", "name": "Éditer profils IAM", "resource": "iam", "action": "profiles.edit", "scope": "organization", "category": "iam"},
    
    # RBAC (7)
    {"code": "rbac.roles.read", "name": "Lire rôles", "resource": "rbac", "action": "roles.read", "scope": "organization", "category": "rbac"},
    {"code": "rbac.roles.create", "name": "Créer rôles", "resource": "rbac", "action": "roles.create", "scope": "organization", "category": "rbac"},
    {"code": "rbac.roles.edit", "name": "Éditer rôles", "resource": "rbac", "action": "roles.edit", "scope": "organization", "category": "rbac"},
    {"code": "rbac.roles.delete", "name": "Supprimer rôles", "resource": "rbac", "action": "roles.delete", "scope": "organization", "category": "rbac"},
    {"code": "rbac.assign_roles", "name": "Assigner rôles", "resource": "rbac", "action": "assign_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.revoke_roles", "name": "Révoquer rôles", "resource": "rbac", "action": "revoke_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.manage", "name": "Gérer RBAC", "resource": "rbac", "action": "manage", "scope": "organization", "category": "rbac"},
    
    # VALIDATIONS (1 + 1 supplémentaire = 2)
    {"code": "validations.manage", "name": "Gérer validations", "resource": "validations", "action": "manage", "scope": "organization", "category": "validations"},
    # +1 supplémentaire
    {"code": "validations.manage.all", "name": "Gérer toutes les validations", "resource": "validations", "action": "manage", "scope": "all", "category": "validations"},
    
    # CONFIG (2)
    {"code": "config.read", "name": "Lire configuration", "resource": "config", "action": "read", "scope": "organization", "category": "config"},
    {"code": "config.manage", "name": "Gérer configuration", "resource": "config", "action": "manage", "scope": "organization", "category": "config"},
    
    # FORMS (4)
    {"code": "forms.read", "name": "Lire formulaires", "resource": "forms", "action": "read", "scope": "organization", "category": "forms"},
    {"code": "forms.create", "name": "Créer formulaires", "resource": "forms", "action": "create", "scope": "organization", "category": "forms"},
    {"code": "forms.edit", "name": "Éditer formulaires", "resource": "forms", "action": "edit", "scope": "organization", "category": "forms"},
    {"code": "forms.manage", "name": "Gérer formulaires", "resource": "forms", "action": "manage", "scope": "organization", "category": "forms"},
    
    # EMAILS (7)
    {"code": "emails.send", "name": "Envoyer emails", "resource": "emails", "action": "send", "scope": "organization", "category": "emails"},
    {"code": "emails.view_history", "name": "Voir historique emails", "resource": "emails", "action": "view_history", "scope": "organization", "category": "emails"},
    {"code": "emails.manage_templates", "name": "Gérer templates emails", "resource": "emails", "action": "manage_templates", "scope": "organization", "category": "emails"},
    {"code": "emails.test", "name": "Tester emails", "resource": "emails", "action": "test", "scope": "organization", "category": "emails"},
    {"code": "email.settings.read", "name": "Lire paramètres emails", "resource": "email", "action": "settings.read", "scope": "organization", "category": "emails"},
    {"code": "email.settings.manage", "name": "Gérer paramètres emails", "resource": "email", "action": "settings.manage", "scope": "organization", "category": "emails"},
    {"code": "emails.manage", "name": "Gérer emails", "resource": "emails", "action": "manage", "scope": "organization", "category": "emails"},
    
    # SECURITY (3)
    {"code": "security.email_domains.read", "name": "Lire domaines emails autorisés", "resource": "security", "action": "email_domains.read", "scope": "organization", "category": "security"},
    {"code": "security.email_domains.manage", "name": "Gérer domaines emails", "resource": "security", "action": "email_domains.manage", "scope": "organization", "category": "security"},
    {"code": "auth.mfa.manage", "name": "Gérer MFA", "resource": "auth", "action": "mfa.manage", "scope": "organization", "category": "security"},
    
    # DASHBOARD (2 + 4 supplémentaires = 6)
    {"code": "dashboard.access", "name": "Accéder au dashboard", "resource": "dashboard", "action": "access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.customize.own", "name": "Personnaliser son dashboard", "resource": "dashboard", "action": "customize", "scope": "own", "category": "dashboard"},
    # +4 supplémentaires
    {"code": "dashboard.admin.access", "name": "Accès dashboard admin", "resource": "dashboard", "action": "admin.access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.candidat.access", "name": "Accès dashboard candidat", "resource": "dashboard", "action": "candidat.access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.commercial.access", "name": "Accès dashboard commercial", "resource": "dashboard", "action": "commercial.access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.company.access", "name": "Accès dashboard entreprise", "resource": "dashboard", "action": "company.access", "scope": "organization", "category": "dashboard"},
    
    # ADMIN (3)
    {"code": "admin.dashboard", "name": "Dashboard administration", "resource": "admin", "action": "dashboard", "scope": "organization", "category": "admin"},
    {"code": "admin.access", "name": "Accès administration", "resource": "admin", "action": "access", "scope": "organization", "category": "admin"},
    {"code": "admin.settings", "name": "Paramètres administration", "resource": "admin", "action": "settings", "scope": "organization", "category": "admin"},
    
    # AUTRES PERMISSIONS SYSTEM (5)
    {"code": "locations.manage", "name": "Gérer localisations", "resource": "locations", "action": "manage", "scope": "organization", "category": "locations"},
    {"code": "references.manage", "name": "Gérer référentiels", "resource": "references", "action": "manage", "scope": "organization", "category": "references"},
    {"code": "rules.manage", "name": "Gérer règles métier", "resource": "rules", "action": "manage", "scope": "organization", "category": "rules"},
    {"code": "system.feature_flags", "name": "Gérer feature flags", "resource": "system", "action": "feature_flags", "scope": "organization", "category": "system"},
    {"code": "flags.manage", "name": "Gérer flags", "resource": "flags", "action": "manage", "scope": "organization", "category": "flags"},
    
    # PERMISSION WILDCARD SUPERADMIN
    {"code": "*.*", "name": "Toutes les permissions (SuperAdmin)", "resource": "*", "action": "*", "scope": "all", "category": "system"},
]


async def reset_database(delete_users=False):
    """Réinitialise la base de données IAM"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🔄 RÉINITIALISATION DE LA BASE DE DONNÉES IAM ({DB_NAME})")
    print("=" * 80)
    
    # 1. Supprimer TOUTES les permissions existantes
    print("\n1️⃣ Nettoyage des permissions existantes...")
    result = await db.permissions.delete_many({})
    print(f"   ✅ {result.deleted_count} permissions supprimées")
    
    # 2. Créer les 160 permissions modernes
    print(f"\n2️⃣ Création des 160 permissions modernes...")
    
    permissions_to_insert = []
    for perm in ALL_MODERN_PERMISSIONS:
        permissions_to_insert.append({
            "id": str(uuid4()),
            "code": perm["code"],
            "name": perm["name"],
            "resource": perm["resource"],
            "action": perm["action"],
            "scope": perm.get("scope", "organization"),
            "category": perm.get("category", "general"),
            "description": perm.get("description"),
            "is_system": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    
    if permissions_to_insert:
        result = await db.permissions.insert_many(permissions_to_insert)
        print(f"   ✅ {len(result.inserted_ids)} permissions créées avec succès")
    
    # 3. Créer un index unique sur le code
    print("\n3️⃣ Création de l'index unique sur 'code'...")
    try:
        await db.permissions.create_index([("code", 1)], unique=True)
        print("   ✅ Index unique créé")
    except Exception as e:
        print(f"   ℹ️  Index déjà existant: {e}")
    
    # 4. Créer le profil SuperAdmin
    print("\n4️⃣ Création du profil SuperAdmin...")
    
    # Récupérer tous les codes de permissions
    all_permission_codes = [p["code"] for p in ALL_MODERN_PERMISSIONS]
    
    super_admin_profile = {
        "id": str(uuid4()),
        "code": "super_admin",
        "name": "Super Administrateur",
        "description": "Profil avec tous les droits (160 permissions)",
        "permissions": all_permission_codes,
        "is_protected": True,
        "is_system_role": True,
        "priority": 1000,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Supprimer l'ancien profil super_admin s'il existe
    await db.profiles.delete_many({"code": "super_admin"})
    
    # Créer le nouveau profil
    await db.profiles.insert_one(super_admin_profile)
    print(f"   ✅ Profil SuperAdmin créé avec {len(all_permission_codes)} permissions")
    
    # 5. Créer/Réinitialiser le compte superAdmin
    print("\n5️⃣ Création du compte administrateur...")
    
    # Hash du mot de passe
    password = "Awana2025!"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    admin_user = {
        "id": str(uuid4()),
        "username": "adminbe",
        "email": "adminbe@awana-group.com",
        "first_name": "Admin",
        "last_name": "BE",
        "full_name": "Admin BE",
        "password": hashed.decode('utf-8'),
        "roles": ["super_admin"],
        "profiles": [super_admin_profile["id"]],
        "is_active": True,
        "is_verified": True,
        "email_verified": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Supprimer l'ancien compte adminbe s'il existe
    await db.users.delete_many({"username": "adminbe"})
    
    # Créer le nouveau compte
    await db.users.insert_one(admin_user)
    print("   ✅ Compte adminbe créé/réinitialisé")
    
    # 6. Supprimer les utilisateurs de test si demandé
    if delete_users:
        print("\n6️⃣ Suppression des utilisateurs de test...")
        # Garder seulement adminbe
        result = await db.users.delete_many({"username": {"$ne": "adminbe"}})
        print(f"   ✅ {result.deleted_count} utilisateurs supprimés")
    
    # 7. Vérification finale
    print("\n7️⃣ Vérification finale...")
    perm_count = await db.permissions.count_documents({})
    profile_count = await db.profiles.count_documents({})
    user_count = await db.users.count_documents({})
    
    print(f"   📊 Permissions: {perm_count}")
    print(f"   📊 Profils: {profile_count}")
    print(f"   📊 Utilisateurs: {user_count}")
    
    client.close()
    
    # Résumé final
    print("\n" + "=" * 80)
    print("✅ RÉINITIALISATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 80)
    print("\n🔑 Identifiants SuperAdmin:")
    print("   Email: adminbe@awana-group.com")
    print("   Username: adminbe")
    print("   Password: Awana2025!")
    print("\n📊 Total: 160 permissions modernes créées")
    print("   - 138 permissions de base")
    print("   - 22 permissions supplémentaires avancées")
    print("\n💡 Prochaines étapes:")
    print("   1. Redémarrer votre backend: sudo supervisorctl restart auth-microservice backend")
    print("   2. Se connecter avec le compte adminbe")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Réinitialiser la base IAM avec 160 permissions")
    parser.add_argument(
        "--delete-users",
        action="store_true",
        help="Supprimer TOUS les utilisateurs (sauf adminbe)"
    )
    
    args = parser.parse_args()
    
    if args.delete_users:
        print("\n⚠️  ATTENTION: Cette option va supprimer TOUS les utilisateurs de test!")
        confirm = input("Tapez 'OUI' pour confirmer: ")
        if confirm != "OUI":
            print("❌ Opération annulée")
            sys.exit(0)
    
    asyncio.run(reset_database(delete_users=args.delete_users))
