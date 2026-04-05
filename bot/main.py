"""Точка входа: polling Telegram-бота."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from bot.backend_client import BackendClient
from bot.config import load_settings
from bot.handlers import setup_router


def _configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )


async def _run() -> None:
    settings = load_settings()
    _configure_logging(settings.log_level)
    log = logging.getLogger(__name__)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    backend = BackendClient(settings)
    dp.include_router(setup_router(settings, backend))

    log.info("event=bot_start")
    try:
        await dp.start_polling(bot)
    finally:
        await backend.aclose()


def main() -> None:
    try:
        asyncio.run(_run())
    except ValueError as e:
        _configure_logging("INFO")
        logging.getLogger(__name__).error("%s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
