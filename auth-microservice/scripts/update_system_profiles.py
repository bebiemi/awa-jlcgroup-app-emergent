#!/usr/bin/env python3
"""
Mise à jour des profils système IAM pour s'aligner sur les permissions/bundles attendus.
 - Ne supprime rien : ajoute les permissions manquantes et bundles manquants sur les profils système.
 - Utilise MONGO_URL et AUTH_DB_NAME (par défaut mongodb://localhost:27017/, auth_db).
 - Conçu pour les profils : super_admin, admin, commercial, company_admin, interim_user, hr_manager, read_only.
"""

import os
from uuid import uuid4
from datetime import datetime, timezone
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("AUTH_DB_NAME", "auth_db")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Permissions clés à garantir (extraits des notes front/back)
PERMISSIONS_REQUIRED = [
    # Missions / Applications
    "missions.read.all",
    "missions.read.own",
    "missions.create.all",
    "missions.create.own",
    "missions.edit.all",
    "missions.edit.own",
    "missions.delete.all",
    "missions.delete.own",
    "missions.publish.all",
    "missions.manage.all",
    "applications.read.all",
    "applications.manage",
    "applications.manage_status",
    "applications.shortlist",
    "applications.send_to_client",
    "applications.create",
    "applications.create.own",
    # Besoins
    "besoins.read.all",
    "besoins.read.own",
    "besoins.create.all",
    "besoins.create.own",
    "besoins.edit.all",
    "besoins.edit.own",
    "besoins.delete.all",
    "besoins.delete.own",
    "besoins.submit.own",
    "besoins.validate.all",
    # Documents
    "documents.read.all",
    "documents.read.own",
    "documents.create.all",
    "documents.create.own",
    "documents.delete.all",
    "documents.delete.own",
    "documents.download.all",
    "documents.verify.all",
    "documents.view_cv.all",
    # Users / IAM
    "users.read",
    "users.manage",
    "users.manage_status",
    "users.delete",
    "users.import",
    "users.create",
    "users.reset_mfa",
    "users.reset_password",
    "iam.groups.manage",
    "iam.profiles.manage",
    "security.email_domains.read",
    "security.email_domains.manage",
    # Config / Flags / Référentiels / Emails / Rules / Locations
    "flags.read",
    "flags.manage",
    "references.read",
    "references.manage",
    "config.read",
    "config.manage",
    "admin.settings",
    "locations.manage",
    "forms.enterprise.manage",
    "emails.read_config",
    "emails.configure",
    "emails.test",
    "emails.manage_templates",
    "emails.read_history",
    "rules.read",
    "rules.manage",
]

# Bundles à assigner si présents en base (optionnel, non bloquant)
BUNDLES_OPTIONAL = [
    "bundle_documents_admin",
    "bundle_documents_user",
    "bundle_config_admin",
    "bundle_payroll_admin",
    "bundle_payroll_user",
    "bundle_entreprises_grouping",
    "bundle_forms_enterprise_admin",
]

SYSTEM_PROFILES = [
    "super_admin",
    "admin",
    "commercial",
    "candidat",
    "company_admin",
    "interim_user",
    "hr_manager",
    "read_only",
]

def ensure_permission_codes_exist(codes: list[str]):
    now = datetime.now(timezone.utc).isoformat()
    created = 0
    for code in codes:
        if not db.permissions.find_one({"code": code}):
            # Création minimale (category par défaut)
            db.permissions.insert_one({
                "id": str(uuid4()),
                "code": code,
                "name": code,
                "resource": code.split(".")[0],
                "action": ".".join(code.split(".")[1:-1]) or "manage",
                "scope": code.split(".")[-1] if code.count(".") >= 2 else "all",
                "category": code.split(".")[0],
                "description": code,
                "is_system": True,
                "is_atomic": True,
                "created_at": now,
                "updated_at": now,
            })
            created += 1
    return created

def upsert_profile(code: str):
    prof = db.profiles.find_one({"code": code})
    perms = set(PERMISSIONS_REQUIRED)
    existing = set(prof.get("permissions", [])) if prof else set()
    merged = sorted(existing.union(perms))

    # Attacher les bundles optionnels s'ils existent
    bundle_ids = []
    for bundle_code in BUNDLES_OPTIONAL:
        bundle = db.capability_bundles.find_one({"code": bundle_code})
        if bundle:
            bundle_ids.append(bundle["id"])

    update = {
        "$set": {
            "permissions": merged,
            "is_system_role": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    }
    if bundle_ids:
        update["$set"]["capability_bundle_ids"] = bundle_ids

    if prof:
        db.profiles.update_one({"_id": prof["_id"]}, update)
        return False
    else:
        db.profiles.insert_one({
            "id": str(uuid4()),
            "code": code,
            "name": code.replace("_", " ").title(),
            "permissions": merged,
            "capability_bundle_ids": bundle_ids,
            "is_system_role": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        return True

def main():
    created_perms = ensure_permission_codes_exist(PERMISSIONS_REQUIRED)
    print(f"[OK] Permissions créées (si manquantes) : {created_perms}")

    created_profiles = 0
    for profile_code in SYSTEM_PROFILES:
        created = upsert_profile(profile_code)
        if created:
            created_profiles += 1
    print(f"[OK] Profils système créés : {created_profiles} | mis à jour : {len(SYSTEM_PROFILES) - created_profiles}")

if __name__ == "__main__":
    main()
