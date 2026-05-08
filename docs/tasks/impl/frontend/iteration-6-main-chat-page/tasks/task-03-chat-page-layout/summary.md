# task-03: Страница чата и layout — summary

**Статус:** Done

## Результат

- [`web/app/(app)/layout.tsx`](../../../../../../web/app/(app)/layout.tsx): `SessionGate` → `ChatProvider` → `AppShell` + `ChatWidgetShell`.
- [`web/app/(app)/chat/page.tsx`](../../../../../../web/app/(app)/chat/page.tsx): клиентская страница с заголовком и контейнером `flex-1 min-h-0` для `ChatPanel`.
- [`web/components/app-shell.tsx`](../../../../../../web/components/app-shell.tsx): у `main` добавлены `flex min-h-0 flex-col` для вертикального flex-потока дочерних страниц.

## Отклонения от плана

- Нет.
