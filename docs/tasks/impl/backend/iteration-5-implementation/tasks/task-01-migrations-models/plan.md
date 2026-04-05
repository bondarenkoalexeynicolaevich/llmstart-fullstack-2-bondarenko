# Задача: миграция 002 + модели

## Цель

Alembic `002`: таблицы `assignments` (FK `flow_id`), `dialog_messages`, `submissions`; enum `dialog_message_role`, `submission_status`; уникальный индекс `(participant_id, assignment_id)` на `submissions`.

## Результат

- Ревизия Alembic с `down_revision = 001_initial`.
- SQLAlchemy-модели в `backend/models/`, импорт в `backend/models/__init__.py` для метаданных.
