# task-03: Страница чата и layout

## Цель

Подключить `ChatProvider` к защищённому layout и сверстать `/chat` под высоту основной области.

## Действия

- [`web/app/(app)/layout.tsx`](../../../../../../../web/app/(app)/layout.tsx): обернуть `AppShell` и `ChatWidgetShell` в `ChatProvider`.
- [`web/app/(app)/chat/page.tsx`](../../../../../../../web/app/(app)/chat/page.tsx): заголовок + контейнер `flex-1 min-h-0` с `ChatPanel`.
- [`web/components/app-shell.tsx`](../../../../../../../web/components/app-shell.tsx): `main` — `flex min-h-0 flex-1 flex-col`, чтобы дочерний контент мог занимать высоту.

## DoD

- На узком экране чат скроллится внутри области сообщений, не ломая шапку приложения.
