# Итерация 2: Проектирование схемы данных и ревью — summary

**Статус:** завершена  
**Tasklist:** [tasklist-database.md](../../../tasklist-database.md)

## Результат

- [docs/data-model.md](../../../data-model.md): логическая модель (Material, KnowledgeItem, Progress VIEW), физическая ER, DDL, индексы, примечания по pgvector и enum.
- [docs/spec/user-scenarios.md](../../../spec/user-scenarios.md): обновлены С1, С3, П3 и сводная таблица.
- Планы и summary задач: [tasks/task-01-logical-model/](tasks/task-01-logical-model/), [tasks/task-02-er-diagram/](tasks/task-02-er-diagram/), [tasks/task-03-review/](tasks/task-03-review/).

## Отклонения от плана исходного tasklist

- Material / KnowledgeItem / Progress спроектированы полностью (таблицы + VIEW), не отложены.

## Задачи

| Задача | Ссылка |
|--------|--------|
| 01 | [tasks/task-01-logical-model/summary.md](tasks/task-01-logical-model/summary.md) |
| 02 | [tasks/task-02-er-diagram/summary.md](tasks/task-02-er-diagram/summary.md) |
| 03 | [tasks/task-03-review/summary.md](tasks/task-03-review/summary.md) |

## Код

- `backend/` и миграции Alembic **не менялись**; целевая схема для migration `003` и последующих — в `docs/data-model.md`.
