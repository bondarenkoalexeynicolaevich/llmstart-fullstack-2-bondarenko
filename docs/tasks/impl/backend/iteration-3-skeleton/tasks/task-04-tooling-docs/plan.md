# Задача 04: зависимости, Makefile, README

## Цель

- Добавить зависимости backend в **`requirements.txt`** (или согласованный альтернативный манифест): FastAPI, uvicorn, SQLAlchemy asyncio, asyncpg, Alembic, при необходимости совместимость версий с Python 3.12+.
- Расширить **[`Makefile`](../../../../../../Makefile)**:
  - `run-backend` — запуск uvicorn (host/port из env или разумные дефолты);
  - цель для миграций, например `migrate-upgrade` — вызов Alembic `upgrade head` с рабочим каталогом и конфигом.
- Обновить **[`README.md`](../../../../../../README.md)**: краткий подраздел Backend — установка, настройка `DATABASE_URL`, порядок «миграции → запуск», отсылка к OpenAPI после реализации endpoint’ов.
- Проверить **[`.env.example`](../../../../../../.env.example)**: все используемые переменные backend с комментариями (дополнить при появлении новых, например `LOG_LEVEL` для backend если отличается от бота — опционально).

## Критерии готовности

- Новый разработчик по README выполняет: venv → install → `.env` → create DB → migrate → run-backend.
- `ruff check backend/` проходит для добавленного кода (если в этой итерации добавлена цель `lint-backend`, задокументировать её).

## Не входит

- CI, pre-commit, агрегат `make lint` по всему монорепо (итерация 8).
