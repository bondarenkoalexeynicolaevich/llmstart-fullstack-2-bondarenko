# Итерация 1: Backend API для frontend — план

## Цель

Реализовать в backend HTTP API и данные, достаточные для экранов итераций 3–6 (дашборд преподавателя, лидерборд, чат виджет/страница) по каноническому контракту без договорённостей «в чате».

## Ценность

Веб-клиент (итерации 2+) может перейти от моков к реальному API: те же пути, схемы и коды ошибок, что в [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml).

## Связанные документы

| Документ | Роль |
|----------|------|
| [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) | Канонический OpenAPI |
| [`docs/data-model.md`](../../../../data-model.md) | Сущности и VIEW прогресса |
| [`docs/integrations.md`](../../../../integrations.md) | Токены бота/JWT веб-сессии |
| [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md) | Человекочитаемое описание (синхронизировать после реализации) |
| [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md) | Сводка области frontend |

## Задачи и порядок

| # | Папка | Содержание |
|---|--------|------------|
| 1 | [tasks/task-01-data-gap-analysis/](tasks/task-01-data-gap-analysis/plan.md) | Пробелы БД/username, индексы, согласование с OpenAPI |
| 2 | [tasks/task-02-dashboard-feed-matrix-api/](tasks/task-02-dashboard-feed-matrix-api/plan.md) | `dashboard`, ленты вопросов/сдач, матрица |
| 3 | [tasks/task-03-leaderboard-and-dialog-api/](tasks/task-03-leaderboard-and-dialog-api/plan.md) | Лидерборд и веб-диалог (`GET`/`POST` по participant) |
| 4 | [tasks/task-04-migrations-and-seed/](tasks/task-04-migrations-and-seed/plan.md) | Alembic, demo-seed, teacher `telegram_id=459032551` |
| 5 | [tasks/task-05-tests-and-contract-docs/](tasks/task-05-tests-and-contract-docs/plan.md) | Тесты, `lint`/`test`, актуализация `docs/tech/` |

Рекомендуемый порядок выполнения: **1 → 4 (частично, если нужны колонки) → 2 → 3 → 4 (seed) → 5**. Если миграции не нужны после анализа, задачи 4 сужаются до seed.

## Эндпоинты (ожидание итерации 1)

Реализация или явное откладывание с причиной в итоговом `summary.md`:

| Метод | Путь | Назначение |
|-------|------|------------|
| POST | `/v1/auth/web-session` | JWT по `telegram_username` + `flow_id` |
| GET | `/v1/flows/{flow_id}/dashboard` | KPI + 14 дней активности (teacher) |
| GET | `/v1/flows/{flow_id}/questions` | Лента вопросов, cursor |
| GET | `/v1/flows/{flow_id}/submissions` | Лента сдач, cursor |
| GET | `/v1/flows/{flow_id}/progress-matrix` | Уроки × участники |
| GET | `/v1/flows/{flow_id}/leaderboard` | Таблица + scatter |
| GET / POST | `/v1/participants/{participant_id}/dialog-messages` | История и отправка (веб) |

Уже в коде (итерации backend до 1): `POST /v1/dialog-messages`, `POST /v1/submissions`, `GET /v1/flows/{flow_id}/modules`, `GET /v1/participants/{id}/submissions` — не ломать контракт.

## Архитектура (KISS)

- **`backend/api/`** — роутеры, Pydantic-схемы запрос/ответ, зависимости (сессия БД, текущий пользователь/роль).
- **`backend/services/`** — запросы SQLAlchemy 2 async, агрегации KPI, построение cursor, вызов LLM для `POST` диалога (если входит в scope; иначе заглушка с фиксацией в summary).
- Ошибки — существующий `ApiError` + коды из OpenAPI (`flow_not_found`, `forbidden`, `validation_error`, …).

## Риски и решения (зафиксировать в task-01 / summary)

- **Резолв по Telegram username:** при отсутствии колонки в `users` — миграция `telegram_username` (case-insensitive unique partial) или согласованный seed-only маппинг (хуже для прод).
- **Пары вопрос–ответ в ленте:** группировка `DialogMessage` (`user` + следующий `assistant`) по `participant_id` и времени; граничные случаи (ответ без вопроса) — `answer_summary: null`.
- **403 vs 404** по UUID — следовать политике в OpenAPI `info`.

## Файлы кода (ожидаемые к изменению)

- `backend/api/router.py` — подключение новых роутеров.
- `backend/api/*.py` — новые модули маршрутов по зонам (или один `flows_web.py` — по объёму).
- `backend/services/*.py` — выборки и бизнес-правила.
- `backend/models/*.py` / Alembic `alembic/versions/*` — при изменении схемы.
- `backend/tests/*` — сценарии happy-path и ошибок.

## Артефакты итерации

- Этот каталог: `plan.md`, `summary.md` (после закрытия).
- `tasks/task-NN-*/plan.md` и `summary.md` по каждой задаче.
- Актуальный [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md).
- При отклонении от OpenAPI — либо правка YAML, либо ADR/запись в `summary.md`.

## Проверки

| Команда / действие |
|--------------------|
| `make lint-backend` |
| `make test-backend` |
| Чистая БД: миграции + seed (инструкция в README или tech doc) |
