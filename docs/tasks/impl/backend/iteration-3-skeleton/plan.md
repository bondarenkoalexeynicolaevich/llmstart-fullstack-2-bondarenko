# Итерация 3 (backend): каркас сервиса и миграции

## Цель и ценность

Поднять **воспроизводимый каркас** `backend/`: приложение FastAPI с жизненным циклом, конфигурация из окружения, **async-подключение к PostgreSQL**, заготовка маршрутов под префикс **`/v1`** (без бизнес-логики endpoint’ов — она в итерации 5), первая **Alembic**-ревизия с таблицами **User**, **Flow**, **Participant** по [`docs/data-model.md`](../../../../data-model.md) и дорожной карте [`docs/plan.md`](../../../../plan.md) (этап «ядро: пользователь, поток, участие»).

**Ценность:** после итерации команда может поднять процесс, прогнать миграции на чистой БД и опереться на согласованную схему; итерации 4–5 не начинаются с нулевой структуры проекта.

## Ограничения и выравнивание

| Источник | Что учитывать |
|----------|----------------|
| [`docs/vision.md`](../../../../vision.md) | Структура `backend/`: `main.py`, `config.py`, `api/`, `services/`, `models/`; логирование без текста сообщений и секретов |
| [`docs/adr/adr-002-backend-http-orm.md`](../../../../adr/adr-002-backend-http-orm.md) | FastAPI, SQLAlchemy 2.x async + asyncpg, Alembic, uvicorn |
| [`.cursor/rules/conventions.mdc`](../../../../../.cursor/rules/conventions.mdc) | Один модуль — одна зона ответственности; KISS |
| [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) | Префикс путей **`/v1`**; реализацию `POST /v1/dialog-messages` и `POST /v1/submissions` **не** включать в эту итерацию |
| Конфигурация | [`docs/vision.md`](../../../../vision.md): **python-dotenv** + `.env`; переменные из [`.env.example`](../../../../../.env.example) уже частично объявлены |

## Архитектура каркаса (целевое состояние)

По шаблону из fastapi-templates (фабрика приложения, `lifespan`, `APIRouter`), согласованному с conventions:

```
backend/
  main.py           # create_app(), lifespan: engine/session factory, подключение к БД
  config.py         # загрузка настроек из окружения (dotenv), без секретов в логах
  api/
    __init__.py
    router.py       # APIRouter(prefix="/v1", tags=…); пока без операций или только технические
  models/
    __init__.py
    base.py         # при необходимости DeclarativeBase / общий metadata
    user.py
    flow.py
    participant.py
```

**Зависимости (черновик):** `fastapi`, `uvicorn`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `python-dotenv` — добавить в корневой [`requirements.txt`](../../../../../requirements.txt) (единый venv с ботом, как сейчас) либо отдельный файл по решению в задаче 4; в плане закрепляем **один venv + дополнение корневого `requirements.txt`**, если не возникнет причина разделить.

**Alembic:** каталог `backend/alembic/` (или `alembic/` в корне с `script_location` — предпочтительно **`backend/alembic`** рядом с приложением), `env.py` в async-режиме, `target_metadata` из declarative base моделей.

**Проверка БД при старте:** один неблокирующий запрос уровня «подключение установлено» (например `SELECT 1`) в `lifespan` с логированием успеха на `INFO` без вывода URL/пароля.

## Схема БД (первая ревизия)

Сущности строго по полям [`docs/data-model.md`](../../../../data-model.md) для **User**, **Flow**, **Participant**:

- Типы: `UUID` PK где указано; `telegram_id` — целое, nullable; даты/время — `timestamptz` или `date` по смыслу поля.
- Перечисления: роль пользователя и участника — `student` / `teacher` (имена в БД — через `Enum` PostgreSQL или строки + constraint; выбрать один стиль и зафиксировать в задаче 3).
- Связи: `Participant.user_id` → `user.id`, `Participant.flow_id` → `flow.id`; **уникальность пары** `(user_id, flow_id)` для участника одного пользователя в одном потоке.
- Именование таблиц: `users`, `flows`, `participants` (snake_case, множественное число) — если не переопределено существующим стилем в ADR.

**Вне первой ревизии:** Module, Lesson, Assignment, Submission, DialogMessage — итерации 5+ / отдельные миграции.

## Makefile и документация

Добавить цели (точные имена — в задаче 4), например:

- `run-backend` — uvicorn на `API_HOST`:`API_PORT` (импорт `backend.main:app` или фабрики — по выбранной строке запуска).
- `migrate` / `migrate-upgrade` — `alembic upgrade head` с корректным `cwd` и конфигом.

Обновить [`README.md`](../../../../../README.md): раздел «Backend (черновик)» — установка, `DATABASE_URL`, миграции, запуск; без дублирования полного OpenAPI (итерация 6).

По возможности в этой же итерации расширить **`lint`** / добавить **`lint-backend`**: `ruff check backend/` (полное объединение `make lint` — итерация 8; здесь достаточно зафиксировать цель в Makefile, если не противоречит объёму).

## Риски

- **Async Alembic:** корректная настройка `env.py` под `async_engine` — при необходимости опереться на официальные рецепты Alembic + asyncio.
- **Дублирование metadata:** одна `Base.metadata` для моделей и для autogenerate.
- **Windows / пути:** команды в README и Makefile учитывают текущий [`Makefile`](../../../../../Makefile) (`PY` для venv).

## Задачи

| Задача | Папка |
|--------|--------|
| Каркас FastAPI: фабрика, lifespan, health, роутер `/v1` | [`tasks/task-01-scaffold-fastapi/`](tasks/task-01-scaffold-fastapi/) |
| Конфиг и сессия БД (engine, `get_session`) | [`tasks/task-02-config-database-session/`](tasks/task-02-config-database-session/) |
| ORM-модели и первая миграция Alembic | [`tasks/task-03-orm-alembic/`](tasks/task-03-orm-alembic/) |
| Makefile, README, зависимости, проверка сценария запуска | [`tasks/task-04-tooling-docs/`](tasks/task-04-tooling-docs/) |

## Следующие шаги

- Итерация 4 tasklist-backend: тесты API (после появления реальных марштузов).
- Итерация 5: реализация `POST /v1/dialog-messages` и `POST /v1/submissions` по OpenAPI.
