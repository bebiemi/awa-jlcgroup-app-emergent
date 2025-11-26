"""Mission access permission tests using configuration roles."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mission_routes import router, get_current_user as route_current_user
from awana_auth.core.dependencies import get_database, get_iam_service, get_current_user as get_user_dep
from awana_auth.core.models import User
from awana_auth.core.mission_models import MissionStatus


class DummyPermissionResult:
    def __init__(self, allowed: bool):
        self.has_permission = allowed


class DummyIAMService:
    """Allow everything for mission permissions by default."""

    async def user_has_permission(self, _user_id: str, code: str):
        allowed_codes = {
            "missions.create.all",
            "missions.update.all",
            "missions.read.all",
            "missions.publish",
            "missions.manage",
        }
        return DummyPermissionResult(code in allowed_codes)


class FakeCursor:
    def __init__(self, data):
        self.data = data

    def sort(self, *_args, **_kwargs):
        return self

    def skip(self, _value):
        return self

    def limit(self, _value):
        return self

    async def to_list(self, length=None):
        return self.data[:length] if length else list(self.data)


class FakeCollection:
    def __init__(self):
        self.data = []

    async def find_one(self, query, _projection=None):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                return dict(doc)
        return None

    async def insert_one(self, doc):
        self.data.append(dict(doc))
        return doc

    async def update_one(self, query, update):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$inc" in update:
                    for key, value in update["$inc"].items():
                        doc[key] = doc.get(key, 0) + value
                return doc
        return None

    def find(self, query, _projection=None):
        filtered = [doc for doc in self.data if all(doc.get(k) == v for k, v in query.items())]
        return FakeCursor(filtered)

    async def count_documents(self, query):
        return len([doc for doc in self.data if all(doc.get(k) == v for k, v in query.items())])


class FakeSystemReferences(FakeCollection):
    async def find_one(self, query, _projection=None):
        if query.get("category") == "contract_types":
            return {"code": query.get("code"), "is_active": True}
        return await super().find_one(query, _projection)


class FakeDB:
    def __init__(self):
        self.missions = FakeCollection()
        self.system_references = FakeSystemReferences()
        self.applications = FakeCollection()


def build_app(fake_db: FakeDB, test_user: User):
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        return fake_db

    async def override_user_dep():
        return test_user

    async def override_current_user():
        return {
            "id": test_user.id,
            "sub": test_user.id,
            "email": test_user.email,
            "roles": test_user.roles,
            "full_name": test_user.full_name,
            "company_id": getattr(test_user, "company_id", None),
        }

    app.dependency_overrides[get_database] = override_db
    app.dependency_overrides[get_iam_service] = lambda: DummyIAMService()
    app.dependency_overrides[get_user_dep] = override_user_dep
    app.dependency_overrides[route_current_user] = override_current_user
    return app


def sample_mission_payload(user: User):
    return {
        "title": "Mission de test",
        "description": "Une mission",
        "company_id": user.company_id,
        "job_type": "dev",
        "required_skills": ["python"],
        "experience_required": "1 an",
        "location": "Paris",
        "contract_type": "cdd",
        "created_by": user.id,
    }


@pytest.mark.parametrize("role", ["admin", "super_admin", "company", "commercial"])
def test_create_mission_allowed_roles(role):
    fake_db = FakeDB()
    user = User(id=f"user-{role}", email="user@example.com", full_name="User", roles=[role], company_id="comp-1")
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.post("/api/missions", json=sample_mission_payload(user))

    assert response.status_code == 201
    assert response.json()["status"] == MissionStatus.DRAFT


def test_create_mission_denied_for_interim():
    fake_db = FakeDB()
    user = User(id="user-interim", email="user@example.com", full_name="User", roles=["interim"], company_id="comp-1")
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.post("/api/missions", json=sample_mission_payload(user))

    assert response.status_code == 403
    assert "rôle" in response.json()["detail"].lower()


@pytest.mark.parametrize("role", ["admin", "super_admin", "commercial"])
def test_publish_mission_allowed_roles(role, monkeypatch):
    fake_db = FakeDB()
    mission_id = "mission-123"
    fake_db.missions.data.append({"id": mission_id, "status": MissionStatus.DRAFT})
    user = User(id=f"user-{role}", email="user@example.com", full_name="User", roles=[role], company_id="comp-1")
    app = build_app(fake_db, user)

    async def allow_permissions(self, *_args, **_kwargs):
        return True

    monkeypatch.setattr("mission_routes.PermissionChecker.user_has_any_permission", allow_permissions)
    client = TestClient(app)

    response = client.post(f"/api/missions/{mission_id}/publish")

    assert response.status_code == 200
    assert response.json()["status"] == MissionStatus.PUBLISHED


def test_publish_mission_denied_for_interim(monkeypatch):
    fake_db = FakeDB()
    fake_db.missions.data.append({"id": "mission-456", "status": MissionStatus.DRAFT})
    user = User(id="user-interim", email="user@example.com", full_name="User", roles=["interim"], company_id="comp-1")
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.post("/api/missions/mission-456/publish")

    assert response.status_code == 403


def test_view_all_requires_allowed_role():
    fake_db = FakeDB()
    fake_db.missions.data.append({"id": "mission-789", "status": MissionStatus.PUBLISHED})
    user = User(id="user-interim", email="user@example.com", full_name="User", roles=["interim"], company_id="comp-1")
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.get("/api/missions")

    assert response.status_code == 403


def test_edit_denied_without_role():
    fake_db = FakeDB()
    mission_id = "mission-edit"
    fake_db.missions.data.append({"id": mission_id, "company_id": "comp-1"})
    user = User(id="user-interim", email="user@example.com", full_name="User", roles=["interim"], company_id="comp-1")
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.put(f"/api/missions/{mission_id}", json={"title": "nouveau"})

    assert response.status_code == 403
