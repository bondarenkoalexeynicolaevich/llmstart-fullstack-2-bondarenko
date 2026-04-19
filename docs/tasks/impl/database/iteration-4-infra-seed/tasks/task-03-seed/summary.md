# Задача 03: JSON и seed-скрипт — summary

## Результат

- [`data/progress-import.v1.json`](../../../../../data/progress-import.v1.json): 1 поток, 3 пользователя (2 студента, 1 преподаватель), 3 участника, 5 заданий с `flow_id`, 4 сдачи с разными статусами; поле `_note` про обновление после migration 003.
- [`scripts/seed_data.py`](../../../../../scripts/seed_data.py): async, `get_settings()` → `init_database()` → `session_scope()`, вставки через `postgresql.insert(…).on_conflict_do_nothing(index_elements=["id"])`, порядок по FK.

## Отклонения от плана

- В лог выводится число попыток вставок из файла (не отдельный подсчёт «реально вставлено» через `RETURNING` — KISS).
