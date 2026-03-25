"""Обработчики aiogram: команды, текст, история в памяти."""

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import Settings
from bot.llm_client import LLMClient

logger = logging.getLogger(__name__)

_ERR_USER = "Сервис временно недоступен. Попробуйте позже."
_UNSUPPORTED = "Поддерживаются только текстовые сообщения."
_WELCOME = (
    "Привет! Я отвечаю на текстовые сообщения. История сброшена — можно начинать диалог."
)


def _fresh_history(settings: Settings) -> list[dict[str, str]]:
    return [{"role": "system", "content": settings.system_prompt}]


def _trim_history(
    messages: list[dict[str, str]],
    max_after_system: int | None,
) -> list[dict[str, str]]:
    if not messages or max_after_system is None:
        return messages
    if messages[0].get("role") != "system":
        return messages[-max_after_system:]
    system = messages[0]
    tail = messages[1:]
    if len(tail) <= max_after_system:
        return messages
    return [system, *tail[-max_after_system:]]


def setup_router(settings: Settings, llm: LLMClient) -> Router:
    router = Router()
    histories: dict[int, list[dict[str, str]]] = {}

    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        uid = message.from_user.id if message.from_user else 0
        histories[uid] = _fresh_history(settings)
        logger.info("event=user_start user_id=%s", uid)
        await message.answer(_WELCOME)

    @router.message(Command("reset"))
    async def cmd_reset(message: Message) -> None:
        uid = message.from_user.id if message.from_user else 0
        histories[uid] = _fresh_history(settings)
        logger.info("event=user_reset user_id=%s", uid)
        await message.answer("История диалога сброшена.")

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        if not message.from_user:
            return
        uid = message.from_user.id
        text = message.text or ""
        if uid not in histories:
            histories[uid] = _fresh_history(settings)

        history = histories[uid]
        history.append({"role": "user", "content": text})
        history[:] = _trim_history(history, settings.max_history_messages)

        logger.info("event=text_message user_id=%s", uid)
        try:
            reply = await llm.chat(history)
        except RuntimeError:
            logger.error("event=llm_failed user_id=%s", uid)
            if history and history[-1].get("role") == "user":
                history.pop()
            await message.answer(_ERR_USER)
            return

        if not reply:
            logger.warning("event=llm_empty user_id=%s", uid)
            if history and history[-1].get("role") == "user":
                history.pop()
            await message.answer(_ERR_USER)
            return

        history.append({"role": "assistant", "content": reply})
        history[:] = _trim_history(history, settings.max_history_messages)
        logger.info("event=llm_ok user_id=%s", uid)
        await message.answer(reply)

    @router.message()
    async def on_unsupported(message: Message) -> None:
        uid = message.from_user.id if message.from_user else 0
        logger.info("event=unsupported_message user_id=%s", uid)
        await message.answer(_UNSUPPORTED)

    return router
