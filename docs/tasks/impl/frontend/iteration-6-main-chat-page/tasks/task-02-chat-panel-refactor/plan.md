# task-02: Рефактор ChatPanel

## Цель

`ChatPanel` — только разметка и вызовы методов из `useChatStore`.

## Действия

- Обновить [`web/components/chat-panel.tsx`](../../../../../../../web/components/chat-panel.tsx): убрать локальный state/hooks загрузки; импортировать `useChatStore`.

## DoD

- Пропсы `participantId` / `flowId` не требуются.
