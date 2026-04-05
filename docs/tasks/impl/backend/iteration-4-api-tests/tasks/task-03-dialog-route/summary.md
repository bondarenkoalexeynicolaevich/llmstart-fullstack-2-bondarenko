# Задача 03: итог

- [`backend/api/errors.py`](../../../../../../../backend/api/errors.py), [`backend/api/security.py`](../../../../../../../backend/api/security.py): Bearer + `ApiError` / envelope.
- [`backend/services/llm.py`](../../../../../../../backend/services/llm.py): `LlmClient`, `NotConfiguredLlmClient`, `get_llm_client`.
- [`backend/api/schemas_dialog.py`](../../../../../../../backend/api/schemas_dialog.py), [`backend/api/dialog.py`](../../../../../../../backend/api/dialog.py): `POST /v1/dialog-messages`; регистрация в [`backend/api/router.py`](../../../../../../../backend/api/router.py); обработчик в [`backend/main.py`](../../../../../../../backend/main.py).
