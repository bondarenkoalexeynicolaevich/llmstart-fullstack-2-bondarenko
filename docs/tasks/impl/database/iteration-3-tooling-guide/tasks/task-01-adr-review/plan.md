# Задача 01: Сверка с ADR-002 и ADR-003 (enum)

**Итерация:** [iteration-3-tooling-guide](../../plan.md)

## Цель

Убедиться, что стек backend (FastAPI, SQLAlchemy 2 async, Alembic) из [ADR-002](../../../../../../adr/adr-002-backend-http-orm.md) **не противоречит** текущей практике в репозитории; зафиксировать **отдельным ADR-003** решение по **PostgreSQL native ENUM** для доменных перечислений, т.к. это нетривиально для миграций и не дублирует ADR-002.

## Шаги

1. **Сверка с ADR-002:** прочитать ADR-002 и сопоставить с `backend/database.py`, `backend/api/deps.py`, расположением Alembic — при полном совпадении в ADR-003 **не повторять** выбор стека, а ссылаться на ADR-002 в тексте гайда (задача 02).
2. **Контекст enum в коде/миграциях:** зафиксировать в ADR-003 существующие типы (`member_role`, `dialog_message_role`, `submission_status` и т.д. по факту миграций), паттерн `postgresql.ENUM` + `SAEnum(..., native_enum=True)` в ORM.
3. **Создать** [docs/adr/adr-003-enum-strategy.md](../../../../../../adr/adr-003-enum-strategy.md):
   - контекст и варианты (native PG ENUM vs TEXT+CHECK);
   - решение: `native_enum=True`, правила `create_type` / `drop type` в Alembic;
   - последствия: явный `DROP TYPE` в downgrade при необходимости, `values_callable` при `create_type=False`, ограничения `ALTER TYPE ... ADD VALUE` в транзакциях.
4. **Обновить** [docs/adr/README.md](../../../../../../adr/README.md): добавить строку в таблицу списка ADR (номер, ссылка, статус, дата).

## DoD

- ADR-003 соответствует формату из `docs/adr/README.md` (контекст / варианты / решение / последствия).
- В README перечислен ADR-003 с корректной ссылкой.
- Нет дублирования содержания ADR-002 в ADR-003, кроме краткой отсылки при необходимости.

## Зависимости

- После выполнения — можно писать раздел «Enum» в `docs/tech/sqlalchemy-alembic-guide.md` (задача 02) со ссылкой на ADR-003.
