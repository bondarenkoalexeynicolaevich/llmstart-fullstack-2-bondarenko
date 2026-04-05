# Итерация 3 (backend): итог

## Сделано

- Каталог [`backend/`](../../../../../backend/): FastAPI (`create_app`, `lifespan`, `GET /health`), конфиг через `python-dotenv`, async SQLAlchemy + `SessionDep`, роутер префикса [`/v1`](../../../../../backend/api/router.py).
- ORM и начальная схема: `users`, `flows`, `participants`, enum `member_role`, UNIQUE `(user_id, flow_id)`; Alembic async, ревизия `001_initial`.
- Корневой [`requirements.txt`](../../../../../requirements.txt), [`Makefile`](../../../../../Makefile): `run-backend`, `migrate-upgrade`, `lint-backend`; [`README.md`](../../../../../README.md) — запуск backend.
- Соответствие fastapi-templates: фабрика приложения, `lifespan`, `GET /health`, `APIRouter`, `Annotated` deps для сессии.

## Задачи

| Задача | Папка |
|--------|--------|
| Каркас FastAPI | [`tasks/task-01-scaffold-fastapi/`](tasks/task-01-scaffold-fastapi/) |
| Конфиг и сессия БД | [`tasks/task-02-config-database-session/`](tasks/task-02-config-database-session/) |
| ORM и Alembic | [`tasks/task-03-orm-alembic/`](tasks/task-03-orm-alembic/) |
| Makefile, README, зависимости | [`tasks/task-04-tooling-docs/`](tasks/task-04-tooling-docs/) |

## Проверка migrate → run-backend → health

**У агента в этой среде:** полный прогон не выполнен: Docker Engine к демону не подключался; с явным `DATABASE_URL` команда `make migrate-upgrade` / `alembic upgrade head` доходит до async-подключения к PostgreSQL (ожидаемо `ConnectionRefused`, если сервер не запущен).

**У владельца репозитория (разово):** в корневом `.env` задать `DATABASE_URL` (`postgresql+asyncpg://…`), поднять PostgreSQL → `make migrate-upgrade` → `make run-backend` → `curl http://127.0.0.1:8000/health` (ожидается `{"status":"ok"}`).

## Отклонения от плана

- Нет: отдельный `schemas/` — появится с реализацией endpoint'ов v1 (итерация 5).

## Следующий шаг

Итерация 4 tasklist-backend: базовые API-тесты.
