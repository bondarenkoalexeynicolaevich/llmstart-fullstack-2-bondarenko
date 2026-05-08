# Задача: Маршрут дашборда и контракт данных (API-слой)

## Цель

Подготовить основу страницы `/dashboard`: чтение сессии (`flow_id`, JWT, `role`), единый типизированный слой HTTP-запросов к teacher-dashboard endpoint-ам без дублирования заголовков и базового URL.

## Контракт backend

Источник полей: [`docs/api/backend-v1.openapi.yaml`](../../../../../api/backend-v1.openapi.yaml).

| Операция | Метод | Примечание |
|----------|-------|------------|
| Дашборд | `GET /v1/flows/{flow_id}/dashboard` | `TeacherDashboardResponse`: `period`, `kpis[]`, `activity[]` |
| Вопросы | `GET /v1/flows/{flow_id}/questions` | query `limit`, `cursor`; ответ `QuestionFeedPage` |
| Сдачи потока | `GET /v1/flows/{flow_id}/submissions` | query `limit`, `cursor`; ответ `SubmissionFeedPage` |
| Матрица | `GET /v1/flows/{flow_id}/progress-matrix` | ответ `ProgressMatrixResponse` |

Заголовок: `Authorization: Bearer <JWT из localStorage>`. База URL: `process.env.NEXT_PUBLIC_BACKEND_BASE_URL`.

## Состав работ

- Утилита или модуль в `web/lib/api/`:
  - функция `apiFetch<T>(path, options)` с подстановкой Bearer и `Content-Type: application/json` где нужно;
  - разбор ошибок: при не-2xx попытаться прочитать тело как `ErrorBody`; при `401` — событие «разлогин» (очистка session + редирект `/login`).
- Типы TypeScript, отражающие схемы: `TeacherDashboardResponse`, `DashboardKpi`, `ActivityDay`, `QuestionFeedPage`, `QuestionFeedItem`, `SubmissionFeedPage`, `SubmissionFeedItem`, `MaterialRef`, `ProgressMatrixResponse`, `MatrixLessonColumn`, `MatrixParticipantRow`, `MatrixCell`, `CursorPageMeta`.
- В корне страницы дашборда (или отдельном wrapper): если `getSession()?.role !== 'teacher'` — **не** вызывать teacher-only методы; показать заголовок и текст вида «Доступно только преподавателям потока» и навигацию на доступные разделы.

## Файлы (ориентир)

- Новые: `web/lib/api/client.ts` (или `web/lib/api/teacher-dashboard.ts`) + при необходимости `web/lib/api/types.ts`.
- Изменяемые: [`web/app/(app)/dashboard/page.tsx`](../../../../../web/app/(app)/dashboard/page.tsx) — подключение заготовки секций или контейнера.

## Состояния и DoD

- Есть один переиспользуемый способ дернуть API с JWT.
- Типы совпадают с полями OpenAPI (имена и nullable).
- Студент не получает «сломанный» экран с сырыми 403 — осмысленное сообщение.
- Нет `console.log` с токеном или телами сообщений.

## Проверки

- Ручной вызов после логина преподавателя: хотя бы `GET .../dashboard` возвращает 200 на демо-сиде.
- `make web-lint` (после добавления кода).
