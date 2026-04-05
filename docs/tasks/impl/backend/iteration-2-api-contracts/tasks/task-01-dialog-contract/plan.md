# Задача 01: контракт «одно сообщение» (`POST /v1/dialog-messages`)

## Цель

Описать запрос/ответ, коды и ошибки для сценария send-and-reply без догадок клиента.

## Запрос

| Поле | Тип | Обязательность |
|------|-----|----------------|
| `flow_id` | UUID string | да |
| `telegram_user_id` | integer | да |
| `content` | string | да, после trim непустая |

Заголовок: `Authorization: Bearer <INTERNAL_API_TOKEN>`.

## Успех (`200`)

| Поле | Тип | Смысл |
|------|-----|--------|
| `reply_text` | string | Текст ответа ассистента (то, что показывает бот) |
| `user_message_id` | UUID | id сохранённого `DialogMessage` с ролью `user` |
| `assistant_message_id` | UUID | id сохранённого `DialogMessage` с ролью `assistant` |

Семантика HTTP: **200** (операция обрабатывает сообщение и возвращает результат; пара сообщений не оформлена как отдельный URI ресурса).

## Ошибки

| HTTP | `error.code` | Условие |
|------|--------------|---------|
| `400` | `validation_error` | Невалидный JSON-схемой, пустой/пробельный `content`, неверный формат UUID |
| `401` | `unauthorized` | Нет Bearer или неверный токен |
| `403` | `forbidden` | Участник есть, но роль не позволяет (например преподаватель вместо студента — если правило включат в ит. 5) |
| `404` | `flow_not_found` | Нет `Flow` с данным `flow_id` |
| `404` | `participant_not_found` | Нет `User` с `telegram_id` или нет `Participant` для (user, flow) |

## Cross-check: `DialogMessage` и `Flow`

- Каждое сохранённое сообщение пользователя и ответа ассистента — строки в `DialogMessage` с `participant_id` резолвленного участника, `role` ∈ {`user`, `assistant`}, `content` — текст из запроса / от LLM ([`docs/data-model.md`](../../../../../../data-model.md)).
- История для LLM: сообщения этого `participant_id` по времени; **системный контекст** потока — из `Flow.system_prompt` по `flow_id`, не из тела запроса (генерация — итерация 5).
- Роль `system` в персистентной истории может не использоваться в MVP; допускается только `user`/`assistant` в ответах API выше.

## Артефакт

Полная схема — в [`docs/api/backend-v1.openapi.yaml`](../../../../../../api/backend-v1.openapi.yaml) (`paths./v1/dialog-messages`).
