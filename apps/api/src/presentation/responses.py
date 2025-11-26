"""Shared response helpers for consistent API metadata."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse


ERROR_META_KEYS = {"updated_at", "retry_after"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalized_error(
    *,
    code: str,
    message: str,
    status_code: int,
    retry_after: Optional[int] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    meta: Dict[str, Any] = {"updated_at": utc_now_iso()}
    if retry_after is not None:
        meta["retry_after"] = retry_after
    if extra_meta:
        meta.update(extra_meta)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {"code": code, "message": message},
            "meta": meta,
        },
    )


def enrich_json_payload(payload: Dict[str, Any], **meta_values: Any) -> Dict[str, Any]:
    """Ensure payload carries a meta.updated_at timestamp for offline sync."""

    meta = payload.get("meta", {}) or {}
    meta.setdefault("updated_at", utc_now_iso())
    for key, value in meta_values.items():
        if key not in ERROR_META_KEYS or key not in meta:
            meta.setdefault(key, value)
    payload["meta"] = meta
    return payload
