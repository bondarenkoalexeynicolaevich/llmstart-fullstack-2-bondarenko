# Задача 04: Миграции и seed — summary

## Миграции

- **`005_users_telegram_username`**: колонка `users.telegram_username`, partial unique по `LOWER(telegram_username)`.

## Seed / demo

| Источник | Содержимое |
|----------|-------------|
| [`data/progress-import.v1.json`](../../../../../../../data/progress-import.v1.json) | Демо-поток UUID `…000001`, студенты, задания, сдачи, материалы и т.д. |
| [`scripts/seed_data.py`](../../../../../../../scripts/seed_data.py) | Async upsert через `INSERT … ON CONFLICT DO NOTHING`; в конце **UPDATE** демопреподавателя: `telegram_id=459032551`, `telegram_username=bondarenko_alexey_nikolaevich`, имя «Алексей Бондаренко» (**@Bondarenko_Alexey_Nikolaevich**). |

Цель PATCH после INSERT: идемпотентность поверх уже залитых старыми версиями JSON строк.

## Команды Makefile

`make db-seed` и алиас `make db-seed-frontend-demo` (то же действие).

## Участие преподавателя в демо-потоке

`participant` с `role=teacher` для того же пользователя уже в JSON (`participants`, id `…000033`).
