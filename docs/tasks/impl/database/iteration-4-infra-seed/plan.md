# Итерация 4: Инфраструктура БД, seed, проверка

## Цель

Воспроизводимо поднимать PostgreSQL (Docker), накатывать миграции, сидировать БД из `data/progress-import.v1.json` и проверять наполнение.

## Ценность

Любой разработчик может поднять стенд «с нуля» без ручного создания строк в таблицах.

## Состав работ

1. **docker-compose** — сервис `db` (PostgreSQL 16), volume, healthcheck; согласование с `.env.example`.
2. **Makefile** — `db-up`, `db-down`, `db-reset`, `db-shell`, `db-logs`, `db-status`, `db-seed`.
3. **Seed** — `data/progress-import.v1.json` (формат задокументирован в файле `_note` + этот план) и `scripts/seed_data.py` (async SQLAlchemy, идемпотентные вставки по `id`).
4. **Проверка** — `scripts/db_inspect.py` (COUNT по таблицам), обновление `README.md`.

## Ограничения схемы (до migration 003)

Сид под **текущие** миграции `001` + `002`: таблицы `users`, `flows`, `participants`, `assignments` (**`flow_id`**), `dialog_messages`, `submissions`. Таблиц `modules` / `lessons` в БД ещё нет.

**После migration 003** (итерация 5): обновить структуру JSON (`modules`, `lessons`, `assignments.lesson_id`) и скрипт импорта.

## Задачи

| Задача | Папка | Содержание |
|--------|-------|------------|
| 01 | [tasks/task-01-docker-env](tasks/task-01-docker-env/) | `docker-compose.yml`, `.env.example` |
| 02 | [tasks/task-02-makefile](tasks/task-02-makefile/) | цели `db-*` в `Makefile` |
| 03 | [tasks/task-03-seed](tasks/task-03-seed/) | JSON + `scripts/seed_data.py` |
| 04 | [tasks/task-04-inspect-readme](tasks/task-04-inspect-readme/) | `db_inspect.py`, README |

## Ссылки

- [tasklist-database.md](../../../tasklist-database.md)
- [docs/data-model.md](../../../../data-model.md)
- [docs/tech/sqlalchemy-alembic-guide.md](../../../../tech/sqlalchemy-alembic-guide.md)
