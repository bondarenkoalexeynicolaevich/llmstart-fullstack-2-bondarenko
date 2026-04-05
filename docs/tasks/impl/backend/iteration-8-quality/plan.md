# Итерация 8: качество и инженерные практики

## Цель и ценность

- **Цель:** единые команды качества в монорепозитории: `make lint` покрывает `bot/`, `backend/`, `scripts/`; `make test` — алиас на актуальные интеграционные тесты backend; документация и дорожная карта согласованы с фактом репозитория.
- **Ценность:** повторяемые проверки перед коммитом и готовность к подключению CI с теми же целями Makefile.

## Стек

- `ruff` (check + format), `pytest` через `make test` / `make test-backend`.
- Windows: переменная `PY` в Makefile без изменений.

## Задачи

| Задача | Папка |
|--------|--------|
| Makefile: `test`, ruff на `scripts/` | [`tasks/task-01-makefile-test-and-lint-scope/`](tasks/task-01-makefile-test-and-lint-scope/) |
| README Quality, `docs/tests.md` | [`tasks/task-02-readme-docs-quality/`](tasks/task-02-readme-docs-quality/) |
| Чеклист перед коммитом (README) | [`tasks/task-03-precommit-or-checklist/`](tasks/task-03-precommit-or-checklist/) |
| `docs/plan.md`, tasklist, summary | [`tasks/task-04-plan-tasklist-close/`](tasks/task-04-plan-tasklist-close/) |
| CI (при появлении) | [`tasks/task-05-ci-optional/`](tasks/task-05-ci-optional/) |

## Риски

- `make test` требует PostgreSQL и `TEST_DATABASE_URL` / `DATABASE_URL`; иначе тесты пропускаются или падают — см. [`docs/tests.md`](../../../tests.md).

## CI (зафиксировано)

Репозиторий без `.github/workflows`; при подключении CI использовать **`make lint`** и **`make test`**.

## Definition of Done (итерация)

- `make lint` включает `scripts/`.
- Существует `make test` (= `test-backend`).
- README содержит раздел про качество и чеклист перед коммитом; при необходимости — строка в `docs/tests.md` про `make test`.
- [`docs/plan.md`](../../../plan.md): сноска о боте/backend не противоречит итерации 7; в tasklist итерация 8 помечена ✅ со ссылкой на этот план и `summary.md`.
