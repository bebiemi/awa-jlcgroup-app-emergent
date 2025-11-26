"""Tests for profile routes context resolution."""
import os
import sys
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_CONFIG_SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))
_CONFIG_TARGET_DIR = "/app/auth-microservice/config"
os.makedirs(_CONFIG_TARGET_DIR, exist_ok=True)
base_config = os.path.join(_CONFIG_SOURCE_DIR, "base.yaml")
if os.path.exists(base_config):
    shutil.copy(base_config, os.path.join(_CONFIG_TARGET_DIR, "base.yaml"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.core.models import User
from awana_auth.utils.config_helpers import cfg
from profile_routes import profile_router, PROFILE_TYPE_AGENCY_COUNTRY


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

    async def update_one(self, query, update, upsert=False):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$addToSet" in update:
                    for key, value in update["$addToSet"].items():
                        if key not in doc:
                            doc[key] = []
                        if value not in doc[key]:
                            doc[key].append(value)
                return doc

        if upsert:
            new_doc = dict(query)
            if "$setOnInsert" in update:
                new_doc.update(update["$setOnInsert"])
            if "$set" in update:
                new_doc.update(update["$set"])
            self.data.append(new_doc)
            return new_doc
        return None


class FakeDB:
    def __init__(self):
        self.agency_country_profiles = FakeCollection()


def build_app(fake_db: FakeDB, test_user: User):
    app = FastAPI()
    app.include_router(profile_router)

    async def override_db():
        return fake_db

    async def override_current_user():
        return test_user

    app.dependency_overrides[get_database] = override_db
    app.dependency_overrides[get_current_user] = override_current_user
    return app


def test_get_my_profile_returns_agency_context():
    """Ensure agency users receive agency profile collection and type."""
    fake_db = FakeDB()
    agency_role = cfg.get_agency_role()
    user = User(id="user-agency", username="agency", email="agency@example.com", roles=[agency_role])
    app = build_app(fake_db, user)
    client = TestClient(app)

    response = client.get("/profiles/me")

    assert response.status_code == 200
    result = response.json()
    assert result["profile_type"] == PROFILE_TYPE_AGENCY_COUNTRY
    assert result["profile"]["user_id"] == user.id
    assert result["profile"].get("country") == "GABON"
    assert fake_db.agency_country_profiles.data[0]["user_id"] == user.id
