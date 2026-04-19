# Задача 04: `db_inspect.py` и README

## Что делаем

- **`scripts/db_inspect.py`** — подключение по `DATABASE_URL`, вывод `COUNT(*)` по таблицам: `users`, `flows`, `participants`, `assignments`, `dialog_messages`, `submissions`.
- **[`README.md`](../../../../../README.md)** — подраздел про локальную БД: `db-up` → `migrate-upgrade` → `db-seed` → проверка (`db_inspect` / `db-shell`), ссылка на [sqlalchemy-alembic-guide.md](../../../../tech/sqlalchemy-alembic-guide.md) при необходимости.

## Критерии готовности

- Новый пользователь может пройти сценарий из README без догадок про порядок команд.
