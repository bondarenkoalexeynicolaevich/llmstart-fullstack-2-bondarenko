# Итерация 6: Чат в основной области — план

## Цель

Страница `/chat` с тем же диалогом, что и в плавающем виджете: общая история и черновик через React Context внутри `(app)`.

## Ценность

Два UX-контура (виджет и полноэкранная страница) не расходятся; навигация не дублирует загрузку с сервера для двух независимых экземпляров UI.

## Связанные документы

| Документ | Роль |
|----------|------|
| [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md) | Tasklist области |
| [`docs/tasks/impl/frontend/iteration-5-assistant-chat/summary.md`](../iteration-5-assistant-chat/summary.md) | Базовый `ChatPanel` и API диалога |
| [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) | JWT и `/v1/participants/.../dialog-messages` |

## Задачи

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-chat-context/](tasks/task-01-chat-context/plan.md) | `ChatProvider`, `useChatStore`, перенос логики из панели |
| 2 | [tasks/task-02-chat-panel-refactor/](tasks/task-02-chat-panel-refactor/plan.md) | `ChatPanel` только UI поверх контекста |
| 3 | [tasks/task-03-chat-page-layout/](tasks/task-03-chat-page-layout/plan.md) | `/chat`, `(app)/layout`, `AppShell` main как flex-колонка |
| 4 | [tasks/task-04-smoke-docs/](tasks/task-04-smoke-docs/plan.md) | Lint/build, summary, tasklist |

Порядок: **1 → 2 → 3 → 4**.

## Архитектура (KISS)

- Один `ChatProvider` в [`web/app/(app)/layout.tsx`](../../../../../web/app/(app)/layout.tsx) внутри `SessionGate`.
- Состояние чата (сообщения, загрузка, отправка, draft, online) — в [`web/lib/chat-context.tsx`](../../../../../web/lib/chat-context.tsx).
- [`web/components/chat-widget-shell.tsx`](../../../../../web/components/chat-widget-shell.tsx): без передачи `participantId`/`flowId` в панель.

## Definition of Done

- На `/chat` видна полноценная переписка; отправка с страницы сразу отражается в открытом виджете и наоборот.
- `npm run lint` и `npm run build` в `web/` проходят.
