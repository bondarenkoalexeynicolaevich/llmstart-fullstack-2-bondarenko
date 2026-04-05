# Итерация 5: итог

## Сделано

- **Миграция `002_dialog_submissions`:** `assignments` (MVP: прямой `flow_id`, `title`, `description`), `dialog_messages` (роль, текст, индекс по `participant_id` + `created_at`), `submissions` (статус `submitted` при создании, уникальность `(participant_id, assignment_id)`).
- **ORM:** модели `Assignment`, `DialogMessage`, `Submission`; enum'ы `DialogMessageRole`, `SubmissionStatus`.
- **Конфиг:** `OPENROUTER_API_KEY` (общий с ботом), `LLM_MODEL`, `OPENROUTER_BASE_URL` (опционально), `LLM_TEMPERATURE`, `MAX_HISTORY_MESSAGES` (дефолт 30).
- **LLM:** `OpenRouterLlmClient` (`AsyncOpenAI`), контент в логи не пишется; без ключа — `NotConfiguredLlmClient` и 500 на диалоге как раньше.
- **Диалог:** `services/dialog_messages.py` — история (лимит N−1 до вставки), INSERT user → LLM → INSERT assistant → commit; `api/dialog.py` логирует id сообщений без текста.
- **Сдачи:** `POST /v1/submissions`, проверка задания в потоке, `409 submission_already_exists` при дубле.
- **Тесты:** TRUNCATE расширен; `seed_assignment`; сценарии submissions и проверка двух строк `dialog_messages` после диалога.

## Отклонение от `docs/data-model.md`

Задание в MVP привязано к **потоку** (`assignments.flow_id`), без цепочки Module → Lesson → Assignment. Дальнейшая нормализация — отдельной миграцией.

## Команды

- `make migrate-upgrade` / `make test-backend` / `make lint-backend`
