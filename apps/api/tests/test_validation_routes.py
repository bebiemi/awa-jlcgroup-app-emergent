import sys
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.domain.entities.validation import AccountValidation, ValidationStatus, ValidationType
from src.presentation.routes import validation_routes
from src.presentation.dependencies import (
    get_current_user,
    get_database,
    get_validator_roles_from_config,
)
from src.presentation import dependencies


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def make_client(monkeypatch):
    async def _make_client(validation: AccountValidation, roles: list[str]):
        app = FastAPI()
        app.include_router(validation_routes.router, prefix="/api")

        validator_user = {
            "id": "validator-1",
            "email": "validator@example.com",
            "roles": roles,
        }

        # Dependency overrides
        class FakeDB:
            account_validations = object()

        app.dependency_overrides[get_database] = lambda: FakeDB()
        app.dependency_overrides[get_current_user] = lambda: validator_user
        app.dependency_overrides[validation_routes.require_validator] = lambda: validator_user
        app.dependency_overrides[dependencies.require_validator] = lambda: validator_user

        # Configuration override to ensure validator role check uses test roles
        get_validator_roles_from_config.cache_clear()
        monkeypatch.setattr(
            "src.presentation.dependencies.get_validator_roles_from_config",
            lambda: roles,
        )

        # In-memory storage for the validation
        store = {validation.id: validation}

        async def fake_get_by_id(self, validation_id: str):
            return store.get(validation_id)

        async def fake_update(self, validation_obj: AccountValidation):
            validation_obj.updated_at = datetime.utcnow()
            store[validation_obj.id] = validation_obj
            return validation_obj

        class FakeAuditRepository:
            def __init__(self, *_, **__):
                pass

            async def create(self, _):
                return None

        class FakeNotificationRepository:
            def __init__(self, *_, **__):
                pass

            async def create(self, _):
                return None

        class FakeEmailProvider:
            async def send_email(self, *_, **__):
                return None

        monkeypatch.setattr(
            "src.presentation.routes.validation_routes.ValidationRepository.get_by_id",
            fake_get_by_id,
            raising=False,
        )
        monkeypatch.setattr(
            "src.presentation.routes.validation_routes.ValidationRepository.update",
            fake_update,
            raising=False,
        )
        monkeypatch.setattr(
            "src.presentation.routes.validation_routes.AuditRepository",
            FakeAuditRepository,
        )
        monkeypatch.setattr(
            "src.presentation.routes.validation_routes.NotificationRepository",
            FakeNotificationRepository,
        )
        monkeypatch.setattr(
            "src.presentation.routes.validation_routes.get_email_provider",
            lambda: FakeEmailProvider(),
        )

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")
        return client, store, validator_user

    return _make_client


@pytest.mark.anyio
async def test_pending_validation_can_be_approved(monkeypatch, make_client):
    validation = AccountValidation(
        id="validation-1",
        user_id="user-1",
        user_email="user@example.com",
        user_name="Jane Doe",
        validation_type=ValidationType.COMPANY,
        status=ValidationStatus.PENDING,
    )

    client, store, validator = await make_client(validation, roles=["commercial"])

    async with client:
        response = await client.post(
            f"/api/validations/admin/{validation.id}/approve",
            json={"comment": "Looks good"},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == ValidationStatus.APPROVED
    updated_validation = store[validation.id]
    assert updated_validation.status == ValidationStatus.APPROVED
    assert updated_validation.reviewed_by == validator["id"]


@pytest.mark.anyio
async def test_pending_validation_can_be_rejected(monkeypatch, make_client):
    validation = AccountValidation(
        id="validation-2",
        user_id="user-2",
        user_email="user2@example.com",
        user_name="John Smith",
        validation_type=ValidationType.INTERIM,
        status=ValidationStatus.PENDING,
    )

    client, store, validator = await make_client(validation, roles=["admin"])

    async with client:
        response = await client.post(
            f"/api/validations/admin/{validation.id}/reject",
            json={"comment": "Missing documents"},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == ValidationStatus.REJECTED
    updated_validation = store[validation.id]
    assert updated_validation.status == ValidationStatus.REJECTED
    assert updated_validation.reviewed_by == validator["id"]
    assert updated_validation.comment == "Missing documents"


@pytest.mark.anyio
async def test_processed_validation_cannot_transition_again(monkeypatch, make_client):
    validation = AccountValidation(
        id="validation-3",
        user_id="user-3",
        validation_type=ValidationType.COMPANY,
        status=ValidationStatus.APPROVED,
    )

    client, _, _ = await make_client(validation, roles=["super_admin"])

    async with client:
        response = await client.post(
            f"/api/validations/admin/{validation.id}/approve",
            json={},
        )

    assert response.status_code == 400, response.text
    assert "already processed" in response.json().get("detail", "")
