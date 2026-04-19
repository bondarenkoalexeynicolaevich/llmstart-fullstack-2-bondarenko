# Задача 03: Ревью postgresql-table-design и закрытие итерации

**Итерация:** [iteration-2-schema](../../plan.md)

## Цель

Пройти чеклист skill `postgresql-table-design` по каждой таблице/VIEW; зафиксировать компромиссы (UUID PK, VARCHAR в существующих миграциях, native enum в ORM vs TEXT+CHECK в документе, IVFFlat после наполнения). Обновить [tasklist-database.md](../../../../../../tasks/tasklist-database.md).

## Шаги

1. Чеклист: PK, FK + индексы, UNIQUE, NOT NULL, типы времени (`timestamptz`), именование snake_case.
2. `summary.md` задачи и итерации.
3. Итерация 2 в tasklist → ✅.

## DoD

- В summary перечислены принятые компромиссы и открытые пункты для итерации 5 (OpenAPI при смене контракта сдач).
