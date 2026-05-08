# Итерация 8: Голосовой режим чата

**Цель:** запись с микрофона в веб-клиенте и обработка голосовых в Telegram через единый backend: STT (Whisper) → существующий сценарий диалога (LLM).

**Стек:** FastAPI `multipart`, OpenAI SDK `whisper-1`, браузер `MediaRecorder`, aiogram voice.

**Канонический контракт:** `docs/api/backend-v1.openapi.yaml`, ADR: `docs/adr/adr-004-voice-stt.md`.

## Задачи

| Задача | Каталог |
|--------|---------|
| ADR + OpenAPI | [tasks/task-01-adr-api-contract](tasks/task-01-adr-api-contract/plan.md) |
| Backend endpoint + STT | [tasks/task-02-backend-voice-endpoint](tasks/task-02-backend-voice-endpoint/plan.md) |
| Web: запись и отправка | [tasks/task-03-web-voice-input](tasks/task-03-web-voice-input/plan.md) |
| Bot: voice handler | [tasks/task-04-bot-voice-handler](tasks/task-04-bot-voice-handler/plan.md) |
| Лимиты, доки, smoke | [tasks/task-05-limits-smoke-docs](tasks/task-05-limits-smoke-docs/plan.md) |

## Definition of Done

- `POST /v1/voice/dialog-messages`: internal (бот) и JWT (веб); ответ включает `transcription`.
- Веб: кнопка микрофона в чате, fallback при отказе в доступе.
- Бот: `F.voice` → backend, ответ текстом.
- Документация и OpenAPI обновлены; `make lint-backend` / тесты при наличии.
