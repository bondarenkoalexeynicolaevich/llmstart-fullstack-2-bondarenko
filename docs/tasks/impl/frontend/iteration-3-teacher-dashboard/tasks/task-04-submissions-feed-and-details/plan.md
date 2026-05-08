# Задача: Лента сдач по потоку и детали по клику

## Цель

Таблица сдач по `GET /v1/flows/{flow_id}/submissions` с раскрытием деталей строки в **Sheet** (уже есть в проекте) или модалке.

## Данные (OpenAPI)

- Ответ `SubmissionFeedPage`: `items[]` (`SubmissionFeedItem`), `next_cursor`.
- `SubmissionFeedItem` (обязательные поля): `submission_id`, `participant_id`, `participant_name`, `lesson_id`, `lesson_title`, `assignment_id`, `assignment_title`, `status` (`submitted` | `reviewed` | `approved`), `submitted_at`, `materials[]`.
- Также `comment`: `string | null`.
- `MaterialRef`: `id`, `title`, `type` (`link` | `file` | `text`), опционально `url` | `content`.

## Состав работ

- Таблица: участник, задание/урок (можно две колонки или объединённая ячейка), статус (badge), время сдачи.
- Клик по строке открывает панель: полный `comment`, заголовки урока/задания, блок **материалов**:
  - `type === link` и есть `url` — внешняя ссылка (новая вкладка);
  - `text` с `content` — безопасный текст (без `dangerouslySetInnerHTML`, если контент не доверенный — показать как plain text / markdown только если явно решите позже).
- Пагинация как в task-03 (`limit` / `cursor` / «Загрузить ещё»).
- Состояния: loading / empty / error аналогично вопросам.

## Файлы (ориентир)

- `web/components/dashboard/submissions-feed.tsx`
- Использовать [`web/components/ui/sheet.tsx`](../../../../../web/components/ui/sheet.tsx) при необходимости.

## DoD

- Детали соответствуют выбранной строке; закрытие Sheet сбрасывает выбор без утечки состояния в список.
- Материалы отображаются для всех типов из enum.

## Проверки

- Клик по нескольким строкам подряд на демо-данных.
- `make web-lint`.
