# SQLAlchemy async и Alembic в этом репозитории

Краткая справка по тому, как устроены сессии БД, DI в FastAPI и миграции. Детали выбора стека — [ADR-002](../adr/adr-002-backend-http-orm.md); стратегия enum в PostgreSQL — [ADR-003](../adr/adr-003-enum-strategy.md).

## Async-движок и сессия

- **`backend/database.py`** — глобальные `AsyncEngine` и `async_sessionmaker`, инициализируются один раз в `init_database(database_url)` из lifespan приложения.
- **`session_scope()`** — async context manager: открывает сессию и отдаёт её в `yield`; после выхода из блока сессия закрывается. Пока не вызван `init_database`, обращение к движку/сессии приведёт к `RuntimeError`.

**Lifespan** (`backend/main.py`): при старте — `init_database(settings.database_url)`, проверка `SELECT 1`, при остановке — `await dispose_database()`.

## FastAPI: зависимость сессии

- **`backend/api/deps.py`**: `get_session()` асинхронно отдаёт сессию через `async with session_scope() as session: yield session`.
- **`SessionDep`** — `Annotated[AsyncSession, Depends(get_session)]`; в эндпоинтах объявляют `session: SessionDep` (см. `backend/api/dialog.py`, `backend/api/submissions.py`).

Коммит: по необходимости явно `await session.commit()` в сервисном коде после операций записи; при исключении до коммита транзакция откатится при закрытии сессии (в зависимости от настроек — по умолчанию для типичного use-case достаточно не коммитить при ошибке).

## Alembic: конфигурация и цикл

Конфиг: **`backend/alembic.ini`**, скрипты: **`backend/alembic/`**, метаданные моделей подхватываются из `backend.models.Base` в `env.py` (async-миграции).

Команды выполнять **из корня репозитория**, указывая конфиг:

```bash
# применить все миграции
.venv/Scripts/python.exe -m alembic -c backend/alembic.ini upgrade head
```

Или через Make (см. ниже).

Полезные шаги:

| Действие | Команда (корень репо) |
|----------|------------------------|
| Новая ревизия с автогенерацией по diff моделей | `python -m alembic -c backend/alembic.ini revision --autogenerate -m "краткое описание"` |
| Применить миграции | `python -m alembic -c backend/alembic.ini upgrade head` |
| Откат на одну ревизию | `python -m alembic -c backend/alembic.ini downgrade -1` |
| Откат к пустой схеме | `python -m alembic -c backend/alembic.ini downgrade base` |

**Autogenerate** не гарантирует полноту: частичные индексы, некоторые изменения constraints, ручные правки enum — всегда просматривайте сгенерированный файл и при необходимости дополняйте вручную.

## Именование ревизий

- **Имя файла:** `YYYYMMDDHHMMSS_slug.py` (например `20260405120000_initial_user_flow_participant.py`).
- **Revision ID** внутри файла — короткий стабильный идентификатор, в проекте уже встречается вид **`NNN_slug`** (например `001_initial`, `002_dialog_submissions`, `003_modules_lessons`, `004_knowledge_progress`), поле `revises` / `down_revision` ссылается на него.

Новую ревизию после автогенерации стоит переименовать файл и привести `revision` к принятому в репо стилю, если это требуется правилами команды.

## Enum в PostgreSQL

См. [ADR-003](../adr/adr-003-enum-strategy.md). В миграциях — `sqlalchemy.dialects.postgresql.ENUM`; в моделях — `SAEnum(EnumClass, name="…", native_enum=True)` рядом с `enum.Enum` в `backend/models/enums.py`.

Паттерны из существующих ревизий:

- первое создание типа: `create_type=True`;
- второе использование того же `name` в одной ревизии: `create_type=False` и `values_callable` (пример — `member_role` / `member_role_existing` в первой миграции);
- в `downgrade`: `DROP TYPE IF EXISTS …` после удаления таблиц, которые этот тип используют.

Добавление нового значения к существующему типу — отдельная миграция с `ALTER TYPE … ADD VALUE`; учитывайте ограничения PostgreSQL на выполнение в транзакции для вашей версии СУБД.

## Seed и скрипты

- **`scripts/seed_data.py`** — импорт из [`data/progress-import.v1.json`](../../data/progress-import.v1.json): `asyncio.run`, `init_database` / `session_scope` из [`backend/database.py`](../../backend/database.py), URL из `get_settings()` (корневой `.env`). Запуск: **`make db-seed`**.
- **`scripts/db_inspect.py`** — сводка `COUNT(*)` по таблицам; для проверки после seed.

Паттерн: настройки из env **без** FastAPI `Depends`, вставки в async-функции.

## Шпаргалка Make

| Цель | Команда |
|------|---------|
| Накатить миграции | `make migrate-upgrade` |
| Поднять Postgres (compose) | `make db-up` |
| Остановить compose | `make db-down` |
| Сброс volume + миграции | `make db-reset` |
| psql в контейнере | `make db-shell` |
| Логи сервиса `db` | `make db-logs` |
| Текущая ревизия Alembic | `make db-status` |
| Seed из `data/progress-import.v1.json` | `make db-seed` |

`migrate-upgrade` вызывает: `$(PY) -m alembic -c backend/alembic.ini upgrade head` (см. `Makefile`). Переменные `POSTGRES_*` и пример `DATABASE_URL` — в `.env.example`, порядок «с нуля» — в [README.md](../../README.md).
