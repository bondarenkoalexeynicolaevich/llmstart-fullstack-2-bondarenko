# task-01: ChatContext — summary

**Статус:** Done

## Результат

- Добавлен [`web/lib/chat-context.tsx`](../../../../../../web/lib/chat-context.tsx): `ChatProvider`, `useChatStore`, тип `ChatStore`.
- Идентификаторы участника и потока читаются из `getSession()` через lazy `useState` при монтировании (без `setState` в эффекте чтения сессии — требование ESLint).
- Логика загрузки истории, отправки, черновика и `useOnline` сосредоточена в провайдере.

## Отклонения от плана

- Нет.
