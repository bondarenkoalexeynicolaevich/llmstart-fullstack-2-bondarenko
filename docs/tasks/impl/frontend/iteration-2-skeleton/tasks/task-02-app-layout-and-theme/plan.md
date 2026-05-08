# Задача: App layout и тема

## Цель

Единый каркас UI: тёмная тема (dev-dashboard стиль), навигация между основными разделами, минимальный набор shadcn-компонентов.

## Состав

- Инициализация shadcn/ui (`components.json`, `lib/utils.ts`).
- Глобальные стили и CSS variables в `app/globals.css`.
- Layout: sidebar или top nav + контентная область.
- Маршруты-заглушки: `/dashboard`, `/leaderboard`, `/chat` (контент placeholder).

## DoD

- Все три раздела открываются из общего меню.
- Тема тёмная по умолчанию.
