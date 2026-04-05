# Задача 03: ORM-модели и первая миграция Alembic

## Цель

Объявить **SQLAlchemy 2.x** declarative-модели для **User**, **Flow**, **Participant** в соответствии с [`docs/data-model.md`](../../../../../../data-model.md):

| Таблица | Ключевые поля |
|---------|----------------|
| `users` | `id`, `telegram_id` (nullable), `name`, `email`, `role`, `created_at` |
| `flows` | `id`, `title`, `system_prompt`, `started_at`, `finished_at` (nullable) |
| `participants` | `id`, `user_id`, `flow_id`, `role`, `joined_at` |

Ограничения:

- FK с каскадом по смыслу MVP (минимум: `ON DELETE` для participant при удалении user/flow — либо RESTRICT, если так безопаснее для данных; зафиксировать выбор в summary задачи).
- **UNIQUE** `(user_id, flow_id)` на `participants`.

Инициализировать **Alembic** в репозитории: `alembic.ini`, `backend/alembic/env.py` (async), `versions/` с **первой ревизией**, создающей три таблицы. Предпочтительно **autogenerate** от актуальной metadata с последующей ручной выверкой.

## Файлы

- `backend/models/base.py` (или эквивалент единой `Base`)
- `backend/models/user.py`, `flow.py`, `participant.py`, `__init__.py` — реэкспорт для metadata
- `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/<rev>_initial_user_flow_participant.py`

## Критерии готовности

- `alembic upgrade head` на пустой БД создаёт ожидаемые таблицы и ограничения.
- `alembic downgrade -1` (или до base) откатывает ревизию без ручных правок DBA.

## Не входит

- Сиды данных, Module/Lesson/Assignment, DialogMessage, Submission.
