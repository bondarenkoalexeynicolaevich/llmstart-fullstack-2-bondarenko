# Задача 03: API лидерборда и веб-диалога

## Цель

Реализовать:

- `GET /v1/flows/{flow_id}/leaderboard` — `LeaderboardResponse` (таблица + `scatter` + `scatter_meta`).
- `GET /v1/participants/{participant_id}/dialog-messages?flow_id=…` — пагинация cursor.
- `POST /v1/participants/{participant_id}/dialog-messages?flow_id=…` — **201**, тело как `DialogMessageCreateResponse`; заголовок `Location` как в OpenAPI.

## Лидерборд

### Табличная часть

- Учитывать только студентов потока.
- `rank`: стабильный при равных значениях (например по `participant_id`).
- `lesson_statuses[]`: массив по урокам потока (тот же порядок колонок, что и матрица — желательно вынести общий helper).
- `overall_progress`: 0–100, консистентен с таблицей и scatter `y`.
- `medal`: `gold/silver/bronze` только для топ-3 или `null`.

### Scatter

- `scatter_meta.axis_x_label` / `axis_y_label` — осмысленные строки (зафиксировать в коде/`api-contracts.md`, например «Уроков завершено» / «Общий прогресс %» — уточнить при реализации).
- Точки: `participant_id`, `display_name`, `x`, `y`, `rank` синхронны с таблицей.

## Веб-диалог

### GET

- Фильтр: `participant_id` принадлежит `flow_id`; иначе 403/404 по политике.
- Строгая сортировка по времени для стабильного cursor (`created_at`, tie-break `id`).
- Не возвращать `system`-сообщения в MVP, только если клиент их ждёт — OpenAPI включает `role: system`; **если фильтруем** — синхронизировать с описанием в `docs/tech/api-contracts.md` и YAML.

### POST

- Создать `DialogMessage` user, затем ответ ассистента.
- Если LLM ещё не подключён в этом спринте: вернуть детерминированную заглушку текста ответа **и** сохранять обе записи — или явно отложить в `summary.md` с согласованием (лучше не ломать 201-тело).
- `429` / `rate_limited` при лимите провайдера — по аналогии с бот-эндпоинтом.

## Связь с ботом

- `POST /v1/dialog-messages` (бот, `telegram_user_id`) остаётся отдельным контуром; общая логика сохранения — вынести в сервис `dialog_service` при дублировании (KISS: одна функция `persist_pair`).

## Тесты (минимум)

- Лидерборд: корректные размеры массивов, медали для 3 лидеров при N≥3.
- Диалог: POST → GET возвращает новые сообщения; чужой `participant_id` — отказ.
