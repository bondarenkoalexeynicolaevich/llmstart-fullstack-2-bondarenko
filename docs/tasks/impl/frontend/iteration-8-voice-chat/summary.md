# Итерация 8 — summary

**Статус:** завершена (2026-05-08).

## Результат

- **Backend:** `POST /v1/voice/dialog-messages` — `multipart/form-data` (`audio`, `flow_id`, для бота ещё `telegram_user_id`). Аутентификация: Bearer `INTERNAL_API_TOKEN` или JWT веб-сессии (без `telegram_user_id` в форме). После STT (OpenAI `whisper-1`) вызываются те же сценарии, что для текста; в ответ добавлено поле `transcription`.
- **Конфиг:** `OPENAI_API_KEY`, опционально `VOICE_MAX_BYTES` (см. `backend/config.py`). Зависимость `python-multipart` для FastAPI Form/File.
- **Web:** `MediaRecorder` (`use-voice-recorder.ts`), кнопка микрофона в `chat-panel.tsx`, `sendVoice` + `apiFetchMultipart`.
- **Бот:** handler `F.voice`, загрузка файла без логирования байт, multipart в backend.
- **Документация:** ADR [`docs/adr/adr-004-voice-stt.md`](../../adr/adr-004-voice-stt.md), OpenAPI, `docs/integrations.md`, `docs/tech/api-contracts.md`, корневой `.env.example`. Цель `make voice-smoke` (ручная подсказка).
- **Тесты:** `backend/tests/test_voice_dialog.py` (мок STT + happy path internal, валидации, отсутствие ключа).

## Отклонения от чернового плана

- Файл ADR назван **`adr-004-voice-stt.md`** (в репозитории уже есть `adr-003-enum-strategy.md`).
- Ответ сохранён как расширение существующей схемы `DialogMessageCreateResponse`, а не отдельный объект с блоком `meta`.

## Приёмка (ручная)

При заданном `OPENAI_API_KEY`: записать голос в веб-чате и отправить voice в Telegram при работающем backend и участнике в потоке.
