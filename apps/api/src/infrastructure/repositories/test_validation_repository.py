"""Tests for ValidationRepository hydration utilities."""
from datetime import datetime, timezone
import sys
import types

import pytest

motor_asyncio = types.SimpleNamespace(AsyncIOMotorDatabase=object)
sys.modules.setdefault("motor", types.SimpleNamespace(motor_asyncio=motor_asyncio))
sys.modules.setdefault("motor.motor_asyncio", motor_asyncio)

from .validation_repository import ValidationRepository
from ...domain.entities.validation import ValidationStatus, ValidationType


BASE_DOC = {
    "id": "validation-id",
    "user_id": "user-id",
    "validation_type": ValidationType.COMPANY.value,
    "status": ValidationStatus.PENDING.value,
    "comment": None,
    "reviewed_by": None,
    "reviewed_by_email": None,
}


def build_doc(**overrides):
    """Create a base validation document with datetime placeholders."""
    now = datetime(2024, 1, 1, 12, 0, 0)
    doc = {
        **BASE_DOC,
        "created_at": now,
        "updated_at": now,
        "reviewed_at": None,
    }
    doc.update(overrides)
    return doc


def test_hydrate_handles_datetime_objects():
    doc = build_doc()

    validation = ValidationRepository._hydrate_validation(doc)

    assert isinstance(validation.created_at, datetime)
    assert isinstance(validation.updated_at, datetime)
    assert validation.reviewed_at is None


@pytest.mark.parametrize(
    "field,value,expected_timezone",
    [
        ("created_at", "2024-01-02T15:30:45", None),
        ("updated_at", "2024-01-03T18:25:30Z", timezone.utc),
    ],
)
def test_hydrate_parses_iso_strings(field, value, expected_timezone):
    doc = build_doc(**{field: value})

    validation = ValidationRepository._hydrate_validation(doc)

    hydrated_value = getattr(validation, field)
    assert isinstance(hydrated_value, datetime)
    assert hydrated_value.tzinfo == expected_timezone


def test_hydrate_sets_none_for_invalid_dates():
    doc = build_doc(reviewed_at="not-a-date")

    validation = ValidationRepository._hydrate_validation(doc)

    assert validation.reviewed_at is None


def test_hydrate_sets_none_for_missing_fields():
    doc = build_doc()
    doc.pop("reviewed_at")

    validation = ValidationRepository._hydrate_validation(doc)

    assert validation.reviewed_at is None

