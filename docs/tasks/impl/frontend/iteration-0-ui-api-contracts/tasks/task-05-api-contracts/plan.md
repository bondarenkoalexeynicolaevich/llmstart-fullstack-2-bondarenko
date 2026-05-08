# Задача 05: HTTP API для веб-клиента (контракты)

## Назначение

Сводка маршрутов и JSON-схем для итерации 1 backend. **Канонический OpenAPI:** [`docs/api/backend-v1.openapi.yaml`](../../../../../api/backend-v1.openapi.yaml) (дополнен в этой итерации).

## Аутентификация

| Клиент | Заголовок |
|--------|-----------|
| Бот | `Authorization: Bearer <INTERNAL_API_TOKEN>` |
| Веб | `Authorization: Bearer <access_token>` после `POST /v1/auth/web-session` |

Один security scheme `bearerAuth`; различие только в значении токена.

## Форматы

- Даты событий: `date-time` ISO 8601, UTC (как в существующем контракте).
- Даты без времени в рядах графика: `date` (`YYYY-MM-DD`).
- Пагинация курсором: `limit` (default 20, max 100), `cursor` (opaque string, optional). Ответ содержит `next_cursor: string \| null`.

## Семантика успешных ответов (HTTP)

- **`POST /v1/auth/web-session`** — **200**: выдача токена (без отдельного URL «ресурса сессии»).
- **`POST /v1/dialog-messages`** (бот) и **`POST /v1/participants/{id}/dialog-messages`** (веб) — **201**; тело — `DialogMessageCreateResponse`; заголовок `Location` — см. OpenAPI.
- **`POST /v1/submissions`** — **201** + `Location` (как в OpenAPI).

## Ошибки

Тело как `ErrorBody` (`error.code`, `error.message`). Поле **`error.details`** — при валидации массив `[{ "field", "issue" }]` (см. схему OpenAPI). Коды **`rate_limited`** (429) и **`internal_error`** (500) — при лимитах и сбоях.

Дополнительные коды:

| code | HTTP |
|------|------|
| `user_not_in_flow` | 404 |
| `user_not_found` | 404 |
| `invalid_username` | 400 |
| `forbidden` | 403 (не та роль, чужой participant_id) |

---

## 1. `POST /v1/auth/web-session`

**Без Bearer.** Создаёт сессию веба по Telegram username.

**Request**

