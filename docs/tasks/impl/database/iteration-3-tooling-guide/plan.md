# Итерация 3: Инструменты миграций и доступа к БД — ADR и практическое руководство

**Область:** database  
**Статус:** завершена (см. [summary.md](summary.md))  
**Связь:** [tasklist-database.md](../../../tasklist-database.md)

## Цель

Зафиксировать паттерны работы с SQLAlchemy async + Alembic в виде **практической справки** и отдельного **ADR-003** по стратегии enum в PostgreSQL (native `ENUM` vs альтернативы), согласованного с уже принятыми ADR-001/002.

## Ценность

Разработчик открывает один гайд и находит: async-сессии/DI, цикл Alembic, именование ревизий, работу с enum и seed; решение по enum не остаётся неявным — его можно сослаться из миграций и code review.

## Источники

- [docs/adr/adr-002-backend-http-orm.md](../../../../adr/adr-002-backend-http-orm.md)
- Фактический код: `backend/database.py`, `backend/api/deps.py`, Alembic в `backend/alembic/`
- [docs/tasks/tasklist-database.md](../../../tasklist-database.md) (строка про enum и итерацию 3)

## Состав работ

| # | Задача | Папка |
|---|--------|--------|
| 01 | Сверка с ADR-002; создание ADR-003; обновление `docs/adr/README.md` | [tasks/task-01-adr-review/](tasks/task-01-adr-review/) |
| 02 | Написание [docs/tech/sqlalchemy-alembic-guide.md](../../../../tech/sqlalchemy-alembic-guide.md) | [tasks/task-02-guide/](tasks/task-02-guide/) |
| 03 | Заполнение `summary.md` итерации после задач 01–02 | [tasks/task-03-summary/](tasks/task-03-summary/) |

## Definition of Done (итерация)

- `docs/adr/adr-003-enum-strategy.md` создан; в `docs/adr/README.md` есть строка ADR-003.
- `docs/tech/sqlalchemy-alembic-guide.md` создан и согласован с кодом в `backend/` (пути, `make migrate-upgrade`, паттерны enum).
- [tasklist-database.md](../../../tasklist-database.md): итерация 3 отражает завершение или актуальный статус по workflow.

## Вне скоупа

- Новые миграции `003_*` (итерация 5).
- Docker Compose, `make db-*`, `scripts/seed_data.py` (итерация 4).
- ORM-модели Module/Lesson (итерация 5).

## Файлы

- Создаются: `docs/adr/adr-003-enum-strategy.md`, `docs/tech/sqlalchemy-alembic-guide.md`, планы задач в `tasks/task-*/plan.md`, по завершении — `summary.md` итерации и задач.
- Обновляется: `docs/adr/README.md`, `docs/tasks/tasklist-database.md`.
