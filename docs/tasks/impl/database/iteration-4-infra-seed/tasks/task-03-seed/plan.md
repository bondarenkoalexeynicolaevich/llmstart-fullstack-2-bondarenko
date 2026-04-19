# Задача 03: `data/progress-import.v1.json` и `scripts/seed_data.py`

## Что делаем

1. **`data/progress-import.v1.json`** — минимальный осмысленный набор под схему **001+002**:
   - 1 поток, 5 заданий (`assignments` с `flow_id`), 2 студента + 1 преподаватель как участники, разный прогресс сдач (`submissions`).
   - Поле **`_note`** в JSON: напоминание обновить формат после migration 003.

2. **`scripts/seed_data.py`**:
   - Загрузка `.env`, `get_settings()` → `init_database()` → async-вставки → `dispose_database()`.
   - Идемпотентность: `INSERT … ON CONFLICT (id) DO NOTHING` (PostgreSQL) по таблицам в порядке FK: flows → users → participants → assignments → submissions.
   - `asyncio.run(main())`, логирование числа затронутых строк (по желанию — через `RETURNING` или подсчёт до/после).

## Критерии готовности

- `make db-seed` завершается с кодом 0 при применённых миграциях.
- Повторный запуск не ломается (conflict do nothing).
