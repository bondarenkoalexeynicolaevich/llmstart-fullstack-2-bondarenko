# Итерация 3: Панель преподавателя — план

## Цель

Заменить заглушку [`web/app/(app)/dashboard/page.tsx`](../../../../../web/app/(app)/dashboard/page.tsx) полноценным экраном: KPI, график активности за 14 дней, лента вопросов и сдач с пагинацией, матрица прогресса — **из реального backend API** (JWT, роль `teacher`).

## Ценность

Преподаватель видит сводку потока в браузере без Telegram и без моков; клиент готов к итерации 4 (лидерборд переиспользует те же паттерны fetch + состояния).

## Связанные документы

| Документ | Роль |
|----------|------|
| [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md) | Сводка области frontend |
| [`docs/tasks/impl/frontend/iteration-0-ui-api-contracts/tasks/task-01-teacher-dashboard-spec/plan.md`](../iteration-0-ui-api-contracts/tasks/task-01-teacher-dashboard-spec/plan.md) | UX и состав виджетов |
| [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) | Схемы `TeacherDashboardResponse`, лент, матрицы |
| [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) | Auth, URL backend, демо-поток |

## Маршрут и доступ

- **Путь UI:** остаётся **`/dashboard`** в группе `(app)` — уже есть редирект с `/` ([`web/app/page.tsx`](../../../../../web/app/page.tsx)).
- **Защита:** layout `(app)` + [`SessionGate`](../../../../../web/components/session-gate.tsx); JWT и `flow_id` из [`web/lib/session`](../../../../../web/lib/session.ts) (итерация 2).
- **Роль:** endpoint-ы дашборда требуют участника с ролью `teacher`. Если в сессии `role !== teacher` — не дергать teacher-only API; показать понятное сообщение и/или ссылку на другие разделы (без утечки внутренних деталей).

## Задачи и порядок

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-dashboard-route-and-data-contracts/](tasks/task-01-dashboard-route-and-data-contracts/plan.md) | Маршрут, проверка роли, модуль API + типы ответов |
| 2 | [tasks/task-02-kpi-and-activity-chart/](tasks/task-02-kpi-and-activity-chart/plan.md) | 4 KPI + линейный график (14 точек) |
| 3 | [tasks/task-03-questions-feed/](tasks/task-03-questions-feed/plan.md) | Таблица вопросов + cursor-пагинация |
| 4 | [tasks/task-04-submissions-feed-and-details/](tasks/task-04-submissions-feed-and-details/plan.md) | Лента сдач + Sheet/модалка деталей |
| 5 | [tasks/task-05-progress-matrix-and-states/](tasks/task-05-progress-matrix-and-states/plan.md) | Матрица, tooltip, горизонтальный скролл |
| 6 | [tasks/task-06-smoke-docs-and-acceptance/](tasks/task-06-smoke-docs-and-acceptance/plan.md) | Smoke, README, skill review, критерии приёмки |

Рекомендуемый порядок: **1 → 2 → 3 → 4 → 5 → 6**.

## Архитектура клиента (KISS)

- **Без React Query** на этой итерации: обёртка над `fetch` (например `web/lib/api/dashboard.ts` или единый `web/lib/api/client.ts`) + явные состояния в компонентах.
- **Типы:** руками по OpenAPI-схемам (или минимальные type aliases), без генератора на этом этапе.
- **Компоненты:** по возможности маленькие client-компоненты для данных (`"use client"`), без лишнего глобального state.
- **График:** добавить **`recharts`** (в проекте его ещё нет — см. [`web/package.json`](../../../../../web/package.json)); альтернативы только если появятся технические блокеры.

## Общие состояния UI

Для каждого блока (KPI+график; вопросы; сдачи; матрица):

| Состояние | Поведение |
|-----------|-----------|
| loading | skeleton / spinner без «прыжков» layout |
| empty | осмысленный текст (где применимо: ленты, матрица без студентов) |
| error | inline alert/banner + **retry**; при `401` — очистка сессии и переход на `/login` |

Формат ошибок API: тело `ErrorBody` из OpenAPI (`error.code`, `error.message`).

## Definition of Done (итерация)

- Все виджеты из спеки ит. 0 заполнены данными с backend на демо-сиде ([`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md)).
- Пагинация лент: `limit` / `cursor` / `next_cursor` как в контракте.
- Клик по строке сдачи открывает детали с `comment` и `materials[]`.
- Матрица: tooltip/hover с уроком, статусом и датой; горизонтальный скролл + закрепление колонки имени (best-effort на CSS).
- `make web-lint`, `make web-build` проходят.
- Отклонения от контракта — правка [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) и заметка в [`summary.md`](summary.md).

## Локальный smoke

1. `make migrate-upgrade` и `make db-seed` (или `make db-seed-frontend-demo`).
2. `make run-backend`, `make web-dev`.
3. Логин преподавателя: username и `flow_id` из [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md).
4. Открыть `/dashboard`: KPI, график, обе ленты (подгрузка следующей страницы), клик по сдаче, матрица.

## Артефакты

- Этот каталог: [`plan.md`](plan.md), [`summary.md`](summary.md) (после закрытия реализации).
- `tasks/task-NN-*/plan.md` и после задач — `summary.md`.
