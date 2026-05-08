"""Настройки из окружения (python-dotenv)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent

_DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Локальный Postgres (Docker) без TLS: иначе asyncpg может уйти в SSL upgrade и оборваться
# (на части связок Windows + Python 3.14 — «unexpected connection_lost()»).
ASYNCPG_CONNECT_ARGS: dict[str, Any] = {"ssl": False}


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
    jwt_secret: str
    jwt_expires_in_seconds: int
    log_level: str
    cors_origins: tuple[str, ...]
    openrouter_api_key: str
    llm_model: str
    openrouter_base_url: str
    llm_temperature: float
    max_history_messages: int
    openai_api_key: str
    voice_max_bytes: int


def _cors_origins_from_env() -> tuple[str, ...]:
    """Разрешённые Origin для браузерного веб-клиента (через запятую)."""
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw:
        return tuple(part.strip() for part in raw.split(",") if part.strip())
    return (
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    )


@lru_cache
def get_settings() -> Settings:
    load_dotenv(_ROOT / ".env")
    db = os.getenv("DATABASE_URL", "").strip()
    if not db:
        msg = "DATABASE_URL is required (postgresql+asyncpg://…)"
        raise RuntimeError(msg)
    base_url = os.getenv("OPENROUTER_BASE_URL", "").strip() or _DEFAULT_OPENROUTER_BASE
    internal_token = os.getenv("INTERNAL_API_TOKEN", "").strip()
    jwt_raw = os.getenv("JWT_SECRET", "").strip()
    jwt_secret = jwt_raw or (
        f"{internal_token}.jwt-dev-derived" if internal_token else ""
    )
    if not jwt_secret:
        msg = (
            "JWT_SECRET is required (or set INTERNAL_API_TOKEN for dev-derived JWT secret)"
        )
        raise RuntimeError(msg)
    return Settings(
        database_url=db,
        api_host=os.getenv("API_HOST", "127.0.0.1").strip(),
        api_port=int(os.getenv("API_PORT", "8000")),
        internal_api_token=internal_token,
        jwt_secret=jwt_secret,
        jwt_expires_in_seconds=_env_int("JWT_EXPIRES_IN_SECONDS", 604_800),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        cors_origins=_cors_origins_from_env(),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini").strip(),
        openrouter_base_url=base_url,
        llm_temperature=_env_float("LLM_TEMPERATURE", 0.7),
        max_history_messages=_env_int("MAX_HISTORY_MESSAGES", 30),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        voice_max_bytes=_env_int("VOICE_MAX_BYTES", 25 * 1024 * 1024),
    )