```json
{
  "telegram_username": "nickname",
  "flow_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

`telegram_username`: без `@`, trim, сравнение без учёта регистра на сервере.

**Response 200**

```json
{
  "access_token": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 604800,
  "user_id": "…",
  "participant_id": "…",
  "role": "teacher",
  "display_name": "Имя"
}
```

`role`: `student` | `teacher` (роль участника в этом потоке).

---

## 2. `GET /v1/flows/{flow_id}/dashboard`

KPI + ряд активности за 14 дней. **Доступ:** участник потока с ролью `teacher`.

**Response 200**

```json
{
  "period": {
    "start_date": "2026-04-23",
    "end_date": "2026-05-06",
    "label": "Последние 14 дней"
  },
  "kpis": [
    {
      "id": "active_students",
      "value": 18,
      "delta": 2,
      "delta_direction": "up",
      "unit": "count"
    },
    {
      "id": "completion_rate",
      "value": 72.5,
      "delta": 3.0,
      "delta_direction": "up",
      "unit": "percent"
    }
  ],
  "activity": [
    { "date": "2026-04-23", "count": 4 },
    { "date": "2026-05-06", "count": 0 }
  ]
}
```

`delta_direction`: `up` | `down` | `unchanged`. Полный набор `id` KPI: `active_students`, `submissions_count`, `questions_count`, `completion_rate`.

---

## 3. `GET /v1/flows/{flow_id}/questions`

Лента пар «вопрос студента — краткий ответ» (агрегация из `DialogMessage`). **Доступ:** teacher.

**Query:** `limit`, `cursor`.

**Response 200**

```json
{
  "items": [
    {
      "participant_id": "…",
      "participant_name": "Анна",
      "asked_at": "2026-05-06T12:00:00Z",
      "question_text": "Как оформить …?",
      "answer_summary": "Нужно использовать …"
    }
  ],
  "next_cursor": null
}
```

---

## 4. `GET /v1/flows/{flow_id}/submissions`

Лента сдач по потоку (новые первыми). **Доступ:** teacher.

**Query:** `limit`, `cursor`.

**Response 200** — элементы содержат материалы для модалки без второго запроса:

```json
{
  "items": [
    {
      "submission_id": "…",
      "participant_id": "…",
      "participant_name": "Анна",
      "lesson_id": "…",
      "lesson_title": "Занятие 3",
      "assignment_id": "…",
      "assignment_title": "ДЗ: API",
      "status": "submitted",
      "submitted_at": "2026-05-06T14:00:00Z",
      "comment": "Готово",
      "materials": [
        {
          "id": "…",
          "title": "Лекция",
          "type": "link",
          "url": "https://…",
          "content": null
        }
      ]
    }
  ],
  "next_cursor": null
}
```

---

## 5. `GET /v1/flows/{flow_id}/progress-matrix`

**Доступ:** teacher.

**Response 200**

```json
{
  "lessons": [
    {
      "id": "…",
      "title": "Урок 1",
      "module_title": "Модуль A",
      "module_order": 0,
      "lesson_order": 0
    }
  ],
  "rows": [
    {
      "participant_id": "…",
      "display_name": "Анна",
      "cells": [
        { "status": "approved", "submitted_at": "2026-05-01T10:00:00Z" },
        { "status": null, "submitted_at": null }
      ]
    }
  ]
}
```

`cells[i]` соответствует `lessons[i]`; `status: null` — нет сдачи.

---

## 6. `GET /v1/flows/{flow_id}/leaderboard`

**Доступ:** любой участник потока (студент видит таблицу группы; при необходимости ограничить в backend — итерация 1).

**Response 200**

```json
{
  "scatter_meta": {
    "axis_x_label": "Занятий с approved-сдачей",
    "axis_y_label": "Сдач в статусе approved"
  },
  "table": [
    {
      "rank": 1,
      "participant_id": "…",
      "display_name": "Анна",
      "overall_progress": 85,
      "lesson_statuses": [
        { "lesson_id": "…", "state": "done" }
      ],
      "medal": "gold"
    }
  ],
  "scatter": [
    {
      "participant_id": "…",
      "display_name": "Анна",
      "x": 5,
      "y": 8,
      "rank": 1
    }
  ]
}
```

`lesson_statuses[].state`: `done` | `partial` | `none`. `medal`: `gold` | `silver` | `bronze` | null.

---

## 7. `GET /v1/participants/{participant_id}/dialog-messages`

**Query:** `flow_id` (required), `limit`, `cursor`.

**Доступ:** токен должен позволять доступ к этому участнику (сам пользователь или преподаватель потока).

**Response 200**

```json
{
  "items": [
    {
      "id": "…",
      "role": "user",
      "content": "Привет",
      "created_at": "2026-05-06T12:00:00Z"
    }
  ],
  "next_cursor": null
}
```

---

## 8. `POST /v1/participants/{participant_id}/dialog-messages`

**Query:** `flow_id` (required).

**Request**

```json
{ "content": "Текст сообщения" }
```

**Response 201** — то же тело, что у бота при `POST /v1/dialog-messages` (текст ответа + id сообщений); см. OpenAPI.

```json
{
  "reply_text": "…",
  "user_message_id": "…",
  "assistant_message_id": "…"
}
```

---

## Согласованность с доменом

Все идентификаторы — UUID сущностей из [`docs/data-model.md`](../../../../../data-model.md). Поле `telegram_username` для резолва `User` может потребовать расширения схемы БД в итерации 1, если username не хранится — зафиксировать в backend tasklist.
