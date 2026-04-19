# Задача 04: db_inspect и README — summary

## Результат

- [`scripts/db_inspect.py`](../../../../../scripts/db_inspect.py): `COUNT(*)` по таблицам текущей схемы (`users`, `flows`, `participants`, `assignments`, `dialog_messages`, `submissions`).
- [`README.md`](../../../../../README.md): ветка «Docker Compose», команды `db-*`, ссылка на [sqlalchemy-alembic-guide.md](../../../../tech/sqlalchemy-alembic-guide.md).
- В [docs/tech/sqlalchemy-alembic-guide.md](../../../../tech/sqlalchemy-alembic-guide.md) обновлена шпаргалка Make под новые цели.

## Отклонения от плана

- Нет отдельной цели `make db-inspect`; проверка через `python scripts/db_inspect.py` (как в tasklist).
