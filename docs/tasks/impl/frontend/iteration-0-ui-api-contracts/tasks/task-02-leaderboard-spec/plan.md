# Задача 02: Спецификация лидерборда

## Цель

Описать экран сравнения прогресса студентов потока: режим таблицы и режим scatter, медали топ-3, поля API.

## Маршрут UI

- `/leaderboard` (уточнить группу маршрутов в итерации 2).

## Режим «Таблица»

Колонки:

| Колонка | Источник |
|---------|----------|
| Место | `rank` (1-based), для 1–3 — иконка медали (`medal`: `gold` \| `silver` \| `bronze` \| null) |
| Студент | `display_name`, `participant_id` |
| Общий прогресс | `overall_progress` (0–100), визуально progress bar |
| Уроки | `lesson_statuses[]`: по одному индикатору на `lesson_id` (иконка: сдано / частично / нет); порядок колонок совпадает с порядком уроков в потоке |

**Сортировка по умолчанию:** по убыванию `overall_progress`, затем по имени.

**Состояния:** `loading` — skeleton; `empty` — нет студентов; `error` — banner + retry.

## Режим «Карта» (scatter plot)

- Ось **X:** `lessons_completed` — число занятий с хотя бы одной сдачей в статусе `approved` (или согласованное правило в backend; здесь — отображаемая величина `x`).
- Ось **Y:** `submissions_approved` — число сдач в статусе `approved` (или другое согласованное поле — см. поле `y_meaning` в ответе API для подписи оси).
- Точка: `participant_id`, `display_name`, `x`, `y`, `rank` (для подписи tooltip).

**Легенда:** подписи осей с человекочитаемыми названиями из API (`scatter_meta.axis_x_label`, `axis_y_label`).

**Состояния:** те же.

## Переключатель

- Вкладки «Таблица» / «Карта» (shadcn Tabs); оба режима используют один ответ `GET /v1/flows/{flow_id}/leaderboard` (объект с `table` и `scatter`).

## Связь с данными

- `Participant` (студенты), `Submission`, `Assignment`, `Lesson`, VIEW прогресса — [`docs/data-model.md`](../../../../../data-model.md).

## API

- `GET /v1/flows/{flow_id}/leaderboard` — см. [`docs/api/backend-v1.openapi.yaml`](../../../../../api/backend-v1.openapi.yaml).
