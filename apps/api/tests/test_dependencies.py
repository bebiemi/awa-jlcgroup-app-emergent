import httpx
import pytest
from fastapi import HTTPException
from starlette.requests import Request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.presentation.dependencies import get_current_user


class MockAsyncClient:
    def __init__(self, response: httpx.Response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        return self.response


def build_request(headers: dict[str, str] | None = None) -> Request:
    headers = headers or {}
    header_items = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "headers": header_items})


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_get_current_user_logs_body_for_4xx(monkeypatch, caplog):
    auth_request = httpx.Request("GET", "http://auth/api/auth/me")
    response = httpx.Response(401, request=auth_request, text="invalid token")
    monkeypatch.setattr("src.presentation.dependencies.httpx.AsyncClient", lambda *_, **__: MockAsyncClient(response))

    request = build_request({"authorization": "Bearer test"})

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, db=None)

    assert exc_info.value.status_code == 401
    assert "invalid token" in caplog.text


@pytest.mark.anyio
async def test_get_current_user_maps_5xx_to_503(monkeypatch, caplog):
    auth_request = httpx.Request("GET", "http://auth/api/auth/me")
    response = httpx.Response(502, request=auth_request, text="upstream outage")
    monkeypatch.setattr("src.presentation.dependencies.httpx.AsyncClient", lambda *_, **__: MockAsyncClient(response))

    request = build_request({"authorization": "Bearer test"})

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, db=None)

    assert exc_info.value.status_code == 503
    assert "upstream error" in str(exc_info.value.detail).lower()
    assert "upstream outage" in caplog.text


@pytest.mark.anyio
async def test_get_current_user_truncates_large_body(monkeypatch, caplog):
    auth_request = httpx.Request("GET", "http://auth/api/auth/me")
    long_text = "x" * 600
    response = httpx.Response(500, request=auth_request, text=long_text)
    monkeypatch.setattr("src.presentation.dependencies.httpx.AsyncClient", lambda *_, **__: MockAsyncClient(response))

    request = build_request({"authorization": "Bearer test"})

    with pytest.raises(HTTPException):
        await get_current_user(request, db=None)

    # Ensure the logged body is truncated to avoid leaking large payloads
    assert long_text[:500] in caplog.text
    assert long_text not in caplog.text
