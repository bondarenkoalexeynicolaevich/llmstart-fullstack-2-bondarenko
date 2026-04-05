# Задача 02: итог

- **`bot/config.py`**: `Settings` с `backend_base_url`, `internal_api_token`, `flow_id` (UUID); OpenRouter-поля удалены.
- **`requirements.txt`**: зависимость **`httpx`**.
- **`.env.example`**: блок бота с `FLOW_ID`; системный промпт перенесён в комментарий (хранится в `Flow` на сервере).
