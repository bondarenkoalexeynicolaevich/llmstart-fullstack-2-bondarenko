# Задача 01: HTTP-клиент backend

## Цель

Модуль `bot/backend_client.py`: базовый URL без хвостового слэша, заголовок `Authorization: Bearer`, разумные таймауты, `POST /v1/dialog-messages` с телом по OpenAPI.

## Состав работ

- Обернуть `httpx.AsyncClient`, метод для отправки сообщения и получения `reply_text`.
- Ошибки сети и HTTP ≠ 2xx → исключения с `status_code` и по возможности `code` из envelope `error.code` (без логирования тел ответов и `content`).
- Логи: `user_id`, события, `http_status`, `error_code` — без текста сообщения пользователя.

## DoD

- Клиент закрывается из `main` (`aclose`).
- Пользовательский текст не попадает в логи клиента.
