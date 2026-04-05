# task-01: Makefile — `test`, ruff на `scripts/`

## Что сделать

- Добавить цель **`test`**, зависящую от **`test-backend`** (одинаковый прогон pytest).
- Расширить **`lint`**: после `lint-bot` и `lint-backend` — проверка **`scripts/`** (`ruff check`).
- Расширить **`format`**: `ruff format` для `bot/`, `backend/`, **`scripts/`**.
- Обновить **`.PHONY`**: `test`, `lint-scripts` (если выделена отдельная цель).

## Файлы

- [`Makefile`](../../../../../../Makefile) в корне репозитория.

## Критерий готовности

- `make lint` запускает ruff для трёх деревьев; `make test` эквивалентен `make test-backend`.
