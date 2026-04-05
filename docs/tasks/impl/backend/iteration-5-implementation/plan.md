# Итерация 5: Endpoints и серверная логика

## Цель

Реализовать персистентность диалога (история + запись в БД), вызов LLM через OpenRouter, endpoint сдачи `POST /v1/submissions` по OpenAPI v1.

## Ценность

Бот (позже) получает рабочее ядро: сообщения сохраняются, ответы — от реальной модели при наличии ключа; сдачи фиксируются с проверкой задания в потоке.

## Отклонение от канонической ER (MVP)

Таблица `assignments` привязана к `flow_id` напрямую (без `Module` / `Lesson`). После появления полной структуры курса — отдельная миграция (`lesson_id`, бэкофилл).

## Задачи

| Задача | Папка |
|--------|--------|
| Миграции 002 и ORM-модели | [`tasks/task-01-migrations-models/`](tasks/task-01-migrations-models/) |
| Настройки + OpenRouter LLM | [`tasks/task-02-openrouter-config/`](tasks/task-02-openrouter-config/) |
| Сервис диалога + API | [`tasks/task-03-dialog-persist/`](tasks/task-03-dialog-persist/) |
| Submissions: схемы, роутер, сервис | [`tasks/task-04-submissions-route/`](tasks/task-04-submissions-route/) |
| Тесты, TRUNCATE, сиды | [`tasks/task-05-tests-truncate/`](tasks/task-05-tests-truncate/) |

## Definition of Done

- `make lint-backend` и `make test-backend` без регрессий (при заданной БД).
- Секреты только из env; в логах нет текста пользовательских сообщений.

## Ссылки

- Контракт: `docs/api/backend-v1.openapi.yaml`
- Принятие итерации: `summary.md` (после завершения).
