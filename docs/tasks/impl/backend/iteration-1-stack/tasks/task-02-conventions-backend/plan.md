# Задача 02: conventions для backend

## Цель

Разделить в `.cursor/rules/conventions.mdc` правила для **бота** (текущий MVP-контур) и **backend** (ядро, персистентность в БД), без противоречий [`docs/vision.md`](../../../../../../vision.md).

## Шаги

1. Уточнить описание rule (не только бот).
2. Секция **Bot**: сохранить KISS, структура `bot/`, ограничения MVP-без лишней инфраструктуры в самом боте; убрать глобальные формулировки «нет БД» / «только in-memory» как относящиеся ко всему проекту — перенести в контекст бота там, где уместно.
3. Секция **Backend**: структура `backend/` как в vision (`main.py`, `api/`, `services/`, `models/`, `config.py`); FastAPI + async SQLAlchemy + Alembic; логирование и секреты как в vision; `ruff` для будущего кода `backend/`.

## DoD

- Один файл conventions с явными секциями Bot / Backend.
- Нет противоречий vision по роли backend и БД.
