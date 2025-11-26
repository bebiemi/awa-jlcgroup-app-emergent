#!/usr/bin/env python3
"""
Assigner des bundles IAM à un profil (par code).
Non destructif : fusionne les bundles existants avec ceux fournis.

Usage :
  python3 scripts/assign_bundles_to_profile.py --profile-code super_admin --bundles bundle_documents_admin,bundle_config_admin --dry-run
  python3 scripts/assign_bundles_to_profile.py --profile-code manager --bundles bundle_documents_user,bundle_payroll_user

Env attendues :
  - MONGO_URL (par défaut mongodb://localhost:27017/)
  - AUTH_DB_NAME (par défaut auth_db)
"""
import argparse
import os
from datetime import datetime, timezone
from typing import List, Tuple
from pymongo import MongoClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assigner des bundles à un profil IAM")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--profile-code", help="Code du profil cible")
    group.add_argument("--profile-id", help="ID du profil cible")
    parser.add_argument(
        "--bundles",
        required=True,
        help="Liste de codes de bundles séparés par des virgules (ex: bundle_documents_admin,bundle_config_admin)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher les modifications sans les appliquer",
    )
    return parser.parse_args()


def get_db():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    db_name = os.getenv("AUTH_DB_NAME", "auth_db")
    client = MongoClient(mongo_url)
    return client[db_name]


def resolve_bundle_refs(db, bundle_codes: List[str]) -> Tuple[List[str], List[str]]:
    """Retourne (refs_trouvés, codes_introuvables). Refs = id si capability_bundles trouvé, sinon code (permission_bundles)."""
    found_refs = []
    missing = []
    cap_coll = db.capability_bundles
    perm_bundle_coll = db.permission_bundles

    for code in bundle_codes:
        bundle = cap_coll.find_one({"code": code})
        if bundle and bundle.get("id"):
            found_refs.append(bundle["id"])
            continue
        # fallback legacy permission_bundles (codes)
        bundle_legacy = perm_bundle_coll.find_one({"code": code})
        if bundle_legacy:
            found_refs.append(code)  # on conserve le code pour compatibilité
            continue
        missing.append(code)
    return found_refs, missing


def load_profile(db, profile_code: str = None, profile_id: str = None):
    query = {"code": profile_code} if profile_code else {"id": profile_id}
    profile = db.profiles.find_one(query)
    return profile


def main():
    args = parse_args()
    db = get_db()

    profile = load_profile(db, args.profile_code, args.profile_id)
    if not profile:
        raise SystemExit("Profil introuvable (code/id)")

    bundle_codes = [b.strip() for b in args.bundles.split(",") if b.strip()]
    refs, missing = resolve_bundle_refs(db, bundle_codes)

    print(f"Profil cible : {profile.get('code')} ({profile.get('id')})")
    print(f"Bundles demandés : {bundle_codes}")
    print(f"Bundles résolus (id ou code) : {refs}")
    if missing:
        print(f"⚠️ Bundles introuvables : {missing}")

    existing_refs = profile.get("capability_bundle_ids", []) or profile.get("bundles", []) or []
    new_refs = list({*existing_refs, *refs})

    print(f"Bundles existants : {existing_refs}")
    print(f"Bundles après fusion : {new_refs}")

    if args.dry_run:
        print("Dry-run : aucune modification appliquée.")
        return

    result = db.profiles.update_one(
        {"id": profile["id"]},
        {
            "$set": {
                "capability_bundle_ids": new_refs,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        },
    )
    if result.modified_count == 1:
        print("✅ Profil mis à jour avec les bundles.")
    else:
        print("ℹ️ Aucun changement appliqué (profil peut déjà contenir ces bundles).")


if __name__ == "__main__":
    main()
