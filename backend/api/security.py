"""Аутентификация внутренних вызовов (Bearer + INTERNAL_API_TOKEN)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.api.errors import ApiError
from backend.config import get_settings

security = HTTPBearer(auto_error=False)


def require_internal_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> None:
    settings = get_settings()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "unauthorized", "Authentication required")
    token = (settings.internal_api_token or "").strip()
    if not token or credentials.credentials != token:
        raise ApiError(401, "unauthorized", "Authentication required")
