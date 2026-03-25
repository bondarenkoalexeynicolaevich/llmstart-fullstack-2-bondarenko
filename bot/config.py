"""Загрузка настроек из переменных окружения (.env)."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        msg = f"Missing or empty required environment variable: {name}"
        raise ValueError(msg)
    return value


def _optional_int(name: str) -> int | None:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return None
    return int(raw.strip())


def _float_with_default(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw.strip())


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    openrouter_api_key: str
    llm_model: str
    system_prompt: str
    llm_temperature: float
    llm_max_tokens: int | None
    max_history_messages: int | None
    log_level: str


def load_settings() -> Settings:
    return Settings(
        bot_token=_require("BOT_TOKEN"),
        openrouter_api_key=_require("OPENROUTER_API_KEY"),
        llm_model=_require("LLM_MODEL"),
        system_prompt=_require("SYSTEM_PROMPT"),
        llm_temperature=_float_with_default("LLM_TEMPERATURE", 0.7),
        llm_max_tokens=_optional_int("LLM_MAX_TOKENS"),
        max_history_messages=_optional_int("MAX_HISTORY_MESSAGES"),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip() or "INFO",
    )
