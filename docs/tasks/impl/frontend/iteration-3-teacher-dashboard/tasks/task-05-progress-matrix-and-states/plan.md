# Задача: Матрица прогресса по урокам

## Цель

Визуализация `GET /v1/flows/{flow_id}/progress-matrix`: колонки уроков, строки студентов, ячейки статуса.

## Данные (OpenAPI)

`ProgressMatrixResponse`:

- `lessons[]`: `MatrixLessonColumn` — `id`, `title`, `module_title`, `module_order`, `lesson_order` (сортировать колонки по `(module_order, lesson_order)` на клиенте, если backend не гарантирует порядок).
- `rows[]`: `MatrixParticipantRow` — `participant_id`, `display_name`, `cells[]`.

`MatrixCell`: либо пустая ячейка (`status` и `submitted_at` оба `null`), либо статус `submitted` | `reviewed` | `approved` и опционально `submitted_at`.

**Соглашение:** порядок элементов в `cells` соответствует порядку колонок в `lessons` после сортировки (длина `cells` должна совпадать с `lessons`; при расхождении — показать error-баннер и записать баг backend).

## Состав работ

- Таблица с **фиксированной первой колонкой** имени и горизонтальным скроллом для уроков (`overflow-x-auto`, `sticky left-0` для ячейки имени).
- Tooltip или `title` на ячейке: название урока, статус, дата сдачи (если есть).
- Цветовое кодирование статусов (доступно + не только цветом — текст в tooltip).
- Сортировка строк: по `display_name` по умолчанию (как в спеки ит. 0).
- Состояния: loading skeleton; empty если `rows.length === 0`; error + retry.

## Файлы (ориентир)

- `web/components/dashboard/progress-matrix.tsx`

## DoD

- На демо-сиде матрица помещается в layout и скроллится на узком экране.
- Пустые ячейки визуально отличимы от заполненных.

## Проверки

- Smoke в браузере с горизонтальным скроллом.
- Быстрая проверка количества колонок vs `cells.length` (assert в dev или визуальный индикатор только для dev — не обязательно).
