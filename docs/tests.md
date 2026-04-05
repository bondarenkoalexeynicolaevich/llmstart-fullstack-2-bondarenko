# Тесты

Сводка по автотестам репозитория. Описаны **интеграционные API-тесты backend** (`backend/tests/`).

## Запуск

- Из корня: **`make test-backend`** или **`pytest`** / **`pytest backend/tests`** (в [`pytest.ini`](../pytest.ini) задано `testpaths = backend/tests`).
- Нужны **PostgreSQL** и URL в `.env` в корне репозитория: **`TEST_DATABASE_URL`** (предпочтительно для отдельной тестовой БД) или **`DATABASE_URL`**.
- Если URL не задан — сессионная фикстура **`migrated_database`** делает **`pytest.skip`** с подсказкой.
- Перед тестами фикстура вызывает **`alembic upgrade head`** (конфиг `backend/alembic.ini`), цепочка ревизий включает **`001_initial`** и **`002_dialog_submissions`**.

## Маркеры и окружение

- В [`pytest.ini`](../pytest.ini) объявлен маркер **`integration`**.
- В [`backend/tests/conftest.py`](../backend/tests/conftest.py) на модуль повешен **`pytestmark = pytest.mark.integration`** — все тесты в этом каталоге считаются интеграционными.
- Автофикстура **`_test_env`** подставляет **`INTERNAL_API_TOKEN`** равным константе **`TEST_TOKEN`** из [`backend/tests/constants.py`](../backend/tests/constants.py) (`"test-internal-api-token"`), чтобы не зависеть от секрета в `.env` при прогоне.

## Фикстуры и данные

- Фикстура **`client`**: перед каждым тестом вызывается **`truncate_core_tables_sync()`** — `TRUNCATE submissions, dialog_messages, assignments, participants, users, flows … CASCADE` (sync **psycopg**, см. `conftest.py`).
- Вспомогательные сиды: **`seed_flow_user_participant`**, **`seed_assignment`**.

## Структура `backend/tests/`

| Файл | Назначение |
|------|------------|
| [`constants.py`](../backend/tests/constants.py) | Общие константы (`TEST_TOKEN`) |
| [`conftest.py`](../backend/tests/conftest.py) | Фикстуры `app`, `client`, миграции, сиды |
| [`test_health.py`](../backend/tests/test_health.py) | `GET /health` |
| [`test_dialog_auth.py`](../backend/tests/test_dialog_auth.py) | Bearer для `POST /v1/dialog-messages` |
| [`test_dialog_messages.py`](../backend/tests/test_dialog_messages.py) | Диалог: happy-path и 404 |
| [`test_submissions_placeholder.py`](../backend/tests/test_submissions_placeholder.py) | `POST /v1/submissions` (имя файла историческое) |

## Перечень тестов

| № | Файл | Тест | Краткое описание |
|---|------|------|------------------|
| 1 | `test_health.py` | `test_health_ok` | `GET /health` → 200 и `{"status":"ok"}` |
| 2 | `test_dialog_auth.py` | `test_dialog_messages_missing_bearer_returns_401` | `POST /v1/dialog-messages` без `Authorization` → 401, код `unauthorized` |
| 3 | `test_dialog_auth.py` | `test_dialog_messages_wrong_bearer_returns_401` | Неверный Bearer → 401, `unauthorized` |
| 4 | `test_dialog_auth.py` | `test_dialog_messages_valid_bearer_returns_404_when_flow_missing` | Валидный Bearer, случайный `flow_id` без строки в БД → 404 `flow_not_found` |
| 5 | `test_dialog_messages.py` | `test_dialog_messages_happy_path` | Сид User/Flow/Participant, подмена **`get_llm_client`** фейковым LLM → 200, `reply_text` и UUID сообщений; в БД **две** строки `dialog_messages` участника; `content` в запросе с пробелами — проверка trim |
| 6 | `test_dialog_messages.py` | `test_dialog_messages_flow_not_found` | Несуществующий поток → 404 `flow_not_found` |
| 7 | `test_dialog_messages.py` | `test_dialog_messages_participant_not_found` | Поток и участник есть для одного `telegram_user_id`, запрос с другим id → 404 `participant_not_found` |
| 8 | `test_submissions_placeholder.py` | `test_submissions_happy_path` | `POST /v1/submissions` с сидом задания в том же flow → 201 и тело по контракту |
| 9 | `test_submissions_placeholder.py` | `test_submissions_assignment_not_found` | Задание из другого потока → 404 `assignment_not_found` |
| 10 | `test_submissions_placeholder.py` | `test_submissions_duplicate_conflict` | Повторная сдача того же задания тем же участником → 409 `submission_already_exists` |

Условие «проходит»: доступная БД, успешный `alembic upgrade head`, зависимости из [`requirements.txt`](../requirements.txt).

## Бот

Отдельного набора pytest для каталога `bot/` нет. Проверки: **`make lint-bot`**, ручной E2E (см. [README.md](../README.md)), опционально **`make smoke-dialog`** при запущенном backend (переменные `BACKEND_BASE_URL`, `INTERNAL_API_TOKEN`, `FLOW_ID`, `TELEGRAM_USER_ID`).
