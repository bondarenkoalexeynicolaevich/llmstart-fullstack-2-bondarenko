# Задача: Makefile, env, README

## Цель

Единообразный запуск из корня репозитория и документация для разработчика.

## Состав

- Makefile: `web-install`, `web-dev`, `web-build`, `web-lint` (pnpm из `web/`).
- `.env.example`: `NEXT_PUBLIC_BACKEND_BASE_URL` (согласовать с `API_HOST`/`API_PORT` backend).
- `README.md`: раздел «Web (frontend)» с командами и ссылкой на tasklist.

## DoD

- Команды работают на Windows (как у пользователя) и в документации указан путь `web/`.
