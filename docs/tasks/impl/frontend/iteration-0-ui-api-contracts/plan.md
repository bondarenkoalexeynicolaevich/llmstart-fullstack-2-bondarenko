# Итерация 0: Требования к UI и API-контракты — план

## Цель

Зафиксировать функциональные требования к четырём зонам веб-клиента, визуальный стиль, вход без OAuth по Telegram username и черновик REST API, достаточный для реализации экранов в итерациях 1–6.

## Ценность

Backend может стартовать итерацию 1 без уточнений в чате: пути, поля JSON, пагинация и ошибки согласованы с [`docs/data-model.md`](../../../data-model.md) и расширяют [`docs/api/backend-v1.openapi.yaml`](../../../api/backend-v1.openapi.yaml).

## Задачи

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-teacher-dashboard-spec/](tasks/task-01-teacher-dashboard-spec/plan.md) | Экран панели преподавателя: KPI, график, вопросы, сдачи, матрица |
| 2 | [tasks/task-02-leaderboard-spec/](tasks/task-02-leaderboard-spec/plan.md) | Лидерборд: таблица и scatter |
| 3 | [tasks/task-03-chat-spec/](tasks/task-03-chat-spec/plan.md) | Плавающий чат и страница «Чат» |
| 4 | [tasks/task-04-style-and-login/](tasks/task-04-style-and-login/plan.md) | Тема tbench-like, `/login`, сессия |
| 5 | [tasks/task-05-api-contracts/](tasks/task-05-api-contracts/plan.md) | Сводка HTTP: схемы, ошибки, связь с OpenAPI |

## Артефакты

- Этот каталог: `plan.md`, `summary.md` (после закрытия итерации).
- Дополнения к [`docs/api/backend-v1.openapi.yaml`](../../../api/backend-v1.openapi.yaml).
- При необходимости: короткое уточнение Web-стека в [`docs/vision.md`](../../../vision.md); ссылка на [`docs/tasks/tasklist-frontend.md`](../../tasklist-frontend.md) из [`docs/plan.md`](../../../plan.md), если дорожная карта ссылается только на `tasklist-web.md`.

## Согласование с доменной моделью

| UI / API | Сущности данных |
|----------|-----------------|
| Участники, роли | `User`, `Participant`, `Flow` |
| Сдачи, статусы | `Submission`, `Assignment`, `Lesson`, `Module` |
| Прогресс по ячейкам | VIEW `participant_assignment_progress` + денормализация для API при необходимости |
| Вопросы и ответы в ленте | Пары `DialogMessage` (`role`: user + assistant), группировка по `created_at` |
| Материалы в деталях сдачи | `Material` по `lesson_id` цепочки сдачи |

## Риски и открытые решения (итерация 1)

- Резолв пользователя по **username** Telegram без Bot API: допустимо хранить `telegram_username` в `users` или маппинг через seed; если поля нет — миграция в итерации 1 (зафиксировать в backend tasklist).
- Определение «активных студентов» и «вопросов за период» — бизнес-правила в итерации 1 (здесь зафиксированы только поля API).

## Файлы, которые будут затронуты документацией

- [`docs/api/backend-v1.openapi.yaml`](../../../api/backend-v1.openapi.yaml) — новые пути и схемы.
- Возможно [`docs/vision.md`](../../../vision.md) — таблица Web.
- Возможно [`docs/plan.md`](../../../plan.md) — ссылка на `tasklist-frontend.md`.
- Возможно [`README.md`](../../../../README.md) — упоминание веб-клиента и pnpm (если ещё не отражено).
