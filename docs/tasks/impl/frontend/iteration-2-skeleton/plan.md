# Итерация 2: Каркас frontend-проекта — план

## Цель

Поднять в каталоге `web/` минимальный Next.js App Router-клиент: тёмная тема, навигация, вход через `POST /v1/auth/web-session` (JWT в `localStorage`), плавающая кнопка чата-заглушка, цели Makefile и документация для совместного запуска с backend.

## Ценность

Итерации 3–6 могут наполнять экраны реальными данными без переделки базового layout, auth-слоя и dev-контуров.

## Связанные документы

| Документ | Роль |
|----------|------|
| [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md) | Сводка области frontend |
| [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) | Схема `WebSessionCreate*` |
| [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) | Обзор auth и URL backend |
| [`docs/vision.md`](../../../../vision.md) | Стек web и структура репозитория |

## Задачи и порядок

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-bootstrap-web-app/](tasks/task-01-bootstrap-web-app/plan.md) | `pnpm`, Next.js, TypeScript, Tailwind |
| 2 | [tasks/task-02-app-layout-and-theme/](tasks/task-02-app-layout-and-theme/plan.md) | Layout, nav, тёмная тема, shadcn минимум |
| 3 | [tasks/task-03-web-session-auth/](tasks/task-03-web-session-auth/plan.md) | Форма входа, `web-session`, сессия в `localStorage` |
| 4 | [tasks/task-04-global-chat-widget-shell/](tasks/task-04-global-chat-widget-shell/plan.md) | FAB + панель-заглушка на всех страницах |
| 5 | [tasks/task-05-devx-docs-and-make-targets/](tasks/task-05-devx-docs-and-make-targets/plan.md) | Makefile, `.env.example`, README |

Рекомендуемый порядок: **1 → 2 → 3 → 4 → 5**.

## Границы (KISS)

- В итерации 2 **нет** полноценного чата с API (итерации 5–6).
- Нет React Query — только `fetch` + небольшие утилиты.
- JWT в **`localStorage`** для MVP; перенос в cookie — отдельная задача при ужесточении модели.

## Demo для локальной проверки входа

После `make db-seed`: преподаватель **username** `bondarenko_alexey_nikolaevich`, **flow_id** `00000000-0000-0000-0000-000000000001` (см. [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md)).

## Артефакты итерации

- Этот каталог: `plan.md`, `summary.md` (после закрытия).
- `tasks/task-NN-*/plan.md` по каждой задаче.

## Проверки

| Действие |
|----------|
| `make web-install` |
| `make web-lint` |
| `make web-build` |
| `make web-dev` + backend: вход и навигация по разделам |
