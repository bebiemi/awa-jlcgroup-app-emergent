#!/usr/bin/env python3
"""
Seed des nouvelles permissions et bundles IAM (non destructif).
Ne supprime rien : ajoute uniquement les permissions/bundles manquants.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("AUTH_DB_NAME", "auth_db")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


# Permissions à garantir (codes alignés avec les routes FastAPI et le frontend)
PERMISSIONS = [
    # Config / Flags / Notifications / Référentiels
    {"code": "config.read", "resource": "config", "action": "read", "scope": "all", "name": "Lire la configuration", "category": "config"},
    {"code": "config.manage", "resource": "config", "action": "manage", "scope": "all", "name": "Gérer la configuration", "category": "config"},
    {"code": "flags.read", "resource": "flags", "action": "read", "scope": "all", "name": "Lire les feature flags", "category": "feature_flags"},
    {"code": "flags.manage", "resource": "flags", "action": "manage", "scope": "all", "name": "Gérer les feature flags", "category": "feature_flags"},
    {"code": "notifications.read", "resource": "notifications", "action": "read", "scope": "all", "name": "Lire les notifications système", "category": "notifications"},
    {"code": "references.read", "resource": "references", "action": "read", "scope": "all", "name": "Lire les référentiels", "category": "references"},
    {"code": "references.manage", "resource": "references", "action": "manage", "scope": "all", "name": "Gérer les référentiels", "category": "references"},
    # Emails
    {"code": "emails.read_status", "resource": "emails", "action": "read_status", "scope": "all", "name": "Voir le statut des emails", "category": "emails"},
    {"code": "emails.read_history", "resource": "emails", "action": "read_history", "scope": "all", "name": "Voir l'historique des emails", "category": "emails"},
    {"code": "emails.read_config", "resource": "emails", "action": "read_config", "scope": "all", "name": "Voir la configuration des emails", "category": "emails"},
    {"code": "emails.manage_templates", "resource": "emails", "action": "manage_templates", "scope": "all", "name": "Gérer les templates email", "category": "emails"},
    {"code": "emails.configure", "resource": "emails", "action": "configure", "scope": "all", "name": "Configurer le provider email", "category": "emails"},
    {"code": "emails.test", "resource": "emails", "action": "test", "scope": "all", "name": "Tester l'envoi d'email", "category": "emails"},
    # Documents (scopes .own/.all)
    {"code": "documents.create.own", "resource": "documents", "action": "create", "scope": "own", "name": "Uploader ses documents", "category": "documents"},
    {"code": "documents.create.all", "resource": "documents", "action": "create", "scope": "all", "name": "Uploader des documents pour tous", "category": "documents"},
    {"code": "documents.read.own", "resource": "documents", "action": "read", "scope": "own", "name": "Lire ses documents", "category": "documents"},
    {"code": "documents.read.all", "resource": "documents", "action": "read", "scope": "all", "name": "Lire tous les documents", "category": "documents"},
    {"code": "documents.delete.own", "resource": "documents", "action": "delete", "scope": "own", "name": "Supprimer ses documents", "category": "documents"},
    {"code": "documents.delete.all", "resource": "documents", "action": "delete", "scope": "all", "name": "Supprimer tous les documents", "category": "documents"},
    {"code": "documents.download.all", "resource": "documents", "action": "download", "scope": "all", "name": "Télécharger tous les documents", "category": "documents"},
    {"code": "documents.verify.all", "resource": "documents", "action": "verify", "scope": "all", "name": "Vérifier tous les documents", "category": "documents"},
    {"code": "documents.view_cv.all", "resource": "documents", "action": "view_cv", "scope": "all", "name": "Voir tous les CV", "category": "documents"},
    # Besoins (.own/.all alignés avec les routes)
    {"code": "besoins.read.own", "resource": "besoins", "action": "read", "scope": "own", "name": "Lire ses besoins", "category": "besoins"},
    {"code": "besoins.read.all", "resource": "besoins", "action": "read", "scope": "all", "name": "Lire tous les besoins", "category": "besoins"},
    {"code": "besoins.edit.own", "resource": "besoins", "action": "edit", "scope": "own", "name": "Modifier ses besoins", "category": "besoins"},
    {"code": "besoins.edit.all", "resource": "besoins", "action": "edit", "scope": "all", "name": "Modifier tous les besoins", "category": "besoins"},
    {"code": "besoins.submit.own", "resource": "besoins", "action": "submit", "scope": "own", "name": "Soumettre ses besoins", "category": "besoins"},
    {"code": "besoins.validate.all", "resource": "besoins", "action": "validate", "scope": "all", "name": "Valider les besoins", "category": "besoins"},
    {"code": "besoins.comment.all", "resource": "besoins", "action": "comment", "scope": "all", "name": "Commenter les besoins", "category": "besoins"},
    {"code": "besoins.convert_to_mission.all", "resource": "besoins", "action": "convert_to_mission", "scope": "all", "name": "Convertir les besoins en missions", "category": "besoins"},
    # Entreprises (.own/.all alignés avec les routes)
    {"code": "entreprises.read.own", "resource": "entreprises", "action": "read", "scope": "own", "name": "Lire son entreprise", "category": "entreprises"},
    {"code": "entreprises.read.all", "resource": "entreprises", "action": "read", "scope": "all", "name": "Lire toutes les entreprises", "category": "entreprises"},
    {"code": "entreprises.create.own", "resource": "entreprises", "action": "create", "scope": "own", "name": "Créer son entreprise", "category": "entreprises"},
    {"code": "entreprises.edit.own", "resource": "entreprises", "action": "edit", "scope": "own", "name": "Modifier son entreprise", "category": "entreprises"},
    {"code": "entreprises.edit.all", "resource": "entreprises", "action": "edit", "scope": "all", "name": "Modifier toutes les entreprises", "category": "entreprises"},
    {"code": "entreprises.delete.all", "resource": "entreprises", "action": "delete", "scope": "all", "name": "Supprimer des entreprises", "category": "entreprises"},
    # Entreprises (grouping)
    {"code": "entreprises.group_request", "resource": "entreprises", "action": "group_request", "scope": "all", "name": "Demander un regroupement d'entreprises", "category": "entreprises"},
    {"code": "entreprises.group_approve", "resource": "entreprises", "action": "group_approve", "scope": "all", "name": "Approuver un regroupement d'entreprises", "category": "entreprises"},
    # Formulaires entreprise
    {"code": "forms.enterprise.read", "resource": "forms.enterprise", "action": "read", "scope": "all", "name": "Lire la config formulaire entreprise", "category": "forms"},
    {"code": "forms.enterprise.manage", "resource": "forms.enterprise", "action": "manage", "scope": "all", "name": "Gérer la config formulaire entreprise", "category": "forms"},
    {"code": "forms.enterprise.update", "resource": "forms.enterprise", "action": "update", "scope": "all", "name": "Mettre à jour la config formulaire entreprise", "category": "forms"},
    # Payroll
    {"code": "payroll.timesheets.read", "resource": "payroll.timesheets", "action": "read", "scope": "own", "name": "Lire ses feuilles de temps", "category": "payroll"},
    {"code": "payroll.timesheets.read.all", "resource": "payroll.timesheets", "action": "read", "scope": "all", "name": "Lire toutes les feuilles de temps", "category": "payroll"},
    {"code": "payroll.timesheets.submit", "resource": "payroll.timesheets", "action": "submit", "scope": "own", "name": "Soumettre ses feuilles de temps", "category": "payroll"},
    {"code": "payroll.timesheets.validate", "resource": "payroll.timesheets", "action": "validate", "scope": "all", "name": "Valider les feuilles de temps", "category": "payroll"},
    {"code": "payroll.slips.request", "resource": "payroll.slips", "action": "request", "scope": "own", "name": "Demander ses fiches de paie", "category": "payroll"},
    {"code": "payroll.slips.download", "resource": "payroll.slips", "action": "download", "scope": "all", "name": "Télécharger les fiches de paie", "category": "payroll"},
    {"code": "payroll.data.share", "resource": "payroll.data", "action": "share", "scope": "all", "name": "Partager les données paie avec apps métiers", "category": "payroll"},
    {"code": "payroll.configure", "resource": "payroll", "action": "configure", "scope": "all", "name": "Configurer le module paie", "category": "payroll"},
    {"code": "payroll.audit.read", "resource": "payroll.audit", "action": "read", "scope": "all", "name": "Consulter l'audit paie", "category": "payroll"},
    # Contracts (interim own / admin all)
    {"code": "contracts.read", "resource": "contracts", "action": "read", "scope": "own", "name": "Lire ses contrats", "category": "contracts"},
    {"code": "contracts.read.all", "resource": "contracts", "action": "read", "scope": "all", "name": "Lire tous les contrats", "category": "contracts"},
]


# Bundles à créer ou mettre à jour
BUNDLES = {
    "bundle_config_admin": {
        "name": "Configuration - Admin",
        "description": "Gestion complète de la configuration et des référentiels",
        "category": "config",
        "permissions": [
            "config.read",
            "config.manage",
            "flags.read",
            "flags.manage",
            "notifications.read",
            "references.read",
            "references.manage",
            "emails.read_status",
            "emails.read_history",
            "emails.read_config",
            "emails.manage_templates",
            "emails.configure",
            "emails.test",
        ],
    },
    "bundle_documents_admin": {
        "name": "Documents - Admin",
        "description": "Gestion et vérification des documents",
        "category": "documents",
        "permissions": [
            "documents.create.all",
            "documents.read.all",
            "documents.delete.all",
            "documents.download.all",
            "documents.verify.all",
            "documents.view_cv.all",
        ],
    },
    "bundle_documents_user": {
        "name": "Documents - Utilisateur",
        "description": "Gestion de ses propres documents",
        "category": "documents",
        "permissions": [
            "documents.create.own",
            "documents.read.own",
            "documents.delete.own",
        ],
    },
    "bundle_payroll_admin": {
        "name": "Paie - Admin",
        "description": "Administration du module paie et partage de données",
        "category": "payroll",
        "permissions": [
            "payroll.timesheets.read.all",
            "payroll.timesheets.validate",
            "payroll.slips.download",
            "payroll.data.share",
            "payroll.configure",
            "payroll.audit.read",
        ],
    },
    "bundle_payroll_user": {
        "name": "Paie - Utilisateur",
        "description": "Accès utilisateur aux feuilles de temps et demandes de paie",
        "category": "payroll",
        "permissions": [
            "payroll.timesheets.read",
            "payroll.timesheets.submit",
            "payroll.slips.request",
        ],
    },
    "bundle_entreprises_grouping": {
        "name": "Entreprises - Regroupement",
        "description": "Demande et approbation de regroupements d'entreprises",
        "category": "entreprises",
        "permissions": [
            "entreprises.group_request",
            "entreprises.group_approve",
        ],
    },
    "bundle_forms_enterprise_admin": {
        "name": "Formulaire Entreprise - Admin",
        "description": "Gestion du formulaire dynamique entreprise",
        "category": "forms",
        "permissions": [
            "forms.enterprise.read",
            "forms.enterprise.manage",
            "forms.enterprise.update",
        ],
    },
}


def upsert_permission(perm: dict) -> bool:
    """Insère la permission si absente. Retourne True si créée."""
    exists = db.permissions.find_one({"code": perm["code"]})
    if exists:
        return False
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid4()),
        "code": perm["code"],
        "name": perm["name"],
        "resource": perm["resource"],
        "action": perm["action"],
        "scope": perm.get("scope", "all"),
        "category": perm.get("category", "general"),
        "description": perm.get("description", perm["name"]),
        "is_system": True,
        "is_atomic": True,
        "created_at": now,
        "updated_at": now,
    }
    db.permissions.insert_one(doc)
    return True


def upsert_bundle(code: str, bundle: dict) -> bool:
    """Upsert d'un bundle (remplace les champs name/description/permissions/category)."""
    now = datetime.now(timezone.utc).isoformat()
    result = db.permission_bundles.update_one(
        {"code": code},
        {
            "$set": {
                "code": code,
                "name": bundle["name"],
                "description": bundle["description"],
                "category": bundle.get("category", "general"),
                "permissions": bundle["permissions"],
                "is_system": True,
                "updated_at": now,
            },
            "$setOnInsert": {
                "id": str(uuid4()),
                "created_at": now,
            },
        },
        upsert=True,
    )
    return result.matched_count == 0 and result.upserted_id is not None


def main():
    print(f"Seeding IAM (DB={DB_NAME}) via {MONGO_URL}")
    created_perms = 0
    for perm in PERMISSIONS:
        if upsert_permission(perm):
            created_perms += 1
            print(f"  ✅ Permission créée : {perm['code']}")
        else:
            print(f"  ⏭️  Permission existante : {perm['code']}")

    created_bundles = 0
    for code, bundle in BUNDLES.items():
        if upsert_bundle(code, bundle):
            created_bundles += 1
            print(f"  ✅ Bundle créé : {code}")
        else:
            print(f"  ⏭️  Bundle mis à jour/présent : {code}")

    print("\nRésumé")
    print(f"  Permissions créées : {created_perms}/{len(PERMISSIONS)}")
    print(f"  Bundles créés     : {created_bundles}/{len(BUNDLES)}")
    print("Terminé.")


if __name__ == "__main__":
    main()
