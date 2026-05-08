# task-03: Web voice input

- `web/lib/use-voice-recorder.ts` — MediaRecorder, состояния idle/recording/processing.
- `web/lib/api/dialog.ts` — отправка multipart с JWT без ручного `Content-Type`.
- `chat-context.tsx` — `sendVoice(blob, filename)`; `chat-panel.tsx` — UI микрофона.
