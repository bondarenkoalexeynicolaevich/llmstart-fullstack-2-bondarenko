# Задача 01: docker-compose и переменные окружения — summary

## Результат

- Добавлен [`docker-compose.yml`](../../../../../docker-compose.yml): сервис `db` (`postgres:16`), volume `pgdata`, проброс порта `${POSTGRES_PORT:-5432}:5432`, `healthcheck` через `pg_isready` с переменными контейнера (`$$POSTGRES_*`).
- Обновлён [`.env.example`](../../../../../.env.example): блок `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, опциональный `POSTGRES_PORT`, пример `DATABASE_URL` под локальный compose.

## Отклонения от плана

- Порт хоста вынесен в `POSTGRES_PORT` (по умолчанию 5432), чтобы при занятом порту можно было сменить без правки compose вручную.
