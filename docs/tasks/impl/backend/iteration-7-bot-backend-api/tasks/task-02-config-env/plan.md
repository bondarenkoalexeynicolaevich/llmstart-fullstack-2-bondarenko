# Задача 02: Конфиг бота и `.env.example`

## Цель

`Settings` в `bot/config.py`: обязательны `BACKEND_BASE_URL`, `INTERNAL_API_TOKEN`, `FLOW_ID` (валидный UUID). Убрать требование OpenRouter и истории в боте.

## Состав работ

- Удалить из бота: `OPENROUTER_*`, `LLM_*`, `SYSTEM_PROMPT`, `MAX_HISTORY_MESSAGES`.
- `.env.example`: блок бота с `FLOW_ID`, пояснения к `INTERNAL_API_TOKEN` / `BACKEND_BASE_URL`; LLM остаётся в секции backend.

## DoD

- `load_settings()` падает с понятной ошибкой при пустых обязательных полях.
- Бот не требует ключей OpenRouter.
