#!/usr/bin/env python3
"""
Audit rapide des permissions :
- Charge les permissions depuis Mongo ou un export JSON (code/resource/action)
- Scanne le code pour trouver les permissions utilisees
- Compare les deux listes pour detecter les manquants et les permissions non utilisees
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CODE_PATHS = ["apps/web/src", "frontend/src"]
JSON_EXPORT_CANDIDATES = [
    REPO_ROOT / "auth-microservice" / "docs" / "awana_rbac_export_v2.json",
    REPO_ROOT / "auth-microservice" / "docs" / "awana_rbac_export.json",
]
DEFAULT_JSON_EXPORT = next((p for p in JSON_EXPORT_CANDIDATES if p.exists()), JSON_EXPORT_CANDIDATES[0])
CODE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

# Heuristique simple pour filtrer les chaines qui ressemblent a des permissions
ACTION_HINTS = {
    "read",
    "create",
    "update",
    "delete",
    "manage",
    "edit",
    "view",
    "access",
    "approve",
    "reject",
    "publish",
    "import",
    "export",
    "browse",
    "apply",
    "track",
    "assign",
    "configure",
    "test",
    "dashboard",
    "reset",
    "status",
    "password",
    "validate",
    "convert",
    "submit",
    "comment",
    "permissions",
    "profiles",
    "groups",
    "iam",
}

PERMISSION_REGEX = re.compile(r"""['"]([a-zA-Z0-9_*]+(?:\.[a-zA-Z0-9_*]+)+)['"]""")


def load_permissions_from_json(path: Path) -> Dict[str, dict]:
    if not path.exists():
        raise FileNotFoundError(f"Export JSON introuvable: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Le fichier JSON {path} est invalide: {exc}") from exc

    permissions = data.get("permissions", data if isinstance(data, list) else [])
    by_code: Dict[str, dict] = {}
    for perm in permissions:
        code = perm.get("code")
        if not code:
            continue
        by_code[code] = perm
    return by_code


def load_permissions_from_mongo(uri: str, db_name: str, collection: str) -> Dict[str, dict]:
    try:
        from pymongo import MongoClient
    except ImportError as exc:  # pragma: no cover - dependance optionnelle
        raise RuntimeError("pymongo n'est pas installe (pip install pymongo)") from exc

    client = MongoClient(uri)
    db = client[db_name]
    coll = db[collection]
    cursor = coll.find({}, {"_id": 0})
    by_code: Dict[str, dict] = {}
    for perm in cursor:
        code = perm.get("code")
        if not code:
            continue
        by_code[code] = perm
    return by_code


def is_permission_like(code: str, strict: bool) -> bool:
    if not code or len(code) > 80:
        return False
    if code.startswith(("http", "https", "www")):
        return False
    segments = code.split(".")
    if len(segments) < 2:
        return False
    if not strict:
        return True
    return any(seg in ACTION_HINTS for seg in segments)


def scan_permission_codes(paths: Iterable[str], strict: bool) -> Tuple[Dict[str, Set[str]], int]:
    usage: Dict[str, Set[str]] = defaultdict(set)
    files_scanned = 0

    for raw_path in paths:
        base = (REPO_ROOT / raw_path).resolve()
        if not base.exists():
            continue
        for file_path in base.rglob("*"):
            if file_path.suffix not in CODE_EXTENSIONS or not file_path.is_file():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="latin-1", errors="ignore")

            for match in PERMISSION_REGEX.finditer(content):
                code = match.group(1)
                if is_permission_like(code, strict=strict):
                    rel = file_path.relative_to(REPO_ROOT)
                    usage[code].add(str(rel))

            files_scanned += 1

    return usage, files_scanned


def find_missing_fields(permissions: Dict[str, dict]) -> List[Tuple[str, List[str]]]:
    missing: List[Tuple[str, List[str]]] = []
    for code, perm in permissions.items():
        missing_keys = [field for field in ("code", "resource", "action") if not perm.get(field)]
        if missing_keys:
            missing.append((code, missing_keys))
    return missing


