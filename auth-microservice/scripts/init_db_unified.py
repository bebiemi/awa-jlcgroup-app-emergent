#!/usr/bin/env python3
"""
Script d'initialisation unifié de la base de données IAM
- Crée toutes les permissions atomiques (182)
- Crée les bundles de permissions (6)
- Crée/Met à jour les profils système avec permissions et bundles appropriés
- Crée le compte super_admin
- Peut supprimer les utilisateurs de test si demandé

Ce script unifie et remplace:
- reset_local_db_with_superadmin.py
- reset_local_db_with_160_permissions.py  
- reset_db_with_permissions_and_bundles.py
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

# ==================== PERMISSIONS ATOMIQUES (182) ====================
# Identiques au script précédent - toutes les 182 permissions
ALL_ATOMIC_PERMISSIONS = [
    # MISSIONS (21)
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
    {"code": "missions.assign", "name": "Assigner une mission", "resource": "missions", "action": "assign", "scope": "organization", "category": "missions"},
    {"code": "missions.validate", "name": "Valider une mission", "resource": "missions", "action": "validate", "scope": "organization", "category": "missions"},
    {"code": "missions.reject", "name": "Rejeter une mission", "resource": "missions", "action": "reject", "scope": "organization", "category": "missions"},
    {"code": "missions.archive", "name": "Archiver une mission", "resource": "missions", "action": "archive", "scope": "organization", "category": "missions"},
    {"code": "missions.publish", "name": "Publier une mission", "resource": "missions", "action": "publish", "scope": "organization", "category": "missions"},
    {"code": "missions.cancel", "name": "Annuler une mission", "resource": "missions", "action": "cancel", "scope": "organization", "category": "missions"},
    
    # BESOINS (21)
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
    {"code": "besoins.comment.all", "name": "Commenter tous les besoins", "resource": "besoins", "action": "comment", "scope": "all", "category": "besoins"},
    {"code": "besoins.read.all", "name": "Lire tous les besoins", "resource": "besoins", "action": "read", "scope": "all", "category": "besoins"},
    {"code": "besoins.read.own", "name": "Lire ses besoins", "resource": "besoins", "action": "read", "scope": "own", "category": "besoins"},
    {"code": "besoins.submit.own", "name": "Soumettre ses besoins", "resource": "besoins", "action": "submit", "scope": "own", "category": "besoins"},
    {"code": "besoins.validate.all", "name": "Valider tous les besoins", "resource": "besoins", "action": "validate", "scope": "all", "category": "besoins"},
    
    # APPLICATIONS (14)
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
    {"code": "applications.edit.own", "name": "Éditer ses candidatures", "resource": "applications", "action": "edit", "scope": "own", "category": "applications"},
    
    # USERS (19)
    {"code": "users.view.all", "name": "Voir tous les utilisateurs", "resource": "users", "action": "view", "scope": "all", "category": "users"},
    {"code": "users.view.own", "name": "Voir son profil utilisateur", "resource": "users", "action": "view", "scope": "own", "category": "users"},
    {"code": "users.create", "name": "Créer utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.edit.own", "name": "Éditer son profil", "resource": "users", "action": "edit", "scope": "own", "category": "users"},
    {"code": "users.edit.all", "name": "Éditer tous les utilisateurs", "resource": "users", "action": "edit", "scope": "all", "category": "users"},
    {"code": "users.delete.all", "name": "Supprimer utilisateurs", "resource": "users", "action": "delete", "scope": "all", "category": "users"},
    {"code": "users.manage", "name": "Gérer utilisateurs", "resource": "users", "action": "manage", "scope": "organization", "category": "users"},
    {"code": "users.manage_status", "name": "Gérer statut utilisateurs", "resource": "users", "action": "manage_status", "scope": "organization", "category": "users"},
    {"code": "users.manage_status.all", "name": "Gérer statut de tous", "resource": "users", "action": "manage_status", "scope": "all", "category": "users"},
    {"code": "users.reset_password", "name": "Réinitialiser mots de passe", "resource": "users", "action": "reset_password", "scope": "organization", "category": "users"},
    {"code": "users.reset_mfa", "name": "Réinitialiser MFA", "resource": "users", "action": "reset_mfa", "scope": "organization", "category": "users"},
    {"code": "users.reset_mfa.all", "name": "Réinitialiser MFA de tous", "resource": "users", "action": "reset_mfa", "scope": "all", "category": "users"},
    {"code": "users.read.all", "name": "Lire tous les utilisateurs", "resource": "users", "action": "read", "scope": "all", "category": "users"},
    {"code": "users.block", "name": "Bloquer un utilisateur", "resource": "users", "action": "block", "scope": "organization", "category": "users"},
    {"code": "users.unblock", "name": "Débloquer un utilisateur", "resource": "users", "action": "unblock", "scope": "organization", "category": "users"},
    {"code": "users.archive", "name": "Archiver un utilisateur", "resource": "users", "action": "archive", "scope": "organization", "category": "users"},
    {"code": "users.restore", "name": "Restaurer un utilisateur", "resource": "users", "action": "restore", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "Suppression logique", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    {"code": "users.delete_hard", "name": "Suppression définitive", "resource": "users", "action": "delete_hard", "scope": "organization", "category": "users"},
    
    # PROFILE (12)
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
    {"code": "profile.read.all", "name": "Lire tous les profils", "resource": "profile", "action": "read", "scope": "all", "category": "profile"},
    {"code": "profile.read.own", "name": "Lire son profil", "resource": "profile", "action": "read", "scope": "own", "category": "profile"},
    
    # ENTREPRISES (16)
    {"code": "entreprises.view.all", "name": "Voir toutes les entreprises", "resource": "entreprises", "action": "view", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.view.own", "name": "Voir son entreprise", "resource": "entreprises", "action": "view", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.edit.all", "name": "Éditer toutes les entreprises", "resource": "entreprises", "action": "edit", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.edit.own", "name": "Éditer son entreprise", "resource": "entreprises", "action": "edit", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.read", "name": "Lire entreprises", "resource": "entreprises", "action": "read", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.read.all", "name": "Lire toutes les entreprises", "resource": "entreprises", "action": "read", "scope": "all", "category": "entreprises"},
    {"code": "entreprises.create", "name": "Créer entreprises", "resource": "entreprises", "action": "create", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.create.own", "name": "Créer son entreprise", "resource": "entreprises", "action": "create", "scope": "own", "category": "entreprises"},
    {"code": "entreprises.edit", "name": "Éditer entreprises", "resource": "entreprises", "action": "edit", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.delete", "name": "Supprimer entreprises", "resource": "entreprises", "action": "delete", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.manage", "name": "Gérer entreprises", "resource": "entreprises", "action": "manage", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.validate", "name": "Valider entreprises", "resource": "entreprises", "action": "validate", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.approve", "name": "Approuver entreprises", "resource": "entreprises", "action": "approve", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.grouping.manage", "name": "Gérer regroupement entreprises", "resource": "entreprises", "action": "grouping.manage", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.grouping.approve", "name": "Approuver regroupement", "resource": "entreprises", "action": "grouping.approve", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.grouping.reject", "name": "Rejeter regroupement", "resource": "entreprises", "action": "grouping.reject", "scope": "organization", "category": "entreprises"},
    
    # DOCUMENTS (15)
    {"code": "documents.read", "name": "Lire documents", "resource": "documents", "action": "read", "scope": "organization", "category": "documents"},
    {"code": "documents.create", "name": "Créer documents", "resource": "documents", "action": "create", "scope": "organization", "category": "documents"},
    {"code": "documents.edit", "name": "Éditer documents", "resource": "documents", "action": "edit", "scope": "organization", "category": "documents"},
    {"code": "documents.delete", "name": "Supprimer documents", "resource": "documents", "action": "delete", "scope": "organization", "category": "documents"},
    {"code": "documents.manage", "name": "Gérer documents", "resource": "documents", "action": "manage", "scope": "organization", "category": "documents"},
    {"code": "documents.download", "name": "Télécharger documents", "resource": "documents", "action": "download", "scope": "organization", "category": "documents"},
    {"code": "documents.approve", "name": "Approuver documents", "resource": "documents", "action": "approve", "scope": "organization", "category": "documents"},
    {"code": "documents.reject", "name": "Rejeter documents", "resource": "documents", "action": "reject", "scope": "organization", "category": "documents"},
    {"code": "documents.view_cv.own", "name": "Voir son CV", "resource": "documents", "action": "view_cv", "scope": "own", "category": "documents"},
    {"code": "documents.view_cv.all", "name": "Voir tous les CV", "resource": "documents", "action": "view_cv", "scope": "all", "category": "documents"},
    {"code": "documents.upload_cv.own", "name": "Téléverser son CV", "resource": "documents", "action": "upload_cv", "scope": "own", "category": "documents"},
    {"code": "documents.view_contracts.all", "name": "Voir tous les contrats", "resource": "documents", "action": "view_contracts", "scope": "all", "category": "documents"},
    {"code": "documents.view_contracts.own", "name": "Voir ses contrats", "resource": "documents", "action": "view_contracts", "scope": "own", "category": "documents"},
    {"code": "documents.upload_contracts.all", "name": "Téléverser tous les contrats", "resource": "documents", "action": "upload_contracts", "scope": "all", "category": "documents"},
    {"code": "documents.upload_contracts.own", "name": "Téléverser ses contrats", "resource": "documents", "action": "upload_contracts", "scope": "own", "category": "documents"},
    
    # IAM (18)
    {"code": "iam.permissions.read", "name": "Lire permissions IAM", "resource": "iam", "action": "permissions.read", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.create", "name": "Créer permissions IAM", "resource": "iam", "action": "permissions.create", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.edit", "name": "Éditer permissions IAM", "resource": "iam", "action": "permissions.edit", "scope": "organization", "category": "iam"},
    {"code": "iam.permissions.delete", "name": "Supprimer permissions IAM", "resource": "iam", "action": "permissions.delete", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.read", "name": "Lire profils IAM", "resource": "iam", "action": "profiles.read", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.create", "name": "Créer profils IAM", "resource": "iam", "action": "profiles.create", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.edit", "name": "Éditer profils IAM", "resource": "iam", "action": "profiles.edit", "scope": "organization", "category": "iam"},
    {"code": "iam.profiles.delete", "name": "Supprimer profils IAM", "resource": "iam", "action": "profiles.delete", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.read", "name": "Lire groupes IAM", "resource": "iam", "action": "groups.read", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.create", "name": "Créer groupes IAM", "resource": "iam", "action": "groups.create", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.edit", "name": "Éditer groupes IAM", "resource": "iam", "action": "groups.edit", "scope": "organization", "category": "iam"},
    {"code": "iam.groups.delete", "name": "Supprimer groupes IAM", "resource": "iam", "action": "groups.delete", "scope": "organization", "category": "iam"},
    {"code": "iam.manage", "name": "Gérer IAM", "resource": "iam", "action": "manage", "scope": "organization", "category": "iam"},
    {"code": "iam.assign_permissions", "name": "Assigner permissions", "resource": "iam", "action": "assign_permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.revoke_permissions", "name": "Révoquer permissions", "resource": "iam", "action": "revoke_permissions", "scope": "organization", "category": "iam"},
    {"code": "iam.audit", "name": "Auditer IAM", "resource": "iam", "action": "audit", "scope": "organization", "category": "iam"},
    {"code": "iam.access_control.read", "name": "Lire contrôle d'accès", "resource": "iam", "action": "access_control.read", "scope": "organization", "category": "iam"},
    {"code": "iam.access_control.manage", "name": "Gérer contrôle d'accès", "resource": "iam", "action": "access_control.manage", "scope": "organization", "category": "iam"},
    
    # RBAC (7)
    {"code": "rbac.roles.read", "name": "Lire rôles", "resource": "rbac", "action": "roles.read", "scope": "organization", "category": "rbac"},
    {"code": "rbac.roles.create", "name": "Créer rôles", "resource": "rbac", "action": "roles.create", "scope": "organization", "category": "rbac"},
    {"code": "rbac.roles.edit", "name": "Éditer rôles", "resource": "rbac", "action": "roles.edit", "scope": "organization", "category": "rbac"},
    {"code": "rbac.roles.delete", "name": "Supprimer rôles", "resource": "rbac", "action": "roles.delete", "scope": "organization", "category": "rbac"},
    {"code": "rbac.assign_roles", "name": "Assigner rôles", "resource": "rbac", "action": "assign_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.revoke_roles", "name": "Révoquer rôles", "resource": "rbac", "action": "revoke_roles", "scope": "organization", "category": "rbac"},
    {"code": "rbac.manage", "name": "Gérer RBAC", "resource": "rbac", "action": "manage", "scope": "organization", "category": "rbac"},
    
    # CONFIG (5)
    {"code": "config.read", "name": "Lire configuration", "resource": "config", "action": "read", "scope": "organization", "category": "config"},
    {"code": "config.manage", "name": "Gérer configuration", "resource": "config", "action": "manage", "scope": "organization", "category": "config"},
    {"code": "config.update", "name": "Mettre à jour configuration", "resource": "config", "action": "update", "scope": "organization", "category": "config"},
    {"code": "config.feature_flags", "name": "Gérer feature flags", "resource": "config", "action": "feature_flags", "scope": "organization", "category": "config"},
    {"code": "config.email_templates", "name": "Gérer templates d'email", "resource": "config", "action": "email_templates", "scope": "organization", "category": "config"},
    
    # ADMIN (6)
    {"code": "admin.dashboard", "name": "Dashboard administration", "resource": "admin", "action": "dashboard", "scope": "organization", "category": "admin"},
    {"code": "admin.access", "name": "Accès administration", "resource": "admin", "action": "access", "scope": "organization", "category": "admin"},
    {"code": "admin.settings", "name": "Paramètres administration", "resource": "admin", "action": "settings", "scope": "organization", "category": "admin"},
    {"code": "admin.statistics", "name": "Voir les statistiques", "resource": "admin", "action": "statistics", "scope": "organization", "category": "admin"},
    {"code": "admin.audit_logs", "name": "Consulter les logs d'audit", "resource": "admin", "action": "audit_logs", "scope": "organization", "category": "admin"},
    {"code": "admin.rbac", "name": "Gérer les rôles et permissions (RBAC)", "resource": "admin", "action": "rbac", "scope": "organization", "category": "admin"},
    
    # VALIDATIONS (2)
    {"code": "validations.manage", "name": "Gérer validations", "resource": "validations", "action": "manage", "scope": "organization", "category": "validations"},
    {"code": "validations.manage.all", "name": "Gérer toutes les validations", "resource": "validations", "action": "manage", "scope": "all", "category": "validations"},
    
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
    
    # DASHBOARD (6)
    {"code": "dashboard.access", "name": "Accéder au dashboard", "resource": "dashboard", "action": "access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.customize.own", "name": "Personnaliser son dashboard", "resource": "dashboard", "action": "customize", "scope": "own", "category": "dashboard"},
    {"code": "dashboard.admin.access", "name": "Accès dashboard admin", "resource": "dashboard", "action": "admin.access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.candidat.access", "name": "Accès dashboard candidat", "resource": "dashboard", "action": "candidat.access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.commercial.access", "name": "Accès dashboard commercial", "resource": "dashboard", "action": "commercial.access", "scope": "organization", "category": "dashboard"},
    {"code": "dashboard.company.access", "name": "Accès dashboard entreprise", "resource": "dashboard", "action": "company.access", "scope": "organization", "category": "dashboard"},
    
    # SYSTEM / AUTRES (5)
    {"code": "locations.manage", "name": "Gérer localisations", "resource": "locations", "action": "manage", "scope": "organization", "category": "locations"},
    {"code": "references.manage", "name": "Gérer référentiels", "resource": "references", "action": "manage", "scope": "organization", "category": "references"},
    {"code": "rules.manage", "name": "Gérer règles métier", "resource": "rules", "action": "manage", "scope": "organization", "category": "rules"},
    {"code": "system.feature_flags", "name": "Gérer feature flags", "resource": "system", "action": "feature_flags", "scope": "organization", "category": "system"},
    {"code": "flags.manage", "name": "Gérer flags", "resource": "flags", "action": "manage", "scope": "organization", "category": "flags"},
    
    # PERMISSION WILDCARD SUPERADMIN
    {"code": "*.*", "name": "Toutes les permissions (SuperAdmin)", "resource": "*", "action": "*", "scope": "all", "category": "system"},
]

# ==================== BUNDLES DE PERMISSIONS ====================
PERMISSION_BUNDLES = {
    "users.manage": {
        "name": "Gérer les utilisateurs",
        "description": "Accès complet à la gestion des utilisateurs",
        "category": "users",
        "permissions": [
            "users.view.all", "users.create", "users.edit.all", "users.block",
            "users.unblock", "users.archive", "users.restore", "users.delete",
        ]
    },
    "missions.full_access": {
        "name": "Accès complet aux missions",
        "description": "Tous les droits sur les missions",
        "category": "missions",
        "permissions": [
            "missions.read.all", "missions.create", "missions.update", "missions.assign",
            "missions.validate", "missions.reject", "missions.archive", "missions.publish", "missions.cancel",
        ]
    },
    "config.manage": {
        "name": "Gérer la configuration",
        "description": "Gestion complète de la configuration système",
        "category": "config",
        "permissions": [
            "config.read", "config.update", "config.feature_flags", "config.email_templates",
        ]
    },
    "admin.access": {
        "name": "Accès administration",
        "description": "Accès complet aux fonctionnalités d'administration",
        "category": "admin",
        "permissions": [
            "admin.dashboard", "admin.statistics", "admin.audit_logs", "admin.rbac",
        ]
    },
    "entreprises.manage": {
        "name": "Gérer les entreprises",
        "description": "Gestion complète des entreprises",
        "category": "entreprises",
        "permissions": [
            "entreprises.view.all", "entreprises.create", "entreprises.edit.all",
            "entreprises.delete", "entreprises.validate", "entreprises.approve",
        ]
    },
    "iam.full_access": {
        "name": "Accès complet IAM",
        "description": "Gestion complète des permissions, profils et groupes",
        "category": "iam",
        "permissions": [
            "iam.permissions.read", "iam.permissions.create", "iam.permissions.edit", "iam.permissions.delete",
            "iam.profiles.read", "iam.profiles.create", "iam.profiles.edit", "iam.profiles.delete",
            "iam.groups.read", "iam.groups.create", "iam.groups.edit", "iam.groups.delete",
            "iam.assign_permissions", "iam.revoke_permissions", "iam.audit",
        ]
    },
}

# ==================== PROFILS SYSTÈME ====================
SYSTEM_PROFILES = {
    "super_admin": {
        "name": "Super Administrateur",
        "description": "Accès complet à toutes les fonctionnalités",
        "permissions": "*",  # Toutes les permissions
        "bundles": [],
        "priority": 1000,
        "is_protected": True,
    },
    "admin": {
        "name": "Administrateur",
        "description": "Administrateur avec accès étendu",
        "permissions": [],  # Sera rempli par les bundles
        "bundles": ["users.manage", "missions.full_access", "config.manage", "admin.access", "entreprises.manage"],
        "priority": 900,
        "is_protected": True,
    },
    "commercial": {
        "name": "Commercial",
        "description": "Gestion des missions et entreprises",
        "permissions": [],
        "bundles": ["missions.full_access", "entreprises.manage"],
        "priority": 500,
        "is_protected": False,
    },
    "company_admin": {
        "name": "Admin Société",
        "description": "Admin d'une société cliente",
        "permissions": [
            "missions.read.all", "entreprises.view.own", "entreprises.edit.own",
            "applications.read.all", "dashboard.company.access",
        ],
        "bundles": [],
        "priority": 400,
        "is_protected": False,
    },
    "interim_user": {
        "name": "Intérimaire",
        "description": "Utilisateur intérimaire/candidat",
        "permissions": [
            "missions.read", "applications.create.own", "applications.read.own",
            "applications.edit.own", "profile.view.own", "profile.edit.own",
            "dashboard.candidat.access", "documents.view_cv.own", "documents.upload_cv.own",
        ],
        "bundles": [],
        "priority": 100,
        "is_protected": False,
    },
    "hr_manager": {
        "name": "Responsable RH",
        "description": "Gestion RH et candidatures",
        "permissions": [
            "users.view.all", "users.create", "applications.read.all", "applications.manage.all",
            "missions.read.all", "dashboard.admin.access",
        ],
        "bundles": [],
        "priority": 600,
        "is_protected": False,
    },
    "read_only": {
        "name": "Lecture Seule",
        "description": "Accès en lecture uniquement",
        "permissions": [
            "missions.read", "users.view.own", "profile.view.own",
            "dashboard.access",
        ],
        "bundles": [],
        "priority": 50,
        "is_protected": False,
    },
}


async def initialize_database_unified(delete_users=False):
    """Initialisation complète et unifiée de la base de données IAM"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 80)
    print(f"🔄 INITIALISATION UNIFIÉE IAM ({DB_NAME})")
    print("=" * 80)
    
    # 1. Nettoyer les permissions existantes
    print("\n1️⃣ Nettoyage des permissions existantes...")
    result = await db.permissions.delete_many({})
    print(f"   ✅ {result.deleted_count} permissions supprimées")
    
    # 2. Créer les permissions atomiques
    print(f"\n2️⃣ Création des permissions atomiques ({len(ALL_ATOMIC_PERMISSIONS)})...")
    
    permissions_to_insert = []
    for perm in ALL_ATOMIC_PERMISSIONS:
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
            "is_atomic": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    
    if permissions_to_insert:
        result = await db.permissions.insert_many(permissions_to_insert)
        print(f"   ✅ {len(result.inserted_ids)} permissions atomiques créées")
    
    # 3. Créer les bundles
    print(f"\n3️⃣ Création des bundles de permissions ({len(PERMISSION_BUNDLES)})...")
    
    await db.permission_bundles.delete_many({})
    
    bundles_to_insert = []
    for bundle_code, bundle_data in PERMISSION_BUNDLES.items():
        bundles_to_insert.append({
            "id": str(uuid4()),
            "code": bundle_code,
            "name": bundle_data["name"],
            "description": bundle_data["description"],
            "category": bundle_data["category"],
            "permissions": bundle_data["permissions"],
            "is_system": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    
    if bundles_to_insert:
        result = await db.permission_bundles.insert_many(bundles_to_insert)
        print(f"   ✅ {len(result.inserted_ids)} bundles créés")
    
    # 4. Créer/Mettre à jour les profils système
    print(f"\n4️⃣ Création/Mise à jour des profils système ({len(SYSTEM_PROFILES)})...")
    
    all_permission_codes = [p["code"] for p in ALL_ATOMIC_PERMISSIONS]
    
    for profile_code, profile_data in SYSTEM_PROFILES.items():
        # Résoudre les permissions du profil
        if profile_data["permissions"] == "*":
            # Super Admin: toutes les permissions
            profile_permissions = all_permission_codes
        else:
            profile_permissions = profile_data["permissions"].copy()
            
            # Ajouter les permissions des bundles
            for bundle_code in profile_data["bundles"]:
                if bundle_code in PERMISSION_BUNDLES:
                    profile_permissions.extend(PERMISSION_BUNDLES[bundle_code]["permissions"])
        
        # Supprimer les doublons
        profile_permissions = list(set(profile_permissions))
        
        profile_doc = {
            "id": str(uuid4()),
            "code": profile_code,
            "name": profile_data["name"],
            "description": profile_data["description"],
            "permissions": profile_permissions,
            "bundles": profile_data["bundles"],
            "is_protected": profile_data["is_protected"],
            "is_system_role": True,
            "priority": profile_data["priority"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert (update or insert)
        await db.profiles.update_one(
            {"code": profile_code},
            {"$set": profile_doc},
            upsert=True
        )
        
        bundle_info = f" + {len(profile_data['bundles'])} bundles" if profile_data['bundles'] else ""
        print(f"   ✅ {profile_code}: {len(profile_permissions)} permissions{bundle_info}")
    
    # 5. Créer les index
    print("\n5️⃣ Création des index...")
    try:
        await db.permissions.create_index([("code", 1)], unique=True, sparse=True)
        await db.permission_bundles.create_index([("code", 1)], unique=True)
        await db.profiles.create_index([("code", 1)], unique=True)
        print("   ✅ Index créés")
    except Exception as e:
        print(f"   ℹ️  Index déjà existants")
    
    # 6. Créer le compte super_admin
    print("\n6️⃣ Création du compte administrateur...")
    
    password = "Awana2025!"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Récupérer l'ID du profil super_admin
    super_admin_profile = await db.profiles.find_one({"code": "super_admin"}, {"id": 1, "_id": 0})
    
    admin_user = {
        "id": str(uuid4()),
        "username": "admin",
        "email": "admin@awana-group.com",
        "first_name": "Admin",
        "last_name": "System",
        "full_name": "Admin System",
        "password_hash": hashed.decode('utf-8'),
        "provider": "local",
        "roles": ["super_admin"],
        "profile_ids": [super_admin_profile["id"]] if super_admin_profile else [],
        "is_active": True,
        "is_verified": True,
        "email_verified": True,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.update_one(
        {"username": "admin"},
        {"$set": admin_user},
        upsert=True
    )
    print("   ✅ Compte 'admin' créé/réinitialisé")
    
    # 7. Corriger les utilisateurs existants (password → password_hash)
    print("\n7️⃣ Correction des utilisateurs existants...")
    result = await db.users.update_many(
        {"password": {"$exists": True}},
        {
            "$rename": {"password": "password_hash"},
            "$set": {"provider": "local", "updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    if result.modified_count > 0:
        print(f"   ✅ {result.modified_count} utilisateur(s) corrigé(s) (password → password_hash)")
    
    # Ajouter provider pour les utilisateurs qui n'en ont pas
    result = await db.users.update_many(
        {"provider": {"$exists": False}},
        {"$set": {"provider": "local"}}
    )
    if result.modified_count > 0:
        print(f"   ✅ {result.modified_count} utilisateur(s) mis à jour (provider ajouté)")
    
    # Activer les comptes super_admin inactifs
    result = await db.users.update_many(
        {
            "roles": "super_admin",
            "$or": [
                {"status": {"$ne": "active"}},
                {"is_active": {"$ne": True}}
            ]
        },
        {
            "$set": {
                "status": "active",
                "is_active": True,
                "is_verified": True,
                "email_verified": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    if result.modified_count > 0:
        print(f"   ✅ {result.modified_count} compte(s) super_admin activé(s)")
    
    # 8. Supprimer les utilisateurs de test si demandé
    if delete_users:
        print("\n8️⃣ Suppression des utilisateurs de test...")
        result = await db.users.delete_many({"username": {"$nin": ["admin", "adminbe"]}})
        print(f"   ✅ {result.deleted_count} utilisateurs supprimés")
    
    # 9. Vérification finale
    print("\n9️⃣ Vérification finale...")
    perm_count = await db.permissions.count_documents({})
    bundle_count = await db.permission_bundles.count_documents({})
    profile_count = await db.profiles.count_documents({"is_system_role": True})
    user_count = await db.users.count_documents({})
    
    print(f"   📊 Permissions atomiques: {perm_count}")
    print(f"   📊 Bundles: {bundle_count}")
    print(f"   📊 Profils système: {profile_count}")
    print(f"   📊 Utilisateurs: {user_count}")
    
    client.close()
    
    # Résumé final
    print("\n" + "=" * 80)
    print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 80)
    print("\n🔑 Identifiants SuperAdmin:")
    print("   Username: admin")
    print("   Email: admin@awana-group.com")
    print("   Password: Awana2025!")
    print(f"\n📊 Système de permissions:")
    print(f"   - {perm_count} permissions atomiques")
    print(f"   - {bundle_count} bundles de permissions")
    print(f"   - {profile_count} profils système avec permissions appropriées")
    print("\n💡 Profils créés/mis à jour:")
    for profile_code, profile_data in SYSTEM_PROFILES.items():
        print(f"   - {profile_code}: {profile_data['name']}")
    print("\n📖 Documentation:")
    print("   - /app/docs/BUNDLE_PERMISSIONS.md")
    print("   - /app/docs/PERMISSIONS_IMPLEMENTATION_STATUS.md")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialisation unifiée de la base IAM")
    parser.add_argument(
        "--delete-users",
        action="store_true",
        help="Supprimer TOUS les utilisateurs (sauf admin/adminbe)"
    )
    
    args = parser.parse_args()
    
    if args.delete_users:
        print("\n⚠️  ATTENTION: Cette option va supprimer TOUS les utilisateurs de test!")
        confirm = input("Tapez 'OUI' pour confirmer: ")
        if confirm != "OUI":
            print("❌ Opération annulée")
            sys.exit(0)
    
    asyncio.run(initialize_database_unified(delete_users=args.delete_users))
