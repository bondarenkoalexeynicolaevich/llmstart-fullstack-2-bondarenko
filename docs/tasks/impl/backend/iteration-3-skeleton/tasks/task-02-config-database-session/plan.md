# Задача 02: конфигурация и async-сессия БД

## Цель

Реализовать **`backend/config.py`**: загрузка из окружения через **python-dotenv** (как в [`docs/vision.md`](../../../../../../vision.md)) — минимум `DATABASE_URL`, `API_HOST`, `API_PORT`, `INTERNAL_API_TOKEN` (последний для будущей проверки Bearer; в каркасе можно только читать, без middleware).

Настроить **async engine** и **async_sessionmaker** (SQLAlchemy 2.x), зависимость **`get_session`** (генератор с `yield` и корректным закрытием).

Интегрировать в **`lifespan`** в `main.py`: создание engine при старте, **проверка подключения** (например `conn.execute(text("SELECT 1"))`), лог `INFO` об успешном старте без секретов; на shutdown — `dispose()` engine.

## Файлы

- `backend/config.py`
- правки `backend/main.py` — импорт настроек, `lifespan`, опционально `Annotated` alias для сессии в `api/deps.py` при появлении файла

## Критерии готовности

- При невалидном / недоступном `DATABASE_URL` приложение падает при старте с понятной ошибкой (без вывода пароля в лог).
- Одна точка конфигурации; значения читаются из `.env` через dotenv.

## Не входит

- Репозитории, сервисы, бизнес-запросы к таблицам (кроме smoke `SELECT 1`).
