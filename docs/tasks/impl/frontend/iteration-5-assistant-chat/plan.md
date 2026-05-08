# Итерация 5: Чат с ассистентом (контур виджета) — план

## Цель

Плавающий виджет (Sheet): загрузка истории диалога и отправка сообщений в backend (`GET`/`POST /v1/participants/{participant_id}/dialog-messages` с JWT).

## Ценность

Ассистент доступен с любой страницы приложения без смены маршрута; сохранённая история после перезагрузки.

## Связанные документы

| Документ | Роль |
|----------|------|
| [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md) | Tasklist области |
| [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) | Схемы диалога |
| [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) | Auth веб-сессии |

## Задачи

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-types-and-api/](tasks/task-01-types-and-api/plan.md) | Типы и `fetchDialogMessages` / `postDialogMessage` |
| 2 | [tasks/task-02-chat-panel/](tasks/task-02-chat-panel/plan.md) | `ChatPanel`: история, optimistic UI, состояния |
| 3 | [tasks/task-03-widget-integration/](tasks/task-03-widget-integration/plan.md) | Подключение к `ChatWidgetShell`, guard сессии |
| 4 | [tasks/task-04-smoke-docs/](tasks/task-04-smoke-docs/plan.md) | Документация итерации, tasklist, lint/build |

Порядок: **1 → 2 → 3 → 4**.

## Архитектура (KISS)

- Запросы через существующий [`web/lib/api/client.ts`](../../../../../web/lib/api/client.ts) (`apiFetch`), без React Query.
- `ChatPanel` монтируется только при открытом Sheet (ленивая загрузка истории).
- Страница `/chat` — итерация 6; здесь только виджет.

## Ограничения API (MVP)

Первая страница `GET` отдаёт до `limit` сообщений с начала истории (порядок `created_at` asc). Для длинной истории полная подгрузка «последних N» — в итерации 6 / доработка пагинации.

## Definition of Done

- Отправка сохраняется на backend; после F5 история совпадает с сервером (в пределах текущей страницы списка).
- Нет `console.log` текста сообщений.
- `npm run lint` и `npm run build` в `web/` проходят.
