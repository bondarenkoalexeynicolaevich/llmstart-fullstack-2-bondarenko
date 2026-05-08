"""GET/POST /v1/participants/{participant_id}/dialog-messages — веб (JWT)."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_dialog import DialogMessageCreateResponse
from backend.api.schemas_web import (
    DialogMessageListPageOut,
    DialogMessageReadOut,
    ParticipantDialogBody,
)
from backend.api.web_auth import require_jwt_principal
from backend.config import get_settings
from backend.services.dialog_messages import (
    DialogWebAccessError,
    list_dialog_messages_page,
    record_dialog_exchange_for_participant_web,
)
from backend.services.llm import LlmClient, get_llm_client
from backend.services.web_jwt import JwtPrincipal

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dialog-messages"])


@router.get(
    "/participants/{participant_id}/dialog-messages",
    response_model=DialogMessageListPageOut,
    summary="История диалога участника (веб)",
)
async def list_participant_dialog_route(
    participant_id: uuid.UUID,
    flow_id: Annotated[uuid.UUID, Query(description="UUID потока")],
    session: SessionDep,
    principal: Annotated[JwtPrincipal, Depends(require_jwt_principal)],
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
) -> DialogMessageListPageOut:
    if principal.participant_id != participant_id or principal.flow_id != flow_id:
        raise ApiError(403, "forbidden", "Operation not allowed for this participant")

    try:
        rows, next_c = await list_dialog_messages_page(
            session,
            participant_id=participant_id,
            flow_id=flow_id,
            limit=limit,
            cursor=cursor,
        )
    except DialogWebAccessError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc

    items = [
        DialogMessageReadOut(
            id=m.id,
            role=m.role.value,  # type: ignore[arg-type]
            content=m.content,
            created_at=m.created_at,
        )
        for m in rows
    ]
    return DialogMessageListPageOut(items=items, next_cursor=next_c)


@router.post(
    "/participants/{participant_id}/dialog-messages",
    response_model=DialogMessageCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить сообщение в диалог (веб)",
)
async def create_participant_dialog_route(
    response: Response,
    participant_id: uuid.UUID,
    flow_id: Annotated[uuid.UUID, Query(description="UUID потока")],
    body: ParticipantDialogBody,
    session: SessionDep,
    principal: Annotated[JwtPrincipal, Depends(require_jwt_principal)],
    llm: Annotated[LlmClient, Depends(get_llm_client)],
) -> DialogMessageCreateResponse:
    if principal.participant_id != participant_id or principal.flow_id != flow_id:
        raise ApiError(403, "forbidden", "Operation not allowed for this participant")

    settings = get_settings()
    logger.info(
        "participant_dialog_accepted flow_id=%s participant_id=%s",
        flow_id,
        participant_id,
    )
    try:
        (
            reply_text,
            user_message_id,
            assistant_message_id,
        ) = await record_dialog_exchange_for_participant_web(
            session,
            flow_id=flow_id,
            participant_id=participant_id,
            content=body.content,
            llm=llm,
            max_history_messages=settings.max_history_messages,
        )
    except DialogWebAccessError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc
    except Exception as exc:
        logger.exception(
            "participant_dialog_failed flow_id=%s participant_id=%s",
            flow_id,
            participant_id,
        )
        raise ApiError(
            500,
            "internal_error",
            "Assistant is temporarily unavailable",
        ) from exc

    response.headers["Location"] = (
        f"/v1/participants/{participant_id}/dialog-messages"
    )
    logger.info(
        "participant_dialog_completed flow_id=%s participant_id=%s",
        flow_id,
        participant_id,
    )
    return DialogMessageCreateResponse(
        reply_text=reply_text,
        user_message_id=user_message_id,
        assistant_message_id=assistant_message_id,
    )
