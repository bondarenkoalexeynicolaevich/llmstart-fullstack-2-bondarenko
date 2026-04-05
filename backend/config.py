"""Настройки из окружения (python-dotenv)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent

_DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return float(raw)


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    api_host: str
    api_port: int
    internal_api_token: str
    log_level: str
    openrouter_api_key: str
    llm_model: str
    openrouter_base_url: str
    llm_temperature: float
    max_history_messages: int


@lru_cache
def get_settings() -> Settings:
    load_dotenv(_ROOT / ".env")
    db = os.getenv("DATABASE_URL", "").strip()
    if not db:
        msg = "DATABASE_URL is required (postgresql+asyncpg://…)"
        raise RuntimeError(msg)
    base_url = os.getenv("OPENROUTER_BASE_URL", "").strip() or _DEFAULT_OPENROUTER_BASE
    return Settings(
        database_url=db,
        api_host=os.getenv("API_HOST", "127.0.0.1").strip(),
        api_port=int(os.getenv("API_PORT", "8000")),
        internal_api_token=os.getenv("INTERNAL_API_TOKEN", "").strip(),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini").strip(),
        openrouter_base_url=base_url,
        llm_temperature=_env_float("LLM_TEMPERATURE", 0.7),
        max_history_messages=_env_int("MAX_HISTORY_MESSAGES", 30),
    )
