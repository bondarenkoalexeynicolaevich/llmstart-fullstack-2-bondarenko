# Итерация 4 (backend): базовые API-тесты

## Цель и ценность

Автотесты HTTP-сценария «сообщение ассистенту» по [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml), инфраструктура pytest и фикстур БД; мок LLM только через `dependency_overrides`. Минимальный маршрут `POST /v1/dialog-messages` с резолвом `Participant` и без персистентности `DialogMessage` до итерации 5.

**Планирование (граница с ит. 5):** идентификаторы `user_message_id` / `assistant_message_id` в ответе — сгенерированные UUID без таблицы `dialog_messages`; реальный OpenRouter, запись диалога и `POST /v1/submissions` — итерация 5.

## Задачи

| Задача | Папка |
|--------|-------|
| Зависимости и Makefile | [`tasks/task-01-deps-makefile/`](tasks/task-01-deps-makefile/) |
| conftest, фикстуры БД | [`tasks/task-02-tests-fixtures/`](tasks/task-02-tests-fixtures/) |
| Bearer, диалог, LLM-порт | [`tasks/task-03-dialog-route/`](tasks/task-03-dialog-route/) |
| Тесты, summary итерации, tasklist | [`tasks/task-04-tests-and-docs/`](tasks/task-04-tests-and-docs/) |

## Definition of Done

- `make test-backend` (или `uv run pytest backend/tests`) проходит при доступной PostgreSQL и `DATABASE_URL` / `TEST_DATABASE_URL`.
- Мок LLM не единственный прод-путь: дефолтная реализация — «не настроено» / raise, тесты подменяют зависимость.

## Риски

- `get_settings.cache_clear()` в фикстурах; глобальный engine сбрасывается в lifespan при каждом `TestClient`.
- TRUNCATE/сид для тестов выполняются через **sync `psycopg`**, иначе `asyncio.run` и сессия `asyncpg` конфликтуют с event loop `TestClient`.
