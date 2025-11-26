from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from awana_auth.core.dependencies import get_database
from awana_auth.core.models import User
from mission_routes import router, get_current_user as route_current_user, get_db


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


class FakeDB:
    def __init__(self):
        self.applications = FakeCollection()
        self.missions = FakeCollection()
        self.system_references = FakeCollection()


def build_app(fake_db: FakeDB, test_user: User):
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        return fake_db

    async def override_current_user():
        return {
            "id": test_user.id,
            "sub": test_user.id,
            "email": test_user.email,
            "roles": test_user.roles,
            "full_name": test_user.full_name,
        }

    app.dependency_overrides[get_database] = override_db
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[route_current_user] = override_current_user
    return app


@pytest.mark.parametrize("role", ["admin", "super_admin", "company", "commercial"])
def test_update_application_allowed_roles(role):
    fake_db = FakeDB()
    application_id = "app-allowed"
    now = datetime.now(timezone.utc)
    fake_db.applications.data.append(
        {
            "id": application_id,
            "mission_id": "mission-1",
            "user_id": "user-1",
            "status": "submitted",
            "created_at": now,
            "updated_at": now,
        }
    )

    user = User(
        id=f"user-{role}",
        username=f"user-{role}",
        email="user@example.com",
        full_name="User",
        roles=[role],
    )
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.put(
        f"/api/missions/applications/{application_id}",
        json={"cover_letter": "updated"},
    )

    assert response.status_code == 200
    assert response.json()["cover_letter"] == "updated"


def test_update_application_denied_for_interim():
    fake_db = FakeDB()
    application_id = "app-denied"
    now = datetime.now(timezone.utc)
    fake_db.applications.data.append(
        {
            "id": application_id,
            "mission_id": "mission-1",
            "user_id": "user-1",
            "status": "submitted",
            "created_at": now,
            "updated_at": now,
        }
    )

    user = User(
        id="user-interim",
        username="user-interim",
        email="user@example.com",
        full_name="User",
        roles=["interim"],
    )
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.put(
        f"/api/missions/applications/{application_id}",
        json={"cover_letter": "updated"},
    )

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
