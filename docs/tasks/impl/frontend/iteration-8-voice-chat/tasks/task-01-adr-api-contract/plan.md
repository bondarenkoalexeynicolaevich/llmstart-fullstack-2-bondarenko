# task-01: ADR + API contract

- ADR `docs/adr/adr-004-voice-stt.md`: Whisper `whisper-1`, один endpoint, лимит 25 MB, без хранения сырого аудио в логах.
- OpenAPI: `POST /v1/voice/dialog-messages` (multipart), расширение `DialogMessageCreateResponse` полем `transcription`.
