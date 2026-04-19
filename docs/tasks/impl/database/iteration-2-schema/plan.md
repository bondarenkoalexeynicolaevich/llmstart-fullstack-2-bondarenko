# Итерация 2: Проектирование схемы данных и ревью

**Область:** database  
**Статус:** завершена (см. [summary.md](summary.md))  
**Связь:** [tasklist-database.md](../../../tasklist-database.md)

## Цель

Актуализировать **логическую** и **физическую** модель PostgreSQL: Module, Lesson, Assignment.lesson_id, Material, KnowledgeItem, Progress (VIEW); исправить модель `User.email`; нарисовать физическую ER-диаграмму; провести ревью по skill `postgresql-table-design`.

## Ценность

Единая согласованная схема для миграций (итерация 4–5) без расхождений между документом и целевой БД.

## Источники

- [docs/spec/user-scenarios.md](../../../../spec/user-scenarios.md)
- [docs/data-model.md](../../../../data-model.md)
- Skill: `postgresql-table-design`
- Текущий код: `backend/models/`, Alembic (до migration 003 `assignments` ещё с `flow_id`)

## Состав работ

| # | Задача | Папка |
|---|--------|--------|
| 01 | Логическая модель + Material/KnowledgeItem/Progress, email nullable, user-scenarios | [tasks/task-01-logical-model/](tasks/task-01-logical-model/) |
| 02 | Физическая ER-диаграмма и DDL в `docs/data-model.md` | [tasks/task-02-er-diagram/](tasks/task-02-er-diagram/) |
| 03 | Ревью postgresql-table-design, summary по задачам и итерации, tasklist | [tasks/task-03-review/](tasks/task-03-review/) |

## Definition of Done (итерация)

- `docs/data-model.md`: логика + физическая схема, Module/Lesson/Assignment.lesson_id, Material, KnowledgeItem, VIEW Progress; `email` nullable, UNIQUE.
- `docs/spec/user-scenarios.md`: Material в С1/П3; KnowledgeItem в С1; Progress (VIEW) в С3 при необходимости.
- Ревью skill зафиксировано в `tasks/task-03-review/summary.md` и `iteration-2-schema/summary.md`.
- [tasklist-database.md](../../../tasklist-database.md): итерация 2 отмечена выполненной.

## Файлы

- Обновляются: `docs/data-model.md`, `docs/spec/user-scenarios.md`, `docs/tasks/tasklist-database.md`
- Создаются: планы/саммари задач в `tasks/task-*/`

Код (`backend/`) в рамках итерации 2 **не меняется** (миграция 003 — итерация 5).
