"""JWT веб-сессии (HS256) — claims совместимы с фронтом итераций 2+."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt

from backend.api.errors import ApiError
from backend.config import Settings


@dataclass(frozen=True, slots=True)
class JwtPrincipal:
    user_id: uuid.UUID
    participant_id: uuid.UUID
    flow_id: uuid.UUID
    role: Literal["student", "teacher"]


def create_access_token(
    *,
    settings: Settings,
    user_id: uuid.UUID,
    participant_id: uuid.UUID,
    flow_id: uuid.UUID,
    role: Literal["student", "teacher"],
) -> tuple[str, int]:
    """Возвращает (token, expires_in_seconds)."""
    now = datetime.now(UTC)
    exp = now + timedelta(seconds=settings.jwt_expires_in_seconds)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "participant_id": str(participant_id),
        "flow_id": str(flow_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )
    return token, settings.jwt_expires_in_seconds


def decode_principal(settings: Settings, token: str) -> JwtPrincipal:
    try:
        raw = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
    except jwt.PyJWTError as exc:
        raise ApiError(401, "unauthorized", "Authentication required") from exc
    try:
        uid = uuid.UUID(str(raw["sub"]))
        pid = uuid.UUID(str(raw["participant_id"]))
        fid = uuid.UUID(str(raw["flow_id"]))
        role = str(raw["role"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiError(401, "unauthorized", "Authentication required") from exc
    if role not in ("student", "teacher"):
        raise ApiError(401, "unauthorized", "Authentication required")
    return JwtPrincipal(user_id=uid, participant_id=pid, flow_id=fid, role=role)
