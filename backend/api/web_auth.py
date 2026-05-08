"""JWT для веб-клиента (не путать с INTERNAL_API_TOKEN бота)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.api.errors import ApiError
from backend.config import get_settings
from backend.services.web_jwt import JwtPrincipal, decode_principal

_web_bearer = HTTPBearer(auto_error=False)


async def require_jwt_principal(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_web_bearer),
    ],
) -> JwtPrincipal:
    settings = get_settings()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "unauthorized", "Authentication required")
    if credentials.credentials == settings.internal_api_token:
        raise ApiError(
            403,
            "forbidden",
            "Operation not allowed for this participant",
        )
    return decode_principal(settings, credentials.credentials)


async def require_teacher_in_flow(
    flow_id: uuid.UUID,
    principal: Annotated[JwtPrincipal, Depends(require_jwt_principal)],
) -> JwtPrincipal:
    if principal.flow_id != flow_id:
        raise ApiError(403, "forbidden", "Operation not allowed for this participant")
    if principal.role != "teacher":
        raise ApiError(403, "forbidden", "Operation not allowed for this participant")
    return principal


async def require_member_in_flow(
    flow_id: uuid.UUID,
    principal: Annotated[JwtPrincipal, Depends(require_jwt_principal)],
) -> JwtPrincipal:
    if principal.flow_id != flow_id:
        raise ApiError(403, "forbidden", "Operation not allowed for this participant")
    return principal
