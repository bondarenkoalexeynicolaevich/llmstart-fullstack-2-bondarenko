# Задача 01: docker-compose и переменные окружения

## Что делаем

- Добавить **`docker-compose.yml`** в корень: сервис `db`, образ `postgres:16`, порты `5432:5432`, именованный volume для данных, `healthcheck` через `pg_isready`.
- Расширить **[`.env.example`](../../../../../.env.example)**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, пример **`DATABASE_URL`** для подключения к этому контейнеру (`postgresql+asyncpg://…`).

## Критерии готовности

- `docker compose config` валиден.
- Значения по умолчанию согласованы между compose и примером строки подключения.
