# Задача 03: Ревью postgresql-table-design — summary

**Статус:** завершена  
**Итерация:** [iteration-2-schema](../../plan.md)

## Чеклист skill (кратко)

| Тема | Решение |
|------|---------|
| PK | UUID + default `gen_random_uuid()` — компромисс с уже применёнными миграциями (skill предпочитает `bigint identity`) |
| Время | `timestamptz` для событий; `date` для границ потока |
| Строки | Новые таблицы — `TEXT`; существующие миграции могут содержать `VARCHAR` — tech debt |
| FK | Индекс на каждой ссылающейся колонке |
| UNIQUE | `users`: частичные индексы на `telegram_id` и `LOWER(email)` при не-NULL; `participants (user_id, flow_id)`; порядок в module/lesson; `submissions (participant_id, assignment_id)` |
| CHECK | Роли, статусы в документируемом DDL; в коде — native enum |
| materials | CHECK по типу и наличию `url` / `content` |
| knowledge_items | `vector(1536)`; IVFFlat — после наполнения |
| Progress | VIEW, не таблица — без дублирования состояния |

## Компромиссы

- Документированный DDL использует `TEXT + CHECK`; ORM продолжит `CREATE TYPE` — зафиксировано в data-model.
- OpenAPI / контракт сдач при смене на `lesson_id` — итерация 5 ([tasklist-database.md](../../../../../../tasks/tasklist-database.md)).

## Отклонения от плана

- Нет.
