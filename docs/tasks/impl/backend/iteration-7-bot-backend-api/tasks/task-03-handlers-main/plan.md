# Задача 03: Handlers и точка входа

## Цель

Текстовые сообщения → `BackendClient.post_dialog_message`; убрать in-memory историю и файл `bot/llm_client.py`.

## Состав работ

- `setup_router(settings, backend_client)`: без словаря `histories` и тримминга.
- `/start`, `/reset`: только UX-текст (история на сервере; сброс разработать позже).
- `main.py`: создать клиент, передать в роутер, в `finally` — `aclose`.

## DoD

- В репозитории нет импорта `LLMClient` в боевом пути.
- Файл `llm_client.py` удалён.
