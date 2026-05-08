# Задача 02: API дашборда, лент и матрицы прогресса

## Цель

Реализовать маршруты под панель преподавателя по OpenAPI:

- `GET /v1/flows/{flow_id}/dashboard`
- `GET /v1/flows/{flow_id}/questions`
- `GET /v1/flows/{flow_id}/submissions`
- `GET /v1/flows/{flow_id}/progress-matrix`

## Аутентификация и доступ

- `Authorization: Bearer` — JWT веб-сессии или внутренний токен (как в OpenAPI `bearerAuth`).
- Для dashboard / лент / матрицы: участник с `role=teacher` в этом `flow_id`; иначе `403` + `forbidden` (или политика 404 — как в реализации `ApiError`).

## Реализация (KISS)

1. **Роутер** — новый файл в `backend/api/` (например `teacher_flow.py` или `flows_analytics.py`) + регистрация в `backend/api/router.py`.
2. **Сервис** — функции/async-классы в `backend/services/`: один модуль или разбить по чтениям при росте.
3. **Схемы Pydantic** — зеркалировать имена полей из `components/schemas` OpenAPI (`DashboardKpi`, `QuestionFeedPage`, …).

### Dashboard

- `period`: последние 14 календарных дней включительно (или как в утверждённом правиле из task-01).
- `kpis`: массив из четырёх элементов с `id` из enum OpenAPI.
- `activity`: 14 точек `date` + `count` (дни без событий — `0`).

### Ленты (`questions`, `submissions`)

- Пагинация: `limit` (default/max по OpenAPI), `cursor` opaque (рекомендация: base64 последнего ключа `(created_at, id)` или аналог).
- Сортировка: новые первыми (как в описании потоковых лент).
- **Submissions:** поле `materials` всегда массив (`MaterialRef`); пустой, если материалов нет.

### Progress matrix

- `lessons`: колонки в порядке модулей/`order` затем уроков/`order`.
- `rows`: по студентам потока (`Participant.role=student`), `cells` выровняны по `lessons.length`.

## Ошибки

Стабильные `error.code`: `flow_not_found`, `forbidden`, `unauthorized`, `validation_error`; тело — `ErrorBody`.

## Тесты (минимум)

- Smoke: учитель видит данные; студент/`flow` чужой — ожидаемый отказ.
- Cursor: две страницы подряд, `next_cursor` меняется.
- Матрица: размерность `cells` == `len(lessons)`.

## Связанные задачи

- Данные и миграции: [task-04](../task-04-migrations-and-seed/plan.md).
- Документирование: [task-05](../task-05-tests-and-contract-docs/plan.md).
