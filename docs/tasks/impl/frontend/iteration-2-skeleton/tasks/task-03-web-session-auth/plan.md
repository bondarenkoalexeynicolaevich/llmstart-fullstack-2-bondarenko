# Задача: Вход через web-session

## Цель

Реализовать MVP-авторизацию веб-клиента согласно OpenAPI: `POST /v1/auth/web-session`.

## Состав

- Страница `/login`: поля `telegram_username`, `flow_id` (UUID).
- Клиентский `fetch` на `{NEXT_PUBLIC_BACKEND_BASE_URL}/v1/auth/web-session` с JSON телом.
- Сохранение в `localStorage`: `access_token`, `user_id`, `participant_id`, `role`, `display_name`, `flow_id`, `expires_in` (опционально метка времени).
- Кнопка «Выход» — очистка storage и редирект на `/login`.
- Layout защищённых страниц: при отсутствии токена — редирект на `/login`.

## DoD

- Успешный логин с демо-данными из `docs/tech/api-contracts.md`.
- Ошибки API показываются пользователю кратко (без логирования секретов).
