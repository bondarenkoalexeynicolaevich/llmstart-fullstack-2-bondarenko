# Task 02 — summary

- **`003_modules_lessons`:** таблицы `modules`, `lessons`, `materials`; очистка `submissions`/`assignments`; `assignments.lesson_id`; `users.email` nullable + частичные UNIQUE; enum `material_type`.
- **`004_knowledge_progress`:** `knowledge_items` (`embedding` как `float8[]`, без pgvector), VIEW `participant_assignment_progress`.
