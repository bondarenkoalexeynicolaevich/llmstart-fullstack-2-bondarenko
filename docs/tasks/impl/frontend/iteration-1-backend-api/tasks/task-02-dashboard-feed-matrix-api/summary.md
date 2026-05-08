# Задача 02: Dashboard / ленты / матрица — summary

## Реализация

| Путь OpenAPI | Код |
|--------------|-----|
| `GET /v1/flows/{flow_id}/dashboard` | `backend/api/flows_web.py`, сервис `backend/services/flow_analytics.py` (`build_dashboard`) |
| `GET /v1/flows/{flow_id}/questions` | `flow_feeds.question_feed_page` |
| `GET /v1/flows/{flow_id}/submissions` | `flow_feeds.submission_feed_page` |
| `GET /v1/flows/{flow_id}/progress-matrix` | `flow_analytics.progress_matrix_payload` |

JWT и роль **teacher**: зависимости `require_teacher_in_flow`; порядок параметров маршрута — Depends до Query с значениями по умолчанию (валидый Python-синтаксис).

Пагинация лент — opaque `cursor` через `backend/services/cursor_page.py`.

## Отличия от плана / OpenAPI

Существенных отклонений от [`docs/api/backend-v1.openapi.yaml`](../../../../../../api/backend-v1.openapi.yaml) нет; коды ошибок через существующий `ApiError` / `ErrorBody`.
