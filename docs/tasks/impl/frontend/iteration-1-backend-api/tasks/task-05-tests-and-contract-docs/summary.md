# Задача 05: Тесты и документация — summary

## Тесты

- Расширены/добавлены сценарии в `backend/tests/test_web_iteration1.py` (web-session, запрет internal token и студента на дашборд, лидерборд, POST/GET диалога с подменой LLM).
- Хелпер `seed_flow_teacher_student_for_web` в `backend/tests/conftest.py`.
- Команды: `make lint-backend`, `make test-backend` должны завершаться без ошибок после `.env` с валидным `DATABASE_URL` / `INTERNAL_API_TOKEN` (для локального секрета JWT см. [`backend/config.py`](../../../../../../../backend/config.py)).

## Документы

| Файл | Назначение |
|------|-------------|
| [`docs/tech/api-contracts.md`](../../../../../../tech/api-contracts.md) | Обзор API, авторизация, таблица путей, демо-данные |
| [`docs/integrations.md`](../../../../../../integrations.md) | JWT переменные в блоке переменных backend |
| [`.env.example`](../../../../../../../.env.example) | `JWT_SECRET`, `JWT_EXPIRES_IN_SECONDS` |

## Принципы api-design-principles

Ресурсные имена и коды ошибок следуют каноническому OpenAPI. Специальных «исключений» из навыка нет; **осознанная политика**: отказ `INTERNAL_API_TOKEN` на веб-JWT-маршрутах для уменьшения площади атаки — описана в `api-contracts.md`.
