# Задача 01: итог

- Зафиксированы тело `POST /v1/dialog-messages`, успех `200` с `reply_text` и id двух `DialogMessage`, Bearer-аутентификация.
- Ошибки: `validation_error`, `unauthorized`, `forbidden`, `flow_not_found`, `participant_not_found` — согласованы с резолвом User → Participant и полями домена.
- Схемы перенесены в канонический [`docs/api/backend-v1.openapi.yaml`](../../../../../../api/backend-v1.openapi.yaml).
