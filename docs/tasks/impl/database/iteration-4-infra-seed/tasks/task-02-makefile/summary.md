# Задача 02: Makefile `db-*` — summary

## Результат

В [`Makefile`](../../../../../Makefile) добавлены цели:

- `db-up`, `db-down`, `db-reset`, `db-shell`, `db-logs`, `db-status`, `db-seed`
- В `.PHONY` перечислены новые цели.

`db-reset`: `docker compose down -v` → `db-up` → `migrate-upgrade`.

`db-shell`: `docker compose exec db psql -U app -d app` (должно совпадать с дефолтами из `.env.example`; при смене пользователя/БД — править команду или env).

## Отклонения от плана

- `db-up` без флага `--wait` для совместимости со старыми версиями Docker Compose; после `db-up` краткая пауза перед первым `migrate-upgrade` может понадобиться на медленных машинах (см. README).
