"""Маршрут диалога с ассистентом."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_dialog import DialogMessageCreateRequest, DialogMessageCreateResponse
from backend.api.security import require_internal_token
from backend.config import get_settings
from backend.services.dialog_messages import record_dialog_exchange
from backend.services.llm import LlmClient, get_llm_client
from backend.services.participants import ParticipantResolveError

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_internal_token)])


@router.post(
    "",
    response_model=DialogMessageCreateResponse,
    summary="Отправить сообщение и получить ответ ассистента",
)
async def create_dialog_message(
    body: DialogMessageCreateRequest,
    session: SessionDep,
    llm: Annotated[LlmClient, Depends(get_llm_client)],
) -> DialogMessageCreateResponse:
    settings = get_settings()
    logger.info(
        "dialog_message_accepted flow_id=%s telegram_user_id=%s",
        body.flow_id,
        body.telegram_user_id,
    )
    try:
        reply_text, user_message_id, assistant_message_id = await record_dialog_exchange(
            session,
            flow_id=body.flow_id,
            telegram_user_id=body.telegram_user_id,
            content=body.content,
            llm=llm,
            max_history_messages=settings.max_history_messages,
        )
    except ParticipantResolveError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc
    except RuntimeError as exc:
        logger.error("llm_generation_failed flow_id=%s", body.flow_id)
        raise ApiError(
            500,
            "internal_error",
            "Assistant is temporarily unavailable",
        ) from exc

    logger.info(
        "dialog_message_completed flow_id=%s telegram_user_id=%s user_message_id=%s assistant_message_id=%s",
        body.flow_id,
        body.telegram_user_id,
        user_message_id,
        assistant_message_id,
    )
    return DialogMessageCreateResponse(
        reply_text=reply_text,
        user_message_id=user_message_id,
        assistant_message_id=assistant_message_id,
    )
