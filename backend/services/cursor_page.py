"""Курсорная пагинация (opaque string, JSON + base64url)."""

from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime
from typing import Any


class CursorDecodeError(Exception):
    pass


def encode_cursor(dt: datetime, row_id: uuid.UUID) -> str:
    payload = {"ts": dt.isoformat(), "id": str(row_id)}
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(value: str) -> tuple[datetime, uuid.UUID]:
    pad = "=" * (-len(value) % 4)
    try:
        raw = base64.urlsafe_b64decode(value + pad)
        data: Any = json.loads(raw.decode("utf-8"))
        ts_raw = data["ts"]
        id_raw = data["id"]
        if not isinstance(ts_raw, str) or not isinstance(id_raw, str):
            raise CursorDecodeError
        parsed = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        uid = uuid.UUID(id_raw)
    except (
        CursorDecodeError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        raise CursorDecodeError from exc
    return parsed, uid