def summarize_list(items: List[str], limit: int) -> Tuple[List[str], int]:
    if len(items) <= limit:
        return items, 0
    return items[:limit], len(items) - limit


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifie l'alignement des permissions DB vs. code")
    parser.add_argument(
        "--source",
        choices=["json", "mongo"],
        default="json" if DEFAULT_JSON_EXPORT.exists() else "mongo",
        help="Source des permissions (mongo ou export JSON)",
    )
    parser.add_argument(
        "--json-file",
        type=Path,
        default=DEFAULT_JSON_EXPORT,
        help="Chemin vers l'export JSON des permissions",
    )
    parser.add_argument(
        "--mongo-uri",
        default=os.getenv("MONGO_URL", "mongodb://localhost:27017"),
        help="URI MongoDB (si source=mongo)",
    )
    parser.add_argument(
        "--mongo-db",
        default=os.getenv("MONGO_DB", "auth_db"),
        help="Nom de la base Mongo (si source=mongo)",
    )
    parser.add_argument(
        "--mongo-collection",
        default=os.getenv("MONGO_COLLECTION", "permissions"),
        help="Collection Mongo des permissions",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=DEFAULT_CODE_PATHS,
        help="Dossiers a scanner pour les permissions utilisees",
    )
    parser.add_argument(
        "--loose",
        action="store_true",
        help="Desactive le filtre heuristique (capture toutes les chaines avec des points)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Nombre max d'elements detailles par section",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Code de retour 1 si des permissions manquent ou si des champs DB sont incomplets",
    )
    args = parser.parse_args()

    # 1) Charger les permissions cote base/export
    if args.source == "mongo":
        permissions_db = load_permissions_from_mongo(args.mongo_uri, args.mongo_db, args.mongo_collection)
        source_label = f"Mongo {args.mongo_db}.{args.mongo_collection}"
    else:
        permissions_db = load_permissions_from_json(args.json_file)
        source_label = f"Export JSON {args.json_file}"

    # 2) Scanner le code
    usage_map, files_scanned = scan_permission_codes(args.paths, strict=not args.loose)
    used_codes = set(usage_map.keys())
    db_codes = set(permissions_db.keys())

    missing_in_db = sorted(code for code in used_codes if code not in db_codes)
    unused_in_code = sorted(code for code in db_codes if code not in used_codes)
    missing_fields = find_missing_fields(permissions_db)

    print("\n=== Permissions audit ===")
    print(f"- Source permissions : {source_label} ({len(db_codes)} codes)")
    print(f"- Fichiers scannes   : {files_scanned}")
    print(f"- Permissions trouvees dans le code : {len(used_codes)}")

    if missing_fields:
        print(f"\nATTENTION - Permissions avec champs manquants ({len(missing_fields)}):")
        items, truncated = summarize_list([f"{code} -> {fields}" for code, fields in missing_fields], args.limit)
        for entry in items:
            print(f"  - {entry}")
        if truncated:
            print(f"  ... et {truncated} autres")

    if missing_in_db:
        print(f"\nERREUR - Permissions utilisees mais absentes en base ({len(missing_in_db)}):")
        items, truncated = summarize_list(missing_in_db, args.limit)
        for code in items:
            examples = ", ".join(sorted(usage_map[code])[:3])
            print(f"  - {code} (ex: {examples})")
        if truncated:
            print(f"  ... et {truncated} autres")
    else:
        print("\nOK - Toutes les permissions utilisees existent en base.")

    if unused_in_code:
        print(f"\nINFO - Permissions presentes en base mais non referencees dans le code ({len(unused_in_code)}):")
        items, truncated = summarize_list(unused_in_code, args.limit)
        for code in items:
            print(f"  - {code}")
        if truncated:
            print(f"  ... et {truncated} autres")

    has_errors = bool(missing_in_db or missing_fields)
    if args.fail_on_mismatch and has_errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
