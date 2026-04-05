# Задача 02: контракт «одна сдача» (`POST /v1/submissions`)

## Цель

Описать создание `Submission` с идентификацией через `telegram_user_id` + `flow_id`, статусы и конфликт дубликата.

## Запрос

| Поле | Тип | Обязательность |
|------|-----|----------------|
| `flow_id` | UUID string | да |
| `telegram_user_id` | integer | да |
| `assignment_id` | UUID string | да |
| `comment` | string \| null | нет |

Заголовок: `Authorization: Bearer <INTERNAL_API_TOKEN>`.

Backend: резолв `Participant` как в диалоге; проверка, что `Assignment` существует и принадлежит цепочке, ведённой из того же `flow_id` (через `Lesson` → `Module` → `flow_id`), иначе `404` с `assignment_not_found`.

## Успех (`201`)

Тело — созданный ресурс:

| Поле | Тип | Примечание |
|------|-----|------------|
| `id` | UUID | id `Submission` |
| `assignment_id` | UUID | как в запросе |
| `participant_id` | UUID | вычисленный сервером |
| `status` | string | начальное значение `submitted` ([`docs/data-model.md`](../../../../../../data-model.md)) |
| `submitted_at` | string (date-time) | ISO 8601 UTC |
| `comment` | string \| null | эхо переданного или null |

## Ошибки

| HTTP | `error.code` | Условие |
|------|--------------|---------|
| `400` | `validation_error` | Невалидное тело / UUID |
| `401` | `unauthorized` | Нет или неверный Bearer |
| `403` | `forbidden` | Роль не студент (или иное правило ит. 5) |
| `404` | `flow_not_found` | Нет потока |
| `404` | `participant_not_found` | Нет участия в потоке |
| `404` | `assignment_not_found` | Нет задания или не из этого потока |
| `409` | `submission_already_exists` | Уже существует `Submission` для той же пары (`participant_id`, `assignment_id`) |

Правило **409:** идемпотентность «одна сдача на задание на участника» на уровне БД; повторное создание с теми же ключами — конфликт.

## Вне MVP контракта

- `GET /v1/submissions/{id}` и списки — не описываются; при необходимости боту — отдельное расширение контракта.

## Артефакт

[`docs/api/backend-v1.openapi.yaml`](../../../../../../api/backend-v1.openapi.yaml) (`paths./v1/submissions`).
