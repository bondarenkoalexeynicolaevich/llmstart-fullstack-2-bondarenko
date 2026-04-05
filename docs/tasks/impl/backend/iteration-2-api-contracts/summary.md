# Итерация 2 (backend): итог

## Сделано

- Канонический контракт: [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) (см. корневой [`plan.md`](plan.md)).
- Зафиксированы `POST /v1/dialog-messages` (`200`) и `POST /v1/submissions` (`201`), envelope ошибок, коды `401`/`403`/`404`/`409`.
- Идентификация: `telegram_user_id` + `flow_id`; аутентификация сервиса: `Authorization: Bearer` + `INTERNAL_API_TOKEN`.
- [`docs/integrations.md`](../../../../integrations.md) — вызов backend из бота; [`.env.example`](../../../../../.env.example) — `INTERNAL_API_TOKEN`, `BACKEND_BASE_URL`.
- [`docs/vision.md`](../../../../vision.md) — sequenceDiagram приведены в соответствие с контрактом.

## Задачи

| Задача | Папка |
|--------|--------|
| Диалог | [`tasks/task-01-dialog-contract/`](tasks/task-01-dialog-contract/) |
| Сдачи | [`tasks/task-02-submissions-contract/`](tasks/task-02-submissions-contract/) |
| OpenAPI и документация | [`tasks/task-03-openapi-and-integrations/`](tasks/task-03-openapi-and-integrations/) |

## Отклонения от черновика

- Нет: подробный `GET` по submissions — вне MVP контракта.

## Следующий шаг

Итерация 3 tasklist-backend: каркас сервиса и миграции.
