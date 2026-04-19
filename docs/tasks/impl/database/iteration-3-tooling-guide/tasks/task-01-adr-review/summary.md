# Задача 01: Сверка с ADR-002 и ADR-003 — summary

**Статус:** завершена  
**Итерация:** [iteration-3-tooling-guide](../../plan.md)

## Результат

- Стек из [ADR-002](../../../../../../adr/adr-002-backend-http-orm.md) (FastAPI, SQLAlchemy 2 async, Alembic) подтверждён; отдельный ADR по стеку не заводился.
- Добавлен [ADR-003](../../../../../../adr/adr-003-enum-strategy.md): native PostgreSQL ENUM, правила `create_type` / `values_callable` / `DROP TYPE`, ссылка на существующие типы в миграциях.
- Обновлён [docs/adr/README.md](../../../../../../adr/README.md) — строка ADR-003 в таблице решений.

## Отклонения от плана

- Нет.
