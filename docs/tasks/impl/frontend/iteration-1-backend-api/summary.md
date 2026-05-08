# Итерация 1: Backend API для frontend — summary

**Статус:** ✅ завершена (соответствие DoD из [`docs/tasks/tasklist-frontend.md`](../../../tasklist-frontend.md)).

## Ценность

Веб-клиент (итерации 2–6) может вызывать реальный backend по [`docs/api/backend-v1.openapi.yaml`](../../../../api/backend-v1.openapi.yaml): веб-сессия (JWT), дашборд преподавателя, ленты вопросов и сдач, матрица прогресса, лидерборд, история и отправка сообщений диалога по `participant_id`.

## Реализованные эндпоинты итерации

| Method | Path |
|--------|------|
| POST | `/v1/auth/web-session` |
| GET | `/v1/flows/{flow_id}/dashboard` |
| GET | `/v1/flows/{flow_id}/questions` |
| GET | `/v1/flows/{flow_id}/submissions` |
| GET | `/v1/flows/{flow_id}/progress-matrix` |
| GET | `/v1/flows/{flow_id}/leaderboard` |
| GET, POST | `/v1/participants/{participant_id}/dialog-messages` |

Существующие для бота/структуры: `dialog-messages` (бот), `submissions` POST, `flows/.../modules`, `participants/.../submissions` — без ломания контракта.

## Ключевые модули

- `backend/api/auth_web.py`, `flows_web.py`, `participant_dialog_web.py`, `web_auth.py`, `schemas_web.py`
- `backend/services/web_jwt.py`, `web_session.py`, `flow_analytics.py`, `flow_feeds.py`, дополнения `dialog_messages.py`, `cursor_page.py`
- `backend/config.py` — `jwt_secret`, `jwt_expires_in_seconds`
- Миграция `005_users_telegram_username`

## Отложенные пункты

Нет открытых отложений по scope итерации 1 из OpenAPI под экраны 3–6.

## Demo / локальный прогон

1. `make db-up`; `make migrate-upgrade`
2. `make db-seed` или `make db-seed-frontend-demo`
3. Преподаватель для входа в веб по username: **`bondarenko_alexey_nikolaevich`**, `flow_id`: **`00000000-0000-0000-0000-000000000001`** (переменные JWT — см. `.env.example`).
