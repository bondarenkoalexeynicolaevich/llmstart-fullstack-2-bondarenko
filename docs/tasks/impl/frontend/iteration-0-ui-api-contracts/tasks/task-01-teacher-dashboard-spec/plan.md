# Задача 01: Спецификация панели преподавателя (Teacher Dashboard)

## Цель

Описать экран аналитики потока для роли преподавателя: состав виджетов, поля данных, UX-состояния и ожидаемый JSON API (детали путей — [task-05](../task-05-api-contracts/plan.md)).

## Маршрут UI

- Предлагаемый путь: `/teacher` или `/dashboard` (финальное имя — в итерации 2); только для `Participant.role = teacher` в выбранном `flow_id`.

## Блоки экрана

### 1. Четыре KPI-карточки

| KPI | Описание | Метрика (логика агрегации задаётся в backend ит. 1) |
|-----|-----------|------------------------------------------------------|
| `active_students` | Студенты с активностью в окне | Число + дельта к предыдущему такому же окну |
| `submissions_count` | Сдачи за период | Число + дельта |
| `questions_count` | Вопросы к ассистенту (сообщения user в диалоге) | Число + дельта |
| `completion_rate` | Доля выполненных заданий по потоку (0–100 %) | Процент + дельта в п.п. |

**Виджет:** заголовок KPI, крупное значение, подпись периода (`period_label`), строка дельты: `delta` (число), `delta_direction` (`up` \| `down` \| `unchanged`), опционально `delta_label`.

**Состояния:** `loading` — skeleton 4 карточки; `empty` — не применимо к агрегатам (всегда числа); `error` — inline alert в зоне KPI + retry.

### 2. Линейный график активности (14 дней)

- Ось X: дни от `start_date` до `end_date` (ровно 14 точек, включая дни без событий — `count: 0`).
- Ось Y: число событий (по умолчанию — сумма сообщений пользователя в диалогах всех студентов потока; уточнение в backend).
- Точка ряда: `{ date: "YYYY-MM-DD", count: integer >= 0 }`.

**Состояния:** `loading` — skeleton графика; `error` — placeholder + retry; `empty` — все `count === 0` — показать ось и подпись «Нет активности за период».

### 3. Лента / таблица вопросов

Колонки (desktop; на mobile — карточки):

- Участник (`participant_name`, опционально `participant_id` UUID)
- Время (`asked_at` — ISO 8601, `timestamptz`)
- Текст вопроса (`question_text`, усечение в таблице с `…`, полный в tooltip / drawer)
- Ответ / резюме (`answer_summary` — краткий текст из ответа ассистента; если нет — `null`)

**Пагинация:** cursor или offset; в API ит. 0 зафиксировано как `limit` + `cursor` (см. OpenAPI).

**Состояния:** `loading` — skeleton строк; `empty` — «Вопросов пока нет»; `error` — banner + retry.

### 4. Лента сдач

Строка:

- `participant_name`, `participant_id`
- `lesson_title`, `assignment_title`, `submitted_at`, `status` (`submitted` \| `reviewed` \| `approved`)
- `submission_id` для перехода к деталям

**Клик по строке:** боковая панель или модал: полный `comment`, `assignment_title`, `lesson_title`, список `materials[]` из домена `Material` (id, title, type, url | content preview).

**Состояния:** аналогично вопросам.

### 5. Матрица прогресса

- Строки: студенты потока (`participant_id`, `display_name`), порядок по имени или по прогрессу — на усмотрение UI (зафиксировать в итерации 2 как сортировка по умолчанию: по имени).
- Колонки: уроки в порядке `module_order`, `lesson_order` (идентификатор колонки — `lesson_id`).
- Ячейка: `null` (нет сдачи) или объект `{ status, submitted_at? }` где `status` согласован с `Submission.status` или отсутствие сдачи.

**Tooltip / hover:** `lesson_title`, дата сдачи, статус.

**Адаптив:** горизонтальный скролл + закрепить первый столбец (имя).

**Состояния:** `loading` — skeleton сетки; `empty` — нет студентов; `error` — сообщение.

## Связь с данными

- `Submission`, `Assignment`, `Lesson`, `Module`, `Participant`, `User`, `DialogMessage`, `Material` — см. [`docs/data-model.md`](../../../../../data-model.md).

## API (ссылка)

- `GET /v1/flows/{flow_id}/dashboard` — KPI + ряд графика + метаданные периода
- `GET /v1/flows/{flow_id}/questions` — лента вопросов
- `GET /v1/flows/{flow_id}/submissions` — лента сдач потока (имя path в OpenAPI)
- `GET /v1/flows/{flow_id}/progress-matrix` — студенты × уроки
