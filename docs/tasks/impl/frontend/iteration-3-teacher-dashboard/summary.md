# Итерация 3: Панель преподавателя — summary

**Статус:** ✅ Done

## Ценность

Преподаватель после веб-входа открывает `/dashboard` и видит сводку потока: четыре KPI с дельтой к предыдущему 14-дневному окну, график активности (сообщения студентов по дням), таблицу вопросов с курсорной пагинацией, ленту сдач с боковой панелью деталей (комментарий и материалы) и матрицу прогресса с подсказками по ячейкам и закреплённой колонкой имён.

## Реализовано

- **`web/lib/api/types.ts`** — типы ответов OpenAPI для дашборда, лент и матрицы.
- **`web/lib/api/client.ts`** — `apiFetch` с `Authorization: Bearer`, разбор `ErrorBody`, при **401** — `clearSession` и редирект на `/login`.
- **`web/lib/api/flow-teacher.ts`** — запросы к `GET .../dashboard`, `questions`, `submissions`, `progress-matrix`.
- **`web/components/teacher-dashboard-client.tsx`** — клиентская страница: роль `student` без вызовов teacher-only API, с понятным сообщением и ссылками на лидерборд и чат; блоки с loading (pulse), empty, error + retry; **recharts** для линейного графика; **Sheet** для деталей сдачи.
- **`web/app/(app)/dashboard/page.tsx`** — рендер `TeacherDashboardClient`.
- Зависимость **`recharts`** в `web/package.json` (установка через `npm install recharts` в каталоге `web/`).

## Задачи

| Задача | Результат |
|--------|-----------|
| task-01 | API-слой и типы; проверка роли на UI |
| task-02 | 4 KPI + график 14 дней |
| task-03 | Таблица вопросов, «Загрузить ещё» по `next_cursor` |
| task-04 | Таблица сдач, клик → Sheet с `comment` и `materials` |
| task-05 | Матрица, `title` на ячейках, горизонтальный скролл, sticky имя |
| task-06 | `npm run lint` / `npm run build` в `web/`; smoke по инструкции в `plan.md` итерации |

## Отклонения от плана

- Отдельные `summary.md` по папкам `task-02` … `task-06` не создавались: итог сжат в этой таблице (KISS).
- Зависимость добавлена через **npm**, т.к. в окружении агента `pnpm` не был в PATH; в tasklist по-прежнему целевой менеджер для команды — **pnpm**, при необходимости выполните `pnpm install` в `web/` для синхронизации lockfile.

## Контракт API

Соответствует [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml) и [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md); изменений контракта не вносилось.
