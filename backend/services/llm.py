"""Граница вызова LLM (OpenRouter / OpenAI-compatible)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from openai import AsyncOpenAI

from backend.config import Settings, get_settings


@runtime_checkable
class LlmClient(Protocol):
    async def generate_reply(
        self,
        *,
        system_prompt: str,
        messages: list[tuple[str, str]],
    ) -> str:
        """messages — пары (role, content), role в {user, assistant, system}."""


class NotConfiguredLlmClient:
    """Среда без ключа OpenRouter — явная ошибка, не «успешный» заглушечный ответ."""

    async def generate_reply(
        self,
        *,
        system_prompt: str,
        messages: list[tuple[str, str]],
    ) -> str:
        _ = system_prompt
        _ = messages
        msg = "LLM client is not configured (set OPENROUTER_API_KEY)"
        raise RuntimeError(msg)


class OpenRouterLlmClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )

    async def generate_reply(
        self,
        *,
        system_prompt: str,
        messages: list[tuple[str, str]],
    ) -> str:
        chat_messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]
        chat_messages.extend(
            {"role": role, "content": content} for role, content in messages
        )
        response = await self._client.chat.completions.create(
            model=self._settings.llm_model,
            messages=chat_messages,
            temperature=self._settings.llm_temperature,
        )
        choice = response.choices[0].message.content
        return (choice or "").strip()


_not_configured: LlmClient = NotConfiguredLlmClient()


def get_llm_client() -> LlmClient:
    settings = get_settings()
    if settings.openrouter_api_key:
        return OpenRouterLlmClient(settings)
    return _not_configured
