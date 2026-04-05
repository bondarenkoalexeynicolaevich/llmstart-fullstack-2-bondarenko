# Сопровождение учебного потока с AI-ассистентом

Система для студентов и преподавателей курсов по разработке и LLM: поддержка между занятиями, прогресс и обзор потока.

> Учебный проект в рамках модуля по AI-driven fullstack-разработке.

## О проекте

Между занятиями студенты часто теряют контекст курса. Продукт даёт AI-ассистента в Telegram и (по плану) веб-клиент с единым backend. Роли: **студент**, **преподаватель**.

## Архитектура

Целевая схема (каталог **`backend/`** и команды запуска — см. ниже; стек в [ADR-002](docs/adr/adr-002-backend-http-orm.md)):

```mermaid
graph LR
  Student[Студент]
  Teacher[Преподаватель]
  Bot[Telegram-бот]
  Web[Веб-клиент]
  Backend[Backend]
  DB[(PostgreSQL)]
  LLM[LLM / OpenRouter]

  Student --> Bot
  Student --> Web
  Teacher --> Web
  Bot --> Backend
  Web --> Backend
  Backend --> DB
  Backend --> LLM
```

Подробности потоков запросов — [docs/vision.md](docs/vision.md).

## Статус

| № | Этап | Статус |
|---|------|--------|
| 1 | Ядро backend и данные | 📋 Planned |
| 2 | Диалог и тонкий бот | 📋 Planned |
| 3 | Структура потока и задания | 📋 Planned |
| 4 | Веб: студент | 📋 Planned |
| 5 | Веб: преподаватель | 📋 Planned |
| 6 | Эксплуатация MVP | 📋 Planned |

DoD и даты — [docs/plan.md](docs/plan.md). Реализация HTTP API v1 для сценариев «сообщение ассистенту» и «сдача ДЗ» в **`backend/`** описана контрактом [docs/api/backend-v1.openapi.yaml](docs/api/backend-v1.openapi.yaml) (дорожная карта — [docs/tasks/tasklist-backend.md](docs/tasks/tasklist-backend.md)).

## Документация

- [Идея продукта](docs/idea.md)
- [Архитектурное видение](docs/vision.md)
- [Модель данных](docs/data-model.md)
- [Интеграции](docs/integrations.md)
- [План](docs/plan.md)
- [Задачи](docs/tasks/)
- [Тесты](docs/tests.md)

## Быстрый старт

Общий **`make install`** из корня ставит зависимости для бота и backend.

### Backend (сначала)

1. **Окружение:** Python **3.12+** и [**uv**](https://docs.astral.sh/uv/getting-started/installation/) в `PATH` (в `Makefile` зависимости ставятся через `uv pip install`).
2. Поднять **PostgreSQL** (свой инстанс или, например, `docker run -d --name pg -p 5432:5432 -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=app postgres:16` и строка вида `postgresql+asyncpg://postgres:dev@127.0.0.1:5432/app`). Скопировать [`.env.example`](.env.example) в `.env`. Обязательно: **`DATABASE_URL`**. Для **`/v1/*`** задайте **`INTERNAL_API_TOKEN`**. Для ответа ассистента в **`POST /v1/dialog-messages`** на backend нужен **`OPENROUTER_API_KEY`** (опционально `LLM_MODEL`, `OPENROUTER_BASE_URL`, `LLM_TEMPERATURE`, `MAX_HISTORY_MESSAGES`).
3. **`make migrate-upgrade`** — Alembic до `head`.
4. **`make run-backend`** — сервис на `API_HOST`:`API_PORT`; проверка `GET /health` → `{"status":"ok"}`.
5. **`make test-backend`** — интеграционные тесты (БД; см. [docs/tests.md](docs/tests.md)).

### Бот (HTTP → backend)

В том же `.env`, что и backend:

- **`BOT_TOKEN`** — Telegram.
- **`BACKEND_BASE_URL`** — например `http://127.0.0.1:8000` (как у запущенного API).
- **`INTERNAL_API_TOKEN`** — **тот же**, что у backend (заголовок `Authorization: Bearer` при вызове API).
- **`FLOW_ID`** — UUID существующей строки **`flows`** (см. ниже).

Прямой OpenRouter и системный промпт **в боте не задаются**: LLM и `Flow.system_prompt` остаются на сервере.

**Данные в БД для диалога:** для пары `FLOW_ID` + ваш `telegram_user_id` сервер должен найти `User` (поле **`telegram_id` = числовой id в Telegram) и `Participant`, связывающий этого пользователя с потоком. Иначе API вернёт **404** (`flow_not_found` / `participant_not_found`). Для локальной отладки можно завести строки вручную (по аналогии с сидированием в [`backend/tests/conftest.py`](backend/tests/conftest.py), функция `seed_flow_user_participant`).

Запуск бота из корня: **`make run`**. Линт: **`make lint`**, только бот: **`make lint-bot`**. Форматирование: **`make format`**.

### Smoke

- **API:** при работающем backend и заполненном `.env` задайте **`TELEGRAM_USER_ID`** (тот же id, что в `users.telegram_id`) и выполните **`make smoke-dialog`** — скрипт [`scripts/smoke_dialog_api.py`](scripts/smoke_dialog_api.py) шлёт короткое сообщение и печатает JSON со статусом (удобно до проверки Telegram).
- **E2E:** `make run-backend` → `make run` → сообщение боту в Telegram; в логах бота не должно быть **текста** пользовательских сообщений (только `user_id` и события).

### OpenAPI / схема API

После `make run-backend`:

- **Runtime:** `http://<API_HOST>:<API_PORT>/openapi.json` — схема, которую отдаёт FastAPI; в браузере удобно открыть **`/docs`** (Swagger UI) или **`/redoc`**.
- **Design-time:** канонический текст контракта для ревью — [docs/api/backend-v1.openapi.yaml](docs/api/backend-v1.openapi.yaml). Пока нет автоматической сверки, JSON с сервера и YAML в репозитории могут незначительно различаться до ручной синхронизации.

### Примеры вызова API (curl)

Все запросы к `/v1/...` — с заголовком `Authorization: Bearer <INTERNAL_API_TOKEN>`. В теле подставьте реальные UUID и `telegram_user_id`, существующие в вашей БД (строки в `flows`, `users`, `participants`; для сдачи — ещё `assignments` в том же потоке). Без данных резолв вернёт 404 по контракту.

```bash
BASE_URL=http://127.0.0.1:8000
TOKEN=your-internal-api-token

curl -sS "$BASE_URL/health"

curl -sS -X POST "$BASE_URL/v1/dialog-messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flow_id":"00000000-0000-0000-0000-000000000001","telegram_user_id":42424242,"content":"Короткий вопрос по материалу"}'

curl -sS -X POST "$BASE_URL/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flow_id":"00000000-0000-0000-0000-000000000001","telegram_user_id":42424242,"assignment_id":"00000000-0000-0000-0000-000000000002","comment":null}'
```

Канонические схемы тел и кодов ошибок — в [OpenAPI YAML](docs/api/backend-v1.openapi.yaml); на запущенном сервисе см. раздел **OpenAPI / схема API** выше.

**Веб и полный стенд MVP** — по плану продукта и задачам бота (переход бота на HTTP к backend); ориентир — [docs/plan.md](docs/plan.md) и [docs/tasks/tasklist-backend.md](docs/tasks/tasklist-backend.md).
