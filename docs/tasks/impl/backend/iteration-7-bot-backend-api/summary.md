# Итерация 7: итог

## Сделано

- Бот вызывает только **`POST /v1/dialog-messages`** через **`bot/backend_client.py`** (`httpx`), без `bot/llm_client.py` и без локальной истории.
- Конфиг бота: **`BOT_TOKEN`**, **`BACKEND_BASE_URL`**, **`INTERNAL_API_TOKEN`**, **`FLOW_ID`**; ключи OpenRouter и промпт из бота убраны.
- **`.env.example`** и **README** отражают порядок: миграции → backend → данные Flow/User/Participant → бот; добавлены **smoke** (`make smoke-dialog`) и E2E-инструкция.

## Отклонения от плана

- Нет отдельного `tasklist-bot.md`; только обновление **tasklist-backend**.

## Риски (как в plan.md)

- Без корректных строк в БД диалог вернёт **404** с кодами домена — в README зафиксировано.
