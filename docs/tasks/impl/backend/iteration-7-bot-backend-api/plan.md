# Итерация 7: рефакторинг бота под Backend API

## Цель и ценность

- **Цель:** бот вызывает только `POST /v1/dialog-messages`; прямой OpenRouter в боте отсутствует.
- **Ценность:** единый контур Bot → Backend → DB/LLM ([`docs/vision.md`](../../../vision.md)), история в PostgreSQL, один контракт ([`docs/api/backend-v1.openapi.yaml`](../../../api/backend-v1.openapi.yaml)).

## Стек

- `httpx.AsyncClient`, таймауты, `Authorization: Bearer`.
- Настройки: `BOT_TOKEN`, `BACKEND_BASE_URL`, `INTERNAL_API_TOKEN`, `FLOW_ID` (UUID), `LOG_LEVEL`.

## Задачи

| Задача | Папка |
|--------|--------|
| HTTP-клиент | [`tasks/task-01-backend-http-client/`](tasks/task-01-backend-http-client/) |
| Конфиг и `.env.example` | [`tasks/task-02-config-env/`](tasks/task-02-config-env/) |
| Handlers и `main.py` | [`tasks/task-03-handlers-main/`](tasks/task-03-handlers-main/) |
| README, smoke, итоги | [`tasks/task-04-docs-smoke/`](tasks/task-04-docs-smoke/) |

## Риски

- `resolve_flow_participant` требует существующие `Flow`, `User` (по `telegram_id`), `Participant`. Иначе API вернёт **404** с кодами `flow_not_found` / `participant_not_found`.
- Локального API «сбросить диалог» нет: `/start` и `/reset` только UX, без обхода единой истории в БД.

## Definition of Done (итерация)

- Боевой ответ ассистента только через backend.
- `ruff check bot/` без замечаний.
- Smoke: backend + бот (или скрипт к API при подготовленной БД); логи без текста пользовательских сообщений.
