"""Загрузка настроек из переменных окружения (.env)."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        msg = f"Missing or empty required environment variable: {name}"
        raise ValueError(msg)
    return value


def _require_uuid(name: str) -> uuid.UUID:
    return uuid.UUID(_require(name))


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    backend_base_url: str
    internal_api_token: str
    flow_id: uuid.UUID
    log_level: str


def load_settings() -> Settings:
    return Settings(
        bot_token=_require("BOT_TOKEN"),
        backend_base_url=_require("BACKEND_BASE_URL"),
        internal_api_token=_require("INTERNAL_API_TOKEN"),
        flow_id=_require_uuid("FLOW_ID"),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip() or "INFO",
    )
