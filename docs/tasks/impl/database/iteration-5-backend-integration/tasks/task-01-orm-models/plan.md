# Task 01: ORM-модели

- Новые: `Module`, `Lesson`, `Material`, `KnowledgeItem` (+ enum `MaterialType`).
- `Assignment`: `lesson_id` вместо `flow_id`.
- `Flow`: `modules` вместо `assignments`.
- `User`: `email` опциональный, без `default=""`.
- Экспорт в `models/__init__.py`.
