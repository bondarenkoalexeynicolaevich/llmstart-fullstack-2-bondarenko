# Итерация 4: Инфраструктура БД, seed, проверка — summary

## Что сделано

- **Docker:** `docker-compose.yml` (Postgres 16, volume, healthcheck), согласование с `.env.example`.
- **Make:** `db-up`, `db-down`, `db-reset`, `db-shell`, `db-logs`, `db-status`, `db-seed`.
- **Данные:** `data/progress-import.v1.json` под миграции `001`+`002` (`assignments.flow_id`), `scripts/seed_data.py` (async, идемпотентно по `id`).
- **Проверка:** `scripts/db_inspect.py`; README и `docs/tech/sqlalchemy-alembic-guide.md` обновлены.

## Отклонения от исходного плана

- В tasklist фигурировали «2 модуля / 3 занятия» — в текущей БД до migration 003 нет таблиц `modules`/`lessons`; seed отражает минимум по фактической схеме (1 поток, 5 заданий, 2 студента с разным прогрессом). После `003` — расширить JSON и скрипт (итерация 5 / database).

## Проверка (ручная)

1. `make db-reset` или `make db-up` → `make migrate-upgrade` → `make db-seed`.
2. `python scripts/db_inspect.py` — ненулевые счётчики в `users`, `flows`, `participants`, `assignments`, `submissions`.
3. `make db-status` — актуальная ревизия Alembic.
