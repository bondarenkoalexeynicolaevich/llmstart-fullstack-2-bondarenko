# task-01: ChatContext

## Цель

Вынести состояние и побочные эффекты чата из `ChatPanel` в провайдер с хуком `useChatStore`.

## Действия

- Новый файл [`web/lib/chat-context.tsx`](../../../../../../../web/lib/chat-context.tsx): `useOnline`, `loadHistory`, `send`, тип `ChatStore`, `ChatProvider`, `useChatStore`.
- Читать `participant_id` и `flow_id` из `getSession()` в `useEffect` после монтирования.

## DoD

- При отсутствии сессии в хранилище контекст не падает (редкий случай вне `SessionGate`).
- Нет `console.log` текста сообщений.
