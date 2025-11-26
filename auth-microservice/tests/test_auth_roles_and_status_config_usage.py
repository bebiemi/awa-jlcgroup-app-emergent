import sys
import types
from datetime import datetime, timezone
from pathlib import Path
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

dummy_motor = types.ModuleType("motor")
dummy_motor_asyncio = types.ModuleType("motor.motor_asyncio")


class AsyncIOMotorDatabase:
    pass


class AsyncIOMotorClient:
    def __init__(self, *args, **kwargs):
        self.databases = {}

    def __getitem__(self, name):
        if name not in self.databases:
            self.databases[name] = AsyncIOMotorDatabase()
        return self.databases[name]


dummy_motor_asyncio.AsyncIOMotorDatabase = AsyncIOMotorDatabase
dummy_motor_asyncio.AsyncIOMotorClient = AsyncIOMotorClient
dummy_motor.motor_asyncio = dummy_motor_asyncio

sys.modules.setdefault("motor", dummy_motor)
sys.modules.setdefault("motor.motor_asyncio", dummy_motor_asyncio)

from awana_auth_routes import get_admin_stats, get_all_users  # noqa: E402
from awana_auth.utils.config_helpers import cfg  # noqa: E402


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def skip(self, value):
        self.documents = self.documents[value:]
        return self

    def limit(self, value):
        self.documents = self.documents[:value]
        return self

    async def to_list(self, length=None):
        return list(self.documents)


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = documents or []
        self.updated = []
        self.deleted = []

    def _matches(self, doc, query):
        if not query:
            return True

        for key, value in query.items():
            doc_value = doc.get(key)
            if isinstance(value, dict):
                if "$gte" in value:
                    if doc_value is None or doc_value < value["$gte"]:
                        return False
                elif "$not" in value:
                    elem_match = value.get("$elemMatch", {})
                    if "$in" in elem_match:
                        if any(role in elem_match["$in"] for role in doc.get(key, [])):
                            return False
                elif "$all" in value:
                    if not all(item in doc.get(key, []) for item in value["$all"]):
                        return False
                else:
                    return False
            else:
                if isinstance(doc_value, list):
                    if value not in doc_value:
                        return False
                elif doc_value != value:
                    return False

        return True

    async def count_documents(self, query):
        return len([doc for doc in self.documents if self._matches(doc, query)])

    def find(self, query=None, projection=None):
        matched = [doc.copy() for doc in self.documents if self._matches(doc, query or {})]
        return FakeCursor(matched)

    async def find_one(self, query, projection=None):
        for doc in self.documents:
            if self._matches(doc, query):
                return doc.copy()
        return None

    async def update_one(self, query, update):
        self.updated.append((query, update))

    async def delete_many(self, query):
        self.deleted.append(query)


class FakeDB:
    def __init__(self, users=None, system_references=None):
        self.users = FakeCollection(users)
        self.groups = FakeCollection()
        self.profiles = FakeCollection()
        self.sessions = FakeCollection()
        self.system_references = FakeCollection(system_references)


@pytest.mark.asyncio
async def test_get_admin_stats_counts_configured_roles_and_status(monkeypatch):
    custom_roles = {
        "admin": "manager",
        "super_admin": "root_admin",
        "interim": "temporary_worker",
        "company": "enterprise",
        "agency": "partner_agency",
    }
    suspended_status = "on_hold"

    monkeypatch.setattr(cfg, "get_admin_role", lambda: custom_roles["admin"])
    monkeypatch.setattr(cfg, "get_super_admin_role", lambda: custom_roles["super_admin"])
    monkeypatch.setattr(cfg, "get_interim_role", lambda: custom_roles["interim"])
    monkeypatch.setattr(cfg, "get_company_role", lambda: custom_roles["company"])
    monkeypatch.setattr(cfg, "get_agency_role", lambda: custom_roles["agency"])
    monkeypatch.setattr(cfg, "get_suspended_status", lambda: suspended_status)

    now_iso = datetime.now(timezone.utc).isoformat()

    users = [
        {
            "id": "1",
            "username": "admin-user",
            "email": "admin@example.com",
            "roles": [custom_roles["admin"]],
            "status": cfg.get_active_status(),
            "provider": "local",
            "created_at": now_iso,
            "updated_at": now_iso,
            "last_login_at": now_iso,
        },
        {
            "id": "2",
            "username": "interim-user",
            "email": "interim@example.com",
            "roles": [custom_roles["interim"]],
            "status": cfg.get_active_status(),
            "provider": "local",
            "created_at": now_iso,
            "updated_at": now_iso,
        },
        {
            "id": "3",
            "username": "agency-user",
            "email": "agency@example.com",
            "roles": [custom_roles["agency"]],
            "status": cfg.get_pending_status(),
            "provider": "google",
            "created_at": now_iso,
            "updated_at": now_iso,
        },
        {
            "id": "4",
            "username": "super-user",
            "email": "root@example.com",
            "roles": [custom_roles["super_admin"]],
            "status": suspended_status,
            "provider": "local",
            "created_at": now_iso,
            "updated_at": now_iso,
        },
    ]

    db = FakeDB(users=users)
    current_user = SimpleNamespace(roles=[custom_roles["admin"]])

    result = await get_admin_stats(current_user=current_user, db=db)

    assert result["users_by_role"]["admin"] == 1
    assert result["users_by_role"]["interim"] == 1
    assert result["users_by_role"]["agency"] == 1
    assert result["users_by_role"]["super_admin"] == 1
    assert result["users_by_status"]["suspended"] == 1


@pytest.mark.asyncio
async def test_get_all_users_uses_configured_super_admin(monkeypatch):
    custom_super_admin = "root_admin"
    monkeypatch.setattr(cfg, "get_super_admin_role", lambda: custom_super_admin)

    now_iso = datetime.now(timezone.utc).isoformat()

    users = [
        {
            "id": "1",
            "username": "super",
            "email": "root@example.com",
            "roles": [custom_super_admin],
            "status": cfg.get_active_status(),
            "provider": "local",
            "created_at": now_iso,
            "updated_at": now_iso,
        },
        {
            "id": "2",
            "username": "admin",
            "email": "admin@example.com",
            "roles": [cfg.get_admin_role()],
            "status": cfg.get_active_status(),
            "provider": "local",
            "created_at": now_iso,
            "updated_at": now_iso,
        },
    ]

    hidden_roles = [
        {
            "code": custom_super_admin,
            "category": "roles",
            "is_hidden_from_admins": True,
        }
    ]

    db = FakeDB(users=users, system_references=hidden_roles)
    current_user = SimpleNamespace(roles=[custom_super_admin])

    result = await get_all_users(include_super_admin=True, current_user=current_user, db=db)

    assert len(result) == 2
    assert any(user.email == "root@example.com" for user in result)
