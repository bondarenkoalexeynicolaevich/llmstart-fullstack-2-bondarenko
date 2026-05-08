# Итерация 4: Лидерборд — план

## Цель

Страница **`/leaderboard`**: переключатель «Таблица / Карта», данные из **`GET /v1/flows/{flow_id}/leaderboard`** (JWT, студент и преподаватель — члены потока).

## Ценность

Наглядное сравнение прогресса участников: таблица с медалями топ-3 и scatter по метаданным осей из API.

## Связанные документы

| Документ | Роль |
|----------|------|
| [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md) | Tasklist области |
| [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) | `LeaderboardResponse` |
| [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) | Auth, демо-поток |

## Задачи

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-types-api/](tasks/task-01-types-api/plan.md) | Типы OpenAPI + `fetchFlowLeaderboard` |
| 2 | [tasks/task-02-table-view/](tasks/task-02-table-view/plan.md) | Таблица, прогресс, иконки уроков, медали |
| 3 | [tasks/task-03-scatter-view/](tasks/task-03-scatter-view/plan.md) | Recharts ScatterChart, топ-3 |
| 4 | [tasks/task-04-page-smoke/](tasks/task-04-page-smoke/plan.md) | Маршрут, lint/build, tasklist |

Порядок: **1 → 2 → 3 → 4**.

## Архитектура (KISS)

- Один клиентский компонент `LeaderboardClient`, один запрос при загрузке; оба режима читают один ответ.
- Переключатель режима — локальный `useState` (без React Query).
- График: **recharts** (уже в проекте).

## Definition of Done

- Оба режима из одного ответа API; loading / empty / error + retry.
- Топ-3 с медалями в таблице; на карте — крупнее/другой цвет для rank ≤ 3.
- `npm run lint` и `npm run build` в `web/` проходят.
