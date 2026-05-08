# task-02: Backend voice endpoint

- `backend/services/voice_stt.py` — транскрипция через OpenAI (в thread pool).
- `backend/api/voice.py` — multipart, dual auth (internal / JWT), вызов `record_dialog_exchange*` после STT.
- `backend/config.py` — `OPENAI_API_KEY`, опционально `VOICE_MAX_BYTES`.
