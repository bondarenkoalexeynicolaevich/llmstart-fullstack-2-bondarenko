"""POST /v1/auth/web-session — без Bearer."""

from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_web import WebSessionCreateRequest, WebSessionCreateResponse
from backend.config import get_settings
from backend.models.enums import MemberRole
from backend.services.web_jwt import create_access_token
from backend.services.web_session import WebSessionError, build_web_session_context

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/web-session",
    response_model=WebSessionCreateResponse,
    summary="Веб-сессия по Telegram username",
)
async def create_web_session_route(
    body: WebSessionCreateRequest,
    session: SessionDep,
) -> WebSessionCreateResponse:
    try:
        user, participant = await build_web_session_context(
            session,
            telegram_username=body.telegram_username,
            flow_id=body.flow_id,
        )
    except WebSessionError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc

    settings = get_settings()
    role = cast(
        Literal["student", "teacher"],
        (
            "teacher"
            if participant.role == MemberRole.teacher
            else "student"
        ),
    )
    token, ttl = create_access_token(
        settings=settings,
        user_id=user.id,
        participant_id=participant.id,
        flow_id=participant.flow_id,
        role=role,
    )
    return WebSessionCreateResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=ttl,
        user_id=user.id,
        participant_id=participant.id,
        role=role,
        display_name=user.name,
    )
