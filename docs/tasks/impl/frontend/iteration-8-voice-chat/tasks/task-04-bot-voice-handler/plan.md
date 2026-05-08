# task-04: Bot voice handler

- `handlers.py` — `@router.message(F.voice)`, скачивание файла, вызов `BackendClient.post_voice_dialog_message`.
- `backend_client.py` — multipart `POST /v1/voice/dialog-messages`.
