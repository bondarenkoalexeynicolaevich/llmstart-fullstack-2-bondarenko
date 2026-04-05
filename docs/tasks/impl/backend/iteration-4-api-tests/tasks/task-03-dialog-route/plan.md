# Задача 03: POST /v1/dialog-messages и LLM-порт

## Содержание

- Проверка `Authorization: Bearer` + `INTERNAL_API_TOKEN`, ответы ошибок в формате `ErrorBody` из OpenAPI.
- Роут: валидация тела, резолв `Flow` / `User` по `telegram_user_id` / `Participant`, вызов инжектируемого `LlmClient` (протокол/класс в `services/`), дефолт — «не настроено» (не фейковый ответ для прода).
- Логирование без текста пользовательского сообщения.

## Критерии готовности

- OpenAPI-коды: 401, 404 (`flow_not_found`, `participant_not_found`), 200 с обязательными полями.
