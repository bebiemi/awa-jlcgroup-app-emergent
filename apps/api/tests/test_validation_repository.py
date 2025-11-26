import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import pytest

# Ensure src is importable when running tests from repository root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.domain.entities.validation import AccountValidation, ValidationStatus, ValidationType
from src.infrastructure.repositories.validation_repository import ValidationRepository


class FakeCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.docs = list(docs)
        self._sort_field: str | None = None
        self._sort_direction: int = 1
        self._skip: int = 0
        self._limit: int | None = None

    def sort(self, field: str, direction: int):
        self._sort_field = field
        self._sort_direction = direction
        return self

    def skip(self, value: int):
        self._skip = value
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    async def to_list(self, length: int | None = None):  # noqa: ARG002 - signature compatibility
        items = self.docs
        if self._sort_field:
            reverse = self._sort_direction == -1
            items = sorted(items, key=lambda doc: doc.get(self._sort_field), reverse=reverse)
        if self._skip:
            items = items[self._skip :]
        if self._limit is not None:
            items = items[: self._limit]
        return items


class FakeCollection:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.docs = docs

    async def count_documents(self, query: Dict[str, Any]):
        return len(self._filter(query))

    def find(self, query: Dict[str, Any], projection: Dict[str, int] | None = None):
        filtered = self._filter(query)
        projected = [self._apply_projection(doc, projection) for doc in filtered]
        return FakeCursor(projected)

    def _filter(self, query: Dict[str, Any]):
        def matches(doc: Dict[str, Any]):
            return all(doc.get(key) == value for key, value in query.items())

        return [doc for doc in self.docs if matches(doc)]

    def _apply_projection(self, doc: Dict[str, Any], projection: Dict[str, int] | None):
        if not projection:
            return doc
        data = dict(doc)
        for key, include in projection.items():
            if include == 0 and key in data:
                data.pop(key)
        return data


class FakeDB:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.account_validations = FakeCollection(docs)


@pytest.mark.asyncio
async def test_list_sorts_desc_and_hydrates_datetimes():
    docs = [
        {
            "id": "1",
            "user_id": "user-1",
            "validation_type": ValidationType.COMPANY.value,
            "status": ValidationStatus.PENDING.value,
            "created_at": "2024-01-02T12:00:00Z",
            "updated_at": "2024-01-02T12:00:00Z",
        },
        {
            "id": "2",
            "user_id": "user-2",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.APPROVED.value,
            "created_at": "2024-01-03T12:00:00Z",
            "updated_at": "2024-01-03T12:00:00Z",
        },
        {
            "id": "3",
            "user_id": "user-3",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.REJECTED.value,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        },
    ]

    repo = ValidationRepository(FakeDB(docs))

    results, total = await repo.list()

    assert total == 3
    assert [validation.id for validation in results] == ["2", "1", "3"]
    for validation in results:
        assert isinstance(validation.created_at, datetime)
        assert isinstance(validation.updated_at, datetime)


@pytest.mark.asyncio
async def test_list_filters_by_status_and_validation_type_with_pagination():
    docs = [
        {
            "id": "1",
            "user_id": "user-1",
            "validation_type": ValidationType.COMPANY.value,
            "status": ValidationStatus.PENDING.value,
            "created_at": "2024-01-03T10:00:00Z",
            "updated_at": "2024-01-03T10:00:00Z",
        },
        {
            "id": "2",
            "user_id": "user-2",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.PENDING.value,
            "created_at": "2024-01-02T10:00:00Z",
            "updated_at": "2024-01-02T10:00:00Z",
        },
        {
            "id": "3",
            "user_id": "user-3",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.APPROVED.value,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
        },
        {
            "id": "4",
            "user_id": "user-4",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.PENDING.value,
            "created_at": "2024-01-04T10:00:00Z",
            "updated_at": "2024-01-04T10:00:00Z",
        },
    ]

    repo = ValidationRepository(FakeDB(docs))

    results, total = await repo.list(
        status=ValidationStatus.PENDING,
        validation_type=ValidationType.INTERIM,
        skip=1,
        limit=1,
    )

    assert total == 2  # two documents match both filters
    assert len(results) == 1
    assert results[0].id == "2"  # second most recent pending interim validation


@pytest.mark.asyncio
async def test_count_by_status_matches_repository_query():
    docs = [
        {
            "id": "1",
            "user_id": "user-1",
            "validation_type": ValidationType.COMPANY.value,
            "status": ValidationStatus.PENDING.value,
            "created_at": "2024-01-03T10:00:00Z",
            "updated_at": "2024-01-03T10:00:00Z",
        },
        {
            "id": "2",
            "user_id": "user-2",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.PENDING.value,
            "created_at": "2024-01-02T10:00:00Z",
            "updated_at": "2024-01-02T10:00:00Z",
        },
        {
            "id": "3",
            "user_id": "user-3",
            "validation_type": ValidationType.INTERIM.value,
            "status": ValidationStatus.APPROVED.value,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
        },
    ]

    repo = ValidationRepository(FakeDB(docs))

    pending_count = await repo.count_by_status(ValidationStatus.PENDING)
    approved_count = await repo.count_by_status(ValidationStatus.APPROVED)

    assert pending_count == 2
    assert approved_count == 1
    assert isinstance(repo._hydrate_validation(docs[0]), AccountValidation)


@pytest.mark.asyncio
async def test_repository_accepts_raw_status_and_type_strings():
    docs = [
        {
            "id": "1",
            "user_id": "user-1",
            "validation_type": "custom_company",
            "status": "en_attente",
            "created_at": "2024-01-03T10:00:00Z",
            "updated_at": "2024-01-03T10:00:00Z",
        },
        {
            "id": "2",
            "user_id": "user-2",
            "validation_type": "custom_company",
            "status": "approuve",
            "created_at": "2024-01-02T10:00:00Z",
            "updated_at": "2024-01-02T10:00:00Z",
        },
    ]

    repo = ValidationRepository(FakeDB(docs))

    pending_results, total_pending = await repo.list(
        status="en_attente", validation_type="custom_company"
    )
    approved_results, total_approved = await repo.list(status="approuve")

    assert total_pending == 1
    assert total_approved == 1
    assert pending_results[0].status == "en_attente"
    assert approved_results[0].validation_type == "custom_company"
    assert await repo.count_by_status("en_attente") == 1
