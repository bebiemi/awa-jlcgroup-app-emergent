import sys
from pathlib import Path
import pytest
from types import SimpleNamespace
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

dummy_motor = types.ModuleType("motor")
dummy_motor_asyncio = types.ModuleType("motor.motor_asyncio")
dummy_bcrypt_module = types.ModuleType("bcrypt")


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
dummy_bcrypt_module.hashpw = lambda password, salt: f"hashed:{password.decode('utf-8')}".encode("utf-8")
dummy_bcrypt_module.gensalt = lambda: b"salt"
dummy_bcrypt_module.checkpw = (
    lambda password, hashed: hashed.decode("utf-8") == f"hashed:{password.decode('utf-8')}"
)
sys.modules.setdefault("bcrypt", dummy_bcrypt_module)

from awana_auth_routes import LocalLoginRequest, local_login
from awana_auth.core.config import auth_config
from awana_auth.utils.config_helpers import cfg


class FakeCursor:
    def __init__(self, documents=None):
        self.documents = documents or []

    def __aiter__(self):
        for doc in self.documents:
            yield doc

    async def to_list(self, length=None):
        return list(self.documents)


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = documents or []
        self.updated = []
        self.inserted = []

    def _matches(self, doc, query):
        if not query:
            return True

        if "$or" in query:
            if not any(self._matches(doc, subquery) for subquery in query["$or"]):
                return False

        for key, value in query.items():
            if key == "$or":
                continue

            if isinstance(value, dict) and "$in" in value:
                if doc.get(key) not in value["$in"]:
                    return False
            elif doc.get(key) != value:
                return False
        return True

    async def find_one(self, query, projection=None):
        for doc in self.documents:
            if self._matches(doc, query):
                return doc.copy()
        return None

    async def update_one(self, query, update):
        self.updated.append((query, update))

    async def insert_one(self, document):
        self.inserted.append(document)
        self.documents.append(document)

    def find(self, query=None, projection=None):
        matched = [doc for doc in self.documents if self._matches(doc, query or {})]
        return FakeCursor(matched)

    async def count_documents(self, query):
        return len([doc for doc in self.documents if self._matches(doc, query)])


class FakeDB:
    def __init__(self, users):
        self.users = FakeCollection(users)
        self.profiles = FakeCollection()
        self.permission_bundles = FakeCollection()
        self.capability_bundles = FakeCollection()
        self.permissions = FakeCollection()


class StubSessionStorage:
    async def create_session(self, user, access_token, refresh_token, ip_address, user_agent, metadata):
        return SimpleNamespace(id=f"session-{user.id}")

    async def update_session_tokens(self, session_id, access_token, refresh_token):
        return None


class StubJWTManager:
    async def create_access_token(self, user, session_id):
        return f"access-{user.id}-{session_id}"

    async def create_refresh_token(self, user, session_id):
        return f"refresh-{user.id}-{session_id}"


class StubRBACManager:
    def __init__(self):
        self.granted = []

    async def grant_role(self, user_id, role_name, granted_by=None):
        self.granted.append((user_id, role_name, granted_by))


class NoOpAuditLogger:
    def __init__(self, *args, **kwargs):
        pass

    async def log(self, *args, **kwargs):
        return None


class DummyRequest:
    def __init__(self):
        self.headers = {}
        self.client = SimpleNamespace(host="testclient")


@pytest.fixture(autouse=True)
def patch_audit_logger(monkeypatch):
    monkeypatch.setattr("awana_auth_routes.AuditLogger", NoOpAuditLogger)


@pytest.fixture(autouse=True)
def stub_bcrypt(monkeypatch):
    class DummyBcryptModule:
        @staticmethod
        def hashpw(password, salt):
            return f"hashed:{password.decode('utf-8')}".encode("utf-8")

        @staticmethod
        def gensalt():
            return b"salt"

        @staticmethod
        def checkpw(password, hashed):
            return hashed.decode("utf-8") == f"hashed:{password.decode('utf-8')}"

    monkeypatch.setitem(sys.modules, "bcrypt", DummyBcryptModule)
    return DummyBcryptModule


@pytest.fixture
def hashed_password(stub_bcrypt):
    raw_password = "P@ssw0rd!"
    hashed = stub_bcrypt.hashpw(raw_password.encode("utf-8"), stub_bcrypt.gensalt()).decode("utf-8")
    return raw_password, hashed


def build_request():
    return DummyRequest()


def build_user(username: str, email: str, roles, password_hash: str):
    return {
        "id": f"{username}-id",
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "provider": "local",
        "roles": roles,
        "status": cfg.get_active_status(),
        "mfa_enabled": False,
        "mfa_required": False,
        "profile_ids": [],
        "permissions": [],
    }


@pytest.mark.asyncio
async def test_admin_login_uses_config_role(monkeypatch, hashed_password):
    raw_password, password_hash = hashed_password
    admin_email = "admin@example.com"

    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", raw_password)
    auth_config.admin_emails = [admin_email]

    db = FakeDB([build_user("admin", admin_email, [cfg.get_admin_role()], password_hash)])

    response = await local_login(
        build_request(),
        SimpleNamespace(),
        LocalLoginRequest(username="admin", password=raw_password),
        db=db,
        jwt_manager=StubJWTManager(),
        session_storage=StubSessionStorage(),
        rbac_manager=StubRBACManager(),
    )

    assert response.user.email == admin_email
    assert cfg.get_admin_role() in response.user.roles
    assert response.access_token.startswith("access-")


@pytest.mark.asyncio
async def test_interim_login_with_active_status(monkeypatch, hashed_password):
    raw_password, password_hash = hashed_password
    interim_email = "interim@example.com"
    interim_role = cfg.get_interim_role()

    db = FakeDB([build_user("interim_user", interim_email, [interim_role], password_hash)])
    auth_config.admin_emails = ["admin@example.com"]

    response = await local_login(
        build_request(),
        SimpleNamespace(),
        LocalLoginRequest(username="interim_user", password=raw_password),
        db=db,
        jwt_manager=StubJWTManager(),
        session_storage=StubSessionStorage(),
        rbac_manager=StubRBACManager(),
    )

    assert interim_role in response.user.roles
    assert response.user.status == cfg.get_active_status()
    assert response.access_token.startswith("access-")


@pytest.mark.asyncio
async def test_agency_login_with_active_status(monkeypatch, hashed_password):
    raw_password, password_hash = hashed_password
    agency_email = "agency@example.com"
    agency_role = cfg.get_agency_role()

    db = FakeDB([build_user("agency_user", agency_email, [agency_role], password_hash)])
    auth_config.admin_emails = ["admin@example.com"]

    response = await local_login(
        build_request(),
        SimpleNamespace(),
        LocalLoginRequest(username="agency_user", password=raw_password),
        db=db,
        jwt_manager=StubJWTManager(),
        session_storage=StubSessionStorage(),
        rbac_manager=StubRBACManager(),
    )

    assert agency_role in response.user.roles
    assert response.user.status == cfg.get_active_status()
    assert response.refresh_token.startswith("refresh-")
