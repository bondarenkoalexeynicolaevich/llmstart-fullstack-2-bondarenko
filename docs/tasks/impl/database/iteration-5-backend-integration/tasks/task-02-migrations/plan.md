# Task 02: Миграции

- **003:** `modules`, `lessons`, `materials`, очистка `submissions`/`assignments`, замена `flow_id` на `lesson_id`, частичные UNIQUE на `users`, nullable `email`, enum `material_type`, индексы.
- **004:** `knowledge_items` (`embedding` как `float8[]`), VIEW `participant_assignment_progress` (pgvector — позже, при RAG).
