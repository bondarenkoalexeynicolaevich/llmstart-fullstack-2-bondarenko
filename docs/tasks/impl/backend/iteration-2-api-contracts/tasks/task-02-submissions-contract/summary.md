# Задача 02: итог

- Описан `POST /v1/submissions`: DTO запроса с `assignment_id` (без `module_id`), ответ `201` с `status: submitted`, `submitted_at`, `participant_id` в теле.
- Ошибки `404` разведены по `flow_not_found`, `participant_not_found`, `assignment_not_found`; дубликат — `409` / `submission_already_exists`.
- Схемы в [`docs/api/backend-v1.openapi.yaml`](../../../../../../api/backend-v1.openapi.yaml).
