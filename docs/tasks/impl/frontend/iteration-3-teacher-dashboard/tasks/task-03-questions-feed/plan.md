# Задача: Лента вопросов к ассистенту

## Цель

Таблица (desktop) / упрощённый список (mobile) по `GET /v1/flows/{flow_id}/questions` с cursor-пагинацией.

## Данные (OpenAPI)

- Ответ `QuestionFeedPage`: `items[]` (`QuestionFeedItem`), `next_cursor` (`string | null`).
- Элемент `QuestionFeedItem`: обязательные `participant_id`, `participant_name`, `asked_at` (date-time), `question_text`; опционально `answer_summary` (`string | null`).
- Query: `limit` (default 20, max 100), `cursor`.

## Состав работ

- Таблица с колонками: участник, время (локализованный формат), вопрос (truncate + tooltip или раскрытие), ответ/резюме (`answer_summary` или «—»).
- Кнопка **«Загрузить ещё»** или бесконечный скролл (KISS — кнопка достаточна): передавать `cursor` из предыдущего ответа, пока `next_cursor` не пустой.
- Состояния: loading (первая загрузка vs append — не дублировать строки); empty «Вопросов пока нет»; error + retry.

## Файлы (ориентир)

- `web/components/dashboard/questions-feed.tsx`

## DoD

- Первая страница и последующие запросы используют один и тот же клиент из task-01.
- Нет дублирования `items` при повторном запросе с тем же cursor (защита на уровне UI-state).

## Проверки

- На демо-сиде есть хотя бы одна строка или корректный empty.
- Ручная проверка второй страницы при достаточном объёме данных в БД.
