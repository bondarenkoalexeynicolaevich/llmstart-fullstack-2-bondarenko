"""Обработчики aiogram: команды и текст через backend API."""

import logging
from io import BytesIO

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.backend_client import BackendApiError, BackendClient, BackendRequestError
from bot.config import Settings

logger = logging.getLogger(__name__)

_ERR_USER = "Сервис временно недоступен. Попробуйте позже."
_ERR_NOT_REGISTERED = (
    "Поток или участник не найдены на сервере. Проверьте FLOW_ID в настройках бота "
    "и что ваш Telegram-профиль привязан к участнику потока в базе."
)
_UNSUPPORTED = "Поддерживаются текстовые и голосовые сообщения; этот тип контента пока не обрабатывается."
_WELCOME = (
    "Привет! Отправляйте текстовые или голосовые сообщения — ответ формирует ассистент на сервере. "
    "История диалога хранится в базе курса."
)
_RESET_HINT = (
    "История ведётся на сервере. Сброс диалога из бота пока не поддерживается "
    "(будет отдельная операция API при необходимости)."
)


def setup_router(_settings: Settings, backend: BackendClient) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        uid = message.from_user.id if message.from_user else 0
        logger.info("event=user_start user_id=%s", uid)
        await message.answer(_WELCOME)

    @router.message(Command("reset"))
    async def cmd_reset(message: Message) -> None:
        uid = message.from_user.id if message.from_user else 0
        logger.info("event=user_reset user_id=%s", uid)
        await message.answer(_RESET_HINT)

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        if not message.from_user:
            return
        uid = message.from_user.id
        text = message.text or ""

        logger.info("event=text_message user_id=%s", uid)
        try:
            reply = await backend.post_dialog_message(uid, text)
        except BackendRequestError:
            logger.error("event=backend_unavailable user_id=%s", uid)
            await message.answer(_ERR_USER)
            return
        except BackendApiError as exc:
            if exc.status_code == 404 and exc.error_code in (
                "flow_not_found",
                "participant_not_found",
            ):
                logger.info("event=dialog_resolve_miss user_id=%s", uid)
                await message.answer(_ERR_NOT_REGISTERED)
                return
            logger.error(
                "event=backend_error user_id=%s http_status=%s",
                uid,
                exc.status_code,
            )
            await message.answer(_ERR_USER)
            return

        if not reply:
            logger.warning("event=backend_empty_reply user_id=%s", uid)
            await message.answer(_ERR_USER)
            return

        logger.info("event=dialog_ok user_id=%s", uid)
        await message.answer(reply)

    @router.message(F.content_type == ContentType.VOICE)
    async def on_voice(message: Message) -> None:
        if not message.from_user or not message.voice:
            return
        uid = message.from_user.id
        vc = message.voice
        log_duration = vc.duration if vc.duration is not None else -1
        logger.info("event=voice_message user_id=%s duration_sec=%s", uid, log_duration)

        bio = BytesIO()
        try:
            await message.bot.download(vc, destination=bio)
        except Exception:
            logger.exception("event=voice_download_failed user_id=%s", uid)
            await message.answer(_ERR_USER)
            return

        audio_bytes = bio.getvalue()
        fname = f"voice-{vc.file_unique_id}.oga"
        logger.info("event=voice_download_ok user_id=%s bytes=%s", uid, len(audio_bytes))

        try:
            reply = await backend.post_voice_dialog_message(uid, audio_bytes, fname)
        except BackendRequestError:
            logger.error("event=backend_unavailable user_id=%s", uid)
            await message.answer(_ERR_USER)
            return
        except BackendApiError as exc:
            if exc.status_code == 404 and exc.error_code in (
                "flow_not_found",
                "participant_not_found",
            ):
                logger.info("event=voice_resolve_miss user_id=%s", uid)
                await message.answer(_ERR_NOT_REGISTERED)
                return
            logger.error(
                "event=voice_backend_error user_id=%s http_status=%s",
                uid,
                exc.status_code,
            )
            await message.answer(_ERR_USER)
            return

        if not reply:
            logger.warning("event=voice_empty_reply user_id=%s", uid)
            await message.answer(_ERR_USER)
            return

        logger.info("event=voice_dialog_ok user_id=%s", uid)
        await message.answer(reply)

    @router.message()
    async def on_unsupported(message: Message) -> None:
        uid = message.from_user.id if message.from_user else 0
        logger.info("event=unsupported_message user_id=%s content_type=%s", uid, message.content_type)
        await message.answer(_UNSUPPORTED)

    return router
