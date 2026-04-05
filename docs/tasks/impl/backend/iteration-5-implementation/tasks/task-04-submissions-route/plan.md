# Задача: POST /v1/submissions

## Цель

Pydantic-схемы по OpenAPI, роутер с `require_internal_token`, сервис: резолв участника, проверка `Assignment.flow_id == body.flow_id`, INSERT `submitted`, `IntegrityError` → 409 `submission_already_exists`. Подключить в `api/router.py`.
