"""POST /v1/voice/dialog-messages — multipart, STT (Whisper) + диалог."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_dialog import DialogMessageCreateResponse
from backend.api.security import security
from backend.config import get_settings
from backend.services.dialog_messages import (
    DialogWebAccessError,
    record_dialog_exchange,
    record_dialog_exchange_for_participant_web,
)
from backend.services.llm import LlmClient, get_llm_client
from backend.services.participants import ParticipantResolveError
from backend.services.voice_stt import transcribe_audio
from backend.services.web_jwt import JwtPrincipal, decode_principal

logger = logging.getLogger(__name__)

router = APIRouter()

AuthMode = Literal["internal", "jwt"]


def _resolve_voice_auth(
    credentials: HTTPAuthorizationCredentials | None,
    flow_id: uuid.UUID,
    telegram_user_id: int | None,
) -> tuple[AuthMode, int | None, JwtPrincipal | None]:
    settings = get_settings()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "unauthorized", "Authentication required")

    token = credentials.credentials
    internal = (settings.internal_api_token or "").strip()

    if internal and token == internal:
        if telegram_user_id is None:
            raise ApiError(
                400,
                "validation_error",
                "telegram_user_id is required for internal (bot) calls",
            )
        return "internal", telegram_user_id, None

    if telegram_user_id is not None:
        raise ApiError(
            400,
            "validation_error",
            "telegram_user_id must not be sent with web JWT",
        )

    principal = decode_principal(settings, token)
    if principal.flow_id != flow_id:
        raise ApiError(403, "forbidden", "Operation not allowed for this participant")
    return "jwt", None, principal


@router.post(
    "",
    response_model=DialogMessageCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Голосовое сообщение: STT и ответ ассистента",
)
async def create_voice_dialog_message(
    response: Response,
    session: SessionDep,
    llm: Annotated[LlmClient, Depends(get_llm_client)],
    audio: Annotated[UploadFile, File(description="Аудио пользователя")],
    flow_id: Annotated[uuid.UUID, Form(description="UUID потока")],
    telegram_user_id: Annotated[
        int | None,
        Form(description="Telegram user id (только internal / бот)"),
    ] = None,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ] = None,
) -> DialogMessageCreateResponse:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ApiError(
            503,
            "stt_unavailable",
            "Voice dialog is not configured (OPENAI_API_KEY)",
        )

    mode, bot_telegram_id, principal = _resolve_voice_auth(
        credentials,
        flow_id,
        telegram_user_id,
    )

    raw = await audio.read()
    size = len(raw)
    if size == 0:
        raise ApiError(400, "validation_error", "Empty audio file")
    if size > settings.voice_max_bytes:
        raise ApiError(
            413,
            "payload_too_large",
            f"Audio exceeds limit of {settings.voice_max_bytes} bytes",
        )

    fname = audio.filename or "voice.webm"
    log_user: int | str
    if mode == "internal":
        log_user = bot_telegram_id or 0
        logger.info(
            "voice_dialog_accepted mode=internal flow_id=%s telegram_user_id=%s bytes=%s",
            flow_id,
            log_user,
            size,
        )
    else:
        log_user = str(principal.participant_id) if principal else ""
        logger.info(
            "voice_dialog_accepted mode=jwt flow_id=%s participant_id=%s bytes=%s",
            flow_id,
            log_user,
            size,
        )

    try:
        transcription = await transcribe_audio(
            api_key=settings.openai_api_key,
            audio_bytes=raw,
            filename=fname,
        )
    except Exception as exc:
        raise ApiError(
            503,
            "stt_failed",
            "Speech recognition temporarily unavailable",
        ) from exc

    if not transcription.strip():
        raise ApiError(
            400,
            "validation_error",
            "Could not transcribe speech; try again or use text",
        )

    try:
        if mode == "internal":
            assert bot_telegram_id is not None
            reply_text, user_mid, assistant_mid = await record_dialog_exchange(
                session,
                flow_id=flow_id,
                telegram_user_id=bot_telegram_id,
                content=transcription,
                llm=llm,
                max_history_messages=settings.max_history_messages,
            )
            response.headers["Location"] = "/v1/dialog-messages"
        else:
            assert principal is not None
            reply_text, user_mid, assistant_mid = (
                await record_dialog_exchange_for_participant_web(
                    session,
                    flow_id=flow_id,
                    participant_id=principal.participant_id,
                    content=transcription,
                    llm=llm,
                    max_history_messages=settings.max_history_messages,
                )
            )
            pid = principal.participant_id
            response.headers["Location"] = (
                f"/v1/participants/{pid}/dialog-messages"
            )
    except ParticipantResolveError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc
    except DialogWebAccessError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc
    except Exception as exc:
        logger.exception("voice_dialog_failed flow_id=%s mode=%s", flow_id, mode)
        raise ApiError(
            500,
            "internal_error",
            "Assistant is temporarily unavailable",
        ) from exc

    logger.info("voice_dialog_completed flow_id=%s mode=%s", flow_id, mode)
    return DialogMessageCreateResponse(
        reply_text=reply_text,
        user_message_id=user_mid,
        assistant_message_id=assistant_mid,
        transcription=transcription,
    )
