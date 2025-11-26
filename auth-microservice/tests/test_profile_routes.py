import sys
import types
import asyncio
from types import SimpleNamespace

def setup_module_mocks():
    fastapi = types.ModuleType("fastapi")

    class DummyAPIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def post(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def put(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def delete(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    def DummyDepends(arg=None):
        return arg

    class DummyHTTPException(Exception):
        def __init__(self, status_code=None, detail=None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    def DummyUploadFile(*args, **kwargs):
        return None

    def DummyFile(default=None):
        return default

    def DummyForm(default=None):
        return default

    fastapi.APIRouter = DummyAPIRouter
    fastapi.Depends = DummyDepends
    fastapi.HTTPException = DummyHTTPException
    fastapi.UploadFile = DummyUploadFile
    fastapi.File = DummyFile
    fastapi.Form = DummyForm

    motor = types.ModuleType("motor")
    motor_asyncio = types.ModuleType("motor.motor_asyncio")

    class DummyAsyncIOMotorDatabase:
        pass

    motor_asyncio.AsyncIOMotorDatabase = DummyAsyncIOMotorDatabase
    motor.motor_asyncio = motor_asyncio

    awana_auth = types.ModuleType("awana_auth")
    awana_core = types.ModuleType("awana_auth.core")
    awana_dependencies = types.ModuleType("awana_auth.core.dependencies")
    awana_models = types.ModuleType("awana_auth.core.models")
    awana_profile_models = types.ModuleType("awana_auth.core.profile_models")
    awana_services = types.ModuleType("awana_auth.services")
    awana_permission_checker = types.ModuleType("awana_auth.services.permission_checker")
    awana_utils = types.ModuleType("awana_auth.utils")
    awana_config_helpers = types.ModuleType("awana_auth.utils.config_helpers")

    def dummy_dependency():
        raise NotImplementedError

    awana_dependencies.get_current_user = dummy_dependency
    awana_dependencies.get_database = dummy_dependency

    class DummyUser:
        pass

    awana_models.User = DummyUser

    class DummyDocumentUploadResponse:
        def __init__(self, *args, **kwargs):
            pass

    awana_profile_models.DocumentUploadResponse = DummyDocumentUploadResponse

    class DummyPermissionChecker:
        def __init__(self, *args, **kwargs):
            pass

    awana_permission_checker.PermissionChecker = DummyPermissionChecker

    class DummyCfg:
        def get_interim_role(self):
            return "interim_role"

        def get_company_role(self):
            return "company_role"

        def get_candidate_role(self):
            return "candidate_role"

        def get_postulant_role(self):
            return "postulant_role"

        def get_collaborator_role(self):
            return "collaborator_role"

        def get_profile_type(self, profile):
            return f"profile_type_{profile}"

        def get_document_type(self, document_type):
            return f"document_type_{document_type}"

    awana_config_helpers.cfg = DummyCfg()

    sys.modules["fastapi"] = fastapi
    sys.modules["motor"] = motor
    sys.modules["motor.motor_asyncio"] = motor_asyncio
    sys.modules["awana_auth"] = awana_auth
    sys.modules["awana_auth.core"] = awana_core
    sys.modules["awana_auth.core.dependencies"] = awana_dependencies
    sys.modules["awana_auth.core.models"] = awana_models
    sys.modules["awana_auth.core.profile_models"] = awana_profile_models
    sys.modules["awana_auth.services"] = awana_services
    sys.modules["awana_auth.services.permission_checker"] = awana_permission_checker
    sys.modules["awana_auth.utils"] = awana_utils
    sys.modules["awana_auth.utils.config_helpers"] = awana_config_helpers


setup_module_mocks()
sys.path.insert(0, '/workspace/awa-jlcgroup-app-emergent/auth-microservice')

import profile_routes


class FakeCollection:
    def __init__(self):
        self.docs = []

    async def find_one(self, filter_query, projection=None):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                result = doc.copy()
                if projection and projection.get("_id") == 0:
                    result.pop("_id", None)
                return result
        return None

    async def insert_one(self, document):
        self.docs.append(document.copy())

    async def update_one(self, filter_query, update, upsert=False):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                return

        if upsert:
            new_doc = filter_query.copy()
            if "$setOnInsert" in update:
                new_doc.update(update["$setOnInsert"])
            if "$set" in update:
                new_doc.update(update["$set"])
            self.docs.append(new_doc)


class FakeDB:
    def __init__(self):
        self.candidat_profiles = FakeCollection()
        self.interim_profiles = FakeCollection()
        self.company_manager_profiles = FakeCollection()
        self.collaborator_profiles = FakeCollection()


def test_company_profile_creation_sets_completion_fields():
    db = FakeDB()
    user = SimpleNamespace(
        id="user_company_1",
        roles=[profile_routes.COMPANY_ROLE],
        full_name="Alice Manager",
        email="alice@example.com",
        phone_number=None,
        is_verified=True,
    )

    response = asyncio.run(profile_routes.get_my_profile(current_user=user, db=db))
    profile = response["profile"]

    assert response["profile_type"] == profile_routes.PROFILE_TYPE_COMPANY
    assert profile["profile_completion_percentage"] == 0
    assert profile["profile_completed"] is False


def test_collaborator_profile_creation_sets_completion_fields():
    db = FakeDB()
    user = SimpleNamespace(
        id="user_collab_1",
        roles=[profile_routes.COLLABORATOR_ROLE],
        full_name="Bob Collaborator",
        email="bob@example.com",
        phone_number="1234567890",
        is_verified=False,
    )

    response = asyncio.run(profile_routes.get_my_profile(current_user=user, db=db))
    profile = response["profile"]

    assert response["profile_type"] == profile_routes.PROFILE_TYPE_COLLABORATOR
    assert profile["profile_completion_percentage"] == 0
    assert profile["profile_completed"] is False
