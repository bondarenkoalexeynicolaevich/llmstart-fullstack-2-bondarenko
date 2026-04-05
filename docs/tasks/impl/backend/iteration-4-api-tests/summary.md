# Итерация 4 (backend): итог

## Сделано

- Инфраструктура: `pytest` / `pytest-asyncio`, [`pytest.ini`](../../../../../pytest.ini), [`make test-backend`](../../../../../Makefile); sync `psycopg` для TRUNCATE и сидов (избежание конфликта asyncio event loop с `Starlette` `TestClient`).
- Маршрут **`POST /v1/dialog-messages`**: Bearer (`INTERNAL_API_TOKEN`), резолв Flow/User/Participant, ответ по OpenAPI; UUID сообщений генерируются без таблицы `dialog_messages` (итерация 5).
- LLM: [`get_llm_client`](../../../../../backend/services/llm.py) / `NotConfiguredLlmClient`; в тестах — `dependency_overrides`, не единственный прод-путь.
- Тесты: health, 401, happy-path с фейковым LLM, `flow_not_found`, `participant_not_found`; сдачи — `pytest.skip` до итерации 5.

## Задачи

| Задача | Папка |
|--------|-------|
| Зависимости / Makefile | [`tasks/task-01-deps-makefile/`](tasks/task-01-deps-makefile/) |
| conftest / фикстуры | [`tasks/task-02-tests-fixtures/`](tasks/task-02-tests-fixtures/) |
| Диалог / LLM-порт | [`tasks/task-03-dialog-route/`](tasks/task-03-dialog-route/) |
| Тесты и tasklist | [`tasks/task-04-tests-and-docs/`](tasks/task-04-tests-and-docs/) |

## Отклонения от плана

- Явно добавлен **`psycopg[binary]`** в `requirements.txt`: иначе `asyncio.run` + `async` session после `TestClient` даёт зависание/конфликт loop с `asyncpg`-engine.

## Следующий шаг

Итерация 5 tasklist-backend: миграции `DialogMessage` / домен сдач, реальный OpenRouter, `POST /v1/submissions`, доработка тестов сдачи.
