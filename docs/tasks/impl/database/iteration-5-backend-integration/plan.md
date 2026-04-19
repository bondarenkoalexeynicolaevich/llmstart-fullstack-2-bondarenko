# Итерация 5: ORM, сервисы, read-API, интеграция в backend

**Цель:** Согласовать backend с [`docs/data-model.md`](../../../../data-model.md): Module, Lesson, Material, KnowledgeItem, `Assignment.lesson_id`, VIEW прогресса, read-эндпоинты, тесты и seed.

**Стек:** FastAPI, SQLAlchemy 2 async, Alembic, PostgreSQL 16 (`docker-compose`: `postgres:16`). `knowledge_items.embedding` — `float8[]` для портируемости; pgvector — отдельной миграцией при RAG.

**Задачи:** см. `tasks/task-*/plan.md`.

**Политика данных при миграции 003:** строки `submissions` и `assignments` удаляются в миграции перед сменой схемы; для dev достаточно `make db-reset` + seed.
