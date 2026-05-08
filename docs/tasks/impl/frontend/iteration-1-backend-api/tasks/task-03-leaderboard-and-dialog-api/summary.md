# Задача 03: Лидерборд и веб-диалог — summary

## Лидерборд

- `GET /v1/flows/{flow_id}/leaderboard` → `backend/services/flow_analytics.leaderboard_payload`, ответ валидируется схемой `LeaderboardResponse` в роутере.
- Доступ: `require_member_in_flow` (студент или преподаватель того же `flow_id`).

## Веб-диалог

- `GET/POST /v1/participants/{participant_id}/dialog-messages?flow_id=…` → `backend/api/participant_dialog_web.py`, логика `backend/services/dialog_messages.py` (`list_dialog_messages_page`, `record_dialog_exchange_for_participant_web`).
- Права: JWT должен содержать тот же `participant_id` и `flow_id`, что запрос (`403` при несоответствии).
- Ответ модели через существующий `LlmClient` / OpenRouter; при сбое LLM клиент получает `500` / `internal_error` по паттерну API.

## 403 против internal token

`INTERNAL_API_TOKEN` на веб-маршрутах с JWT **отклоняется сознательно** (`backend/api/web_auth.py`) — см. [`docs/tech/api-contracts.md`](../../../../../../tech/api-contracts.md).
