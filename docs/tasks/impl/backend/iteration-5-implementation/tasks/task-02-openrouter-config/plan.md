# Задача: OpenRouter и настройки

## Цель

- `Settings`: `OPENROUTER_API_KEY` (то же имя, что у бота), `LLM_MODEL`, опционально базовый URL, `LLM_TEMPERATURE`, `MAX_HISTORY_MESSAGES`.
- `OpenRouterLlmClient` в `backend/services/llm.py` на `AsyncOpenAI`; история `(role, content)` + system; без логирования контента.
- При пустом ключе — `NotConfiguredLlmClient` как сейчас.
