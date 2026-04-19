# Задача 02: цели Makefile `db-*`

## Что делаем

Добавить в корневой **[`Makefile`](../../../../../Makefile)** цели:

| Цель | Поведение |
|------|-----------|
| `db-up` | `docker compose up -d` для сервиса БД |
| `db-down` | `docker compose down` |
| `db-reset` | `docker compose down -v`, затем `db-up`, затем `migrate-upgrade` |
| `db-shell` | интерактивный `psql` в контейнере (пользователь/БД по умолчанию из примера) |
| `db-logs` | `docker compose logs -f db` |
| `db-status` | `alembic current` с `backend/alembic.ini` |
| `db-seed` | `$(PY) scripts/seed_data.py` |

Обновить `.PHONY` и сохранить совместимость с Windows (`ifeq ($(OS),Windows_NT)` для `PY`).

## Критерии готовности

- Команды документированы в README (задача 04).
