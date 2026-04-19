# Задача 02: Практическое руководство SQLAlchemy + Alembic

**Итерация:** [iteration-3-tooling-guide](../../plan.md)

## Цель

Создать [docs/tech/sqlalchemy-alembic-guide.md](../../../../../../tech/sqlalchemy-alembic-guide.md) — краткую справку по паттернам репозитория, чтобы по одному файлу ответить на вопросы: как получить сессию в FastAPI, как прогнать миграции, как именовать ревизии, как работать с enum и seed.

## Шаги

1. **Async-сессия и DI:** описать устройство `backend/database.py` (`AsyncEngine`, `async_sessionmaker`, `session_scope()`, `init_database` / `dispose_database`) и `backend/api/deps.py` (`get_session`, `SessionDep`); пример использования в эндпоинтах.
2. **Цикл Alembic:** `alembic revision --autogenerate -m "..."`, `alembic upgrade head`, `alembic downgrade -1` / `base`; предупреждение про ограничения autogenerate (например частичные индексы).
3. **Именование ревизий:** конвенция проекта — файлы `YYYYMMDDHHMMSS_slug.py`, revision id вида `NNN_slug` (как в существующих `001_*`, `002_*`).
4. **Enum в PostgreSQL:** ссылка на [ADR-003](../../../../../../adr/adr-003-enum-strategy.md); паттерны `create_type=True` / `create_type=False` + `values_callable`; `DROP TYPE` в downgrade; кратко про добавление значений (`ALTER TYPE ... ADD VALUE`) и ограничения в транзакциях.
5. **Seed через скрипт:** паттерн `asyncio.run(main())` + прямое использование `async_sessionmaker` без FastAPI DI; ссылка на планируемый `scripts/seed_data.py` (итерация 4).
6. **Шпаргалка make:** `make migrate-upgrade`; упоминание будущих `make db-up`, `make db-seed` (итерация 4) без выдумывания несуществующих целей.

## DoD

- Файл гайда существует по указанному пути; пути к модулям и команды соответствуют репозиторию на момент написания.
- Разделы покрывают пункты из [plan.md итерации](../../plan.md) и Definition of Done в [tasklist-database.md](../../../../../../tasks/tasklist-database.md) для итерации 3.

## Зависимости

- Предпочтительно выполнять после [задачи 01](../task-01-adr-review/plan.md), чтобы в гайде была живая ссылка на ADR-003.
