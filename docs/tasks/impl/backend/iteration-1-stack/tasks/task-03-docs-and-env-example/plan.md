# Задача 03: vision, `.env.example`, README

## Цель

Синхронизировать документацию и пример окружения с зафиксированным стеком backend.

## Шаги

1. [`docs/vision.md`](../../../../../../vision.md): таблица «Технологии → Backend» — FastAPI, SQLAlchemy 2.x async, Alembic, asyncpg, uvicorn; при необходимости строка в таблице архитектурных решений на ADR-002.
2. [`.env.example`](../../../../../../../.env.example): блок backend — `DATABASE_URL`, `API_HOST`, `API_PORT` с комментариями (без секретов).
3. [`README.md`](../../../../../../../README.md): 2–5 предложений про будущий backend, переменные и то, что рабочий запуск сервера ожидается в итерации 3 tasklist-backend.

## DoD

- Vision, example env и README согласованы с ADR-002 и conventions.
