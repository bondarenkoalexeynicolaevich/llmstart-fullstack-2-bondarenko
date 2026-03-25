"""Клиент OpenRouter через OpenAI-compatible API."""

import logging

from openai import AsyncOpenAI

from bot.config import Settings

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=settings.openrouter_api_key,
        )

    async def chat(self, messages: list[dict[str, str]]) -> str:
        kwargs: dict = {
            "model": self._settings.llm_model,
            "messages": messages,
            "temperature": self._settings.llm_temperature,
        }
        if self._settings.llm_max_tokens is not None:
            kwargs["max_tokens"] = self._settings.llm_max_tokens
        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as e:
            logger.exception("LLM request failed")
            raise RuntimeError("LLM request failed") from e

        choice = response.choices[0].message if response.choices else None
        content = (choice.content or "").strip() if choice else ""
        if not content:
            logger.warning("Empty LLM response")
        return content
