# Итерация 1 (backend): стек, ADR, соглашения

## Цель и ценность

Зафиксировать единый стек серверного ядра (HTTP, доступ к БД, миграции, запуск), оформить решение в ADR, синхронизировать правила репозитория и пример окружения с [`docs/vision.md`](../../../../vision.md) и [`docs/adr/adr-001-database.md`](../../../../adr/adr-001-database.md). Снять блокировку «на чём пишем backend» для итераций 2–3 tasklist.

## Решение по стеку

| Слой | Выбор |
|------|--------|
| HTTP | FastAPI |
| СУБД | PostgreSQL ([ADR-001](../../../../adr/adr-001-database.md)) |
| Доступ к БД | SQLAlchemy 2.x async + asyncpg |
| Миграции | Alembic |
| ASGI-сервер | uvicorn |

**Связь с ADR-001:** ADR-001 — выбор PostgreSQL; [ADR-002](../../../../adr/adr-002-backend-http-orm.md) — прикладной Python-стек поверх БД (HTTP + ORM + миграции).

## Задачи

| Задача | Папка |
|--------|--------|
| Стек и ADR | [`tasks/task-01-stack-and-adr/`](tasks/task-01-stack-and-adr/) |
| Conventions backend | [`tasks/task-02-conventions-backend/`](tasks/task-02-conventions-backend/) |
| Vision, `.env.example`, README | [`tasks/task-03-docs-and-env-example/`](tasks/task-03-docs-and-env-example/) |

## Файлы (итог)

- `docs/adr/adr-002-backend-http-orm.md`
- `docs/adr/README.md` — строка в таблице
- `.cursor/rules/conventions.mdc` — секции Bot и Backend
- `docs/vision.md` — таблица технологий Backend, при необходимости таблица ADR
- `.env.example` — `DATABASE_URL`, `API_HOST`, `API_PORT` (и комментарии)
- `README.md` — кратко про backend и дорожку запуска

Каталога `backend/` в этой итерации нет — воспроизводимый запуск сервера и цели `lint-backend` / `run-backend` в Makefile планируются в **итерации 3** (каркас) и **8** (качество) tasklist-backend.

## Риски

- **Дублирование ADR-001** — снято разделением: СУБД vs прикладной стек.
- **Переусложнение** — без DDD/лишних слоёв до появления реального кода; KISS в conventions.

## Следующие шаги

- Итерация 2 tasklist-backend: контракты API.
- Итерация 3: каркас `backend/`, миграции под User, Flow, Participant ([`docs/data-model.md`](../../../../data-model.md)).
