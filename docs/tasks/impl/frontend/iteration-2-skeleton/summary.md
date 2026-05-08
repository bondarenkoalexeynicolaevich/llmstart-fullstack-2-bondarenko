# Итерация 2: Каркас frontend-проекта — summary

**Статус:** ✅ завершена.

## Ценность

В репозитории есть запускаемый `web/`-клиент (Next.js App Router, TypeScript, Tailwind, shadcn/ui): навигация, тёмная тема, вход через backend JWT, плавающий каркас чата, цели Makefile и инструкции в README.

## Реализовано

- Каталог **`web/`** с dev/build/lint через **`make web-*`** (npm из корня; при желании — pnpm в `web/` по [vision](../../../../vision.md)).
- **`NEXT_PUBLIC_BACKEND_BASE_URL`** — базовый URL API для браузера (`web/.env.local`).
- Экран **входа**: `telegram_username`, `flow_id` → `POST /v1/auth/web-session` с сохранением JWT и полей сессии в `localStorage`.
- Защищённые маршруты через layout: редирект на `/login` без токена.
- Компоненты: **`AppShell`** (sidebar + header), **`ChatWidgetShell`** (FAB + Sheet).
- **CORS** в backend ([`backend/main.py`](../../../../../backend/main.py), [`CORS_ORIGINS`](../../../../../.env.example)) для origin dev-сервера Next.js.
- Обновлены **[`Makefile`](../../../../../Makefile)**, **[`.env.example`](../../../../../.env.example)**, **[`README.md`](../../../../../README.md)**.

## Интеграция с API

- Вход: [`WebSessionCreateRequest/Response`](../../../../api/backend-v1.openapi.yaml) — без Bearer.
- Остальные вызовы итераций 3+ — с `Authorization: Bearer <JWT>` (реализуются позже).

## Локальный smoke

1. `make run-backend` (БД и seed по README).
2. `make web-install && make web-dev`.
3. Открыть `/login`, ввести demo username и flow_id, убедиться в редиректе на `/dashboard` и работе «Выход».

## Задачи

| Задача | Результат |
|--------|-----------|
| task-01-bootstrap-web-app | [plan](tasks/task-01-bootstrap-web-app/plan.md), [summary](tasks/task-01-bootstrap-web-app/summary.md) |
| task-02-app-layout-and-theme | [plan](tasks/task-02-app-layout-and-theme/plan.md), [summary](tasks/task-02-app-layout-and-theme/summary.md) |
| task-03-web-session-auth | [plan](tasks/task-03-web-session-auth/plan.md), [summary](tasks/task-03-web-session-auth/summary.md) |
| task-04-global-chat-widget-shell | [plan](tasks/task-04-global-chat-widget-shell/plan.md), [summary](tasks/task-04-global-chat-widget-shell/summary.md) |
| task-05-devx-docs-and-make-targets | [plan](tasks/task-05-devx-docs-and-make-targets/plan.md), [summary](tasks/task-05-devx-docs-and-make-targets/summary.md) |

## Отложенное

- HttpOnly cookie для JWT, refresh — вне scope итерации 2.
- Реальная история/отправка в виджете — итерации 5–6.
