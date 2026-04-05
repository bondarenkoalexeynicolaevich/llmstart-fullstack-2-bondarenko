# Задача 02: backend/tests и conftest

## Содержание

- Каталог `backend/tests/`, `conftest.py`: `DATABASE_URL` / `TEST_DATABASE_URL`, сброс кэша `get_settings`, session-scoped миграции Alembic, фикстура `TestClient`, TRUNCATE таблиц базового домена между тестами.
- Фабрики/хелпер для вставки `User`, `Flow`, `Participant` (async через `asyncio.run` или общая фикстура).

## Критерии готовности

- Изоляция тестов: пустые таблицы перед сценарием, корректный порядок FK.
