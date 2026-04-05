# Итерация 8: итог

## Сделано

- **Makefile:** цель **`test`** → **`test-backend`**; **`lint-scripts`** и включение в **`lint`**; **`format`** покрывает `scripts/`; `.PHONY` обновлён.
- **README:** раздел **«Проверки качества»** (`make lint`, `make format`, `make test`), зависимость тестов от БД и env; чеклист перед коммитом; в блоке backend — `make test` / `make test-backend`.
- **`docs/tests.md`:** в разделе запуска указан **`make test`**.
- **`docs/plan.md`:** сноска под сводной таблицей приведена в соответствие с закрытыми backend-итерациями 1–7 и схемой «бот → backend».
- **Tasklist:** итерация 8 помечена ✅, ссылки на `plan.md` и этот `summary.md`.
- **Workflow:** `plan.md` итерации и `plan.md` подзадач `task-01` … `task-05` (без отдельных `summary.md` по задачам в рамках этого прогона).

## Отклонения от плана

- **Pre-commit:** не добавлялись `.pre-commit-config.yaml` — достаточно чеклиста в README (минимум из formulation DoD).

## CI

- Репозиторий без GitHub Actions; при появлении CI использовать **`make lint`** и **`make test`** (`plan.md` итерации).

## Проверки (DoD)

| Критерий | Статус |
|----------|--------|
| `make lint` покрывает `bot/`, `backend/`, `scripts/` | Да |
| `make test` существует | Да |
| README, `docs/tests.md`, `docs/plan.md`, tasklist | Обновлены |
| `make lint` локально | Пройден |
