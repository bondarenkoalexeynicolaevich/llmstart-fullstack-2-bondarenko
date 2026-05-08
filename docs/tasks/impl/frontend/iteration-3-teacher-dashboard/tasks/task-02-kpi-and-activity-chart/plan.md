# Задача: KPI-карточки и график активности (14 дней)

## Цель

Отобразить блок `GET /v1/flows/{flow_id}/dashboard`: четыре KPI и линейный график по массиву `activity`.

## Данные (OpenAPI)

Ответ `TeacherDashboardResponse`:

- `period`: `start_date`, `end_date`, `label` — подпись периода для KPI и графика.
- `kpis`: массив `DashboardKpi`; элемент с полями:
  - `id`: `active_students` | `submissions_count` | `questions_count` | `completion_rate`
  - `value`, `delta`, `delta_direction` (`up` | `down` | `unchanged`), `unit` (`count` | `percent`)
- `activity`: массив `ActivityDay` — `{ date: date, count: integer >= 0 }` (ожидается 14 точек, включая нули).

Маппинг KPI на UI: **по `id`**, не по порядку в массиве.

## Состав работ

- Зависимость **`recharts`**: `npm install recharts` из корня через принятую в репо команду (`make web-install` / установка в `web/`).
- Компонент сетки из **4 карточек** (shadcn `Card` при наличии): заголовок человекочитаемый по `id`, значение с форматированием (`unit === percent` → проценты).
- Отображение дельты: стрелка/цвет по `delta_direction`, текст `delta` (для процентов — явно указать, что это п.п. или сырое число согласно backend).
- График: линия по `activity`; ось X — даты (короткий формат); при всех `count === 0` — подпись «Нет активности за период» (оси остаются).
- Состояния: skeleton при загрузке; error с retry для всего блока dashboard (можно общий с task-01).

## Файлы (ориентир)

- `web/components/dashboard/kpi-grid.tsx`
- `web/components/dashboard/activity-chart.tsx`
- Обновление [`web/app/(app)/dashboard/page.tsx`](../../../../../web/app/(app)/dashboard/page.tsx) или `dashboard-page.tsx`.

## DoD

- На демо-данных видны 4 KPI и график без ошибок гидрации.
- Темная тема читаема (контраст линии/сетки).

## Проверки

- Smoke после логина преподавателя.
- `make web-build`.
