# Backend — Tasklist

## Обзор

Рабочий список итераций для серверного ядра на текущем этапе: выбор и фиксация стека, контракты API под сценарии «вопрос ассистенту» и «фиксация ДЗ», каркас сервиса, тесты, реализация, документация, перевод бота на HTTP-клиент к backend, базовые инженерные практики. Согласуется с [`docs/plan.md`](../plan.md) (итерации 1–2 и задел по структуре потока для сдач), [`docs/vision.md`](../vision.md), [`docs/data-model.md`](../data-model.md).

**Skills:** на этапах выбора стека и проектирования API имеет смысл рекомендовать подходящие agent skills (FastAPI, HTTP-контракты, async Python, uv, тесты). Подбор — через команду **`/find-skills`** в Cursor; типичные направления: шаблоны FastAPI, принципы REST/OpenAPI, asyncio/httpx, uv, pytest.

## Легенда статусов

| Символ | Статус |
|--------|--------|
| 📋 | Planned — запланирован |
| 🚧 | In Progress — в работе |
| ✅ | Done — завершён |

## Сводная таблица итераций

| № | Итерация | Статус | Артефакты планирования |
|---|----------|--------|------------------------|
| 1 | Стек, ADR/соглашения | ✅ | `docs/tasks/impl/backend/iteration-1-stack/plan.md`, `summary.md` |
| 2 | Контракты API (диалог + сдача ДЗ) | ✅ | [`impl/backend/iteration-2-api-contracts/plan.md`](impl/backend/iteration-2-api-contracts/plan.md), [`summary.md`](impl/backend/iteration-2-api-contracts/summary.md) |
| 3 | Каркас backend-сервиса | ✅ | [`impl/backend/iteration-3-skeleton/plan.md`](impl/backend/iteration-3-skeleton/plan.md), [`summary.md`](impl/backend/iteration-3-skeleton/summary.md) |
| 4 | Базовые API-тесты (сценарии как у бота) | ✅ | [`impl/backend/iteration-4-api-tests/plan.md`](impl/backend/iteration-4-api-tests/plan.md), [`summary.md`](impl/backend/iteration-4-api-tests/summary.md) |
| 5 | Endpoints и серверная логика | ✅ | [`impl/backend/iteration-5-implementation/plan.md`](impl/backend/iteration-5-implementation/plan.md), [`summary.md`](impl/backend/iteration-5-implementation/summary.md) |
| 6 | Документация backend | ✅ | [`impl/backend/iteration-6-docs/plan.md`](impl/backend/iteration-6-docs/plan.md), [`summary.md`](impl/backend/iteration-6-docs/summary.md) |
| 7 | Рефакторинг бота под API | ✅ | [`impl/backend/iteration-7-bot-backend-api/plan.md`](impl/backend/iteration-7-bot-backend-api/plan.md), [`summary.md`](impl/backend/iteration-7-bot-backend-api/summary.md) |
| 8 | Качество и инженерные практики | ✅ | [`impl/backend/iteration-8-quality/plan.md`](impl/backend/iteration-8-quality/plan.md), [`summary.md`](impl/backend/iteration-8-quality/summary.md) |

*Пути `docs/tasks/impl/backend/...` — по [`docs/templates/workflow.md`](../templates/workflow.md); при первом запуске создать каталоги и `plan.md` / `summary.md` по правилам workflow.*

---

## Итерация 1: Стек, ключевое решение, соглашения

**Цель:** Зафиксировать стек backend (язык, фреймворк HTTP, работа с БД, миграции), отразить решение в ADR при необходимости и обновить `.cursor/rules/conventions.mdc` под backend (без противоречий [`docs/vision.md`](../vision.md)).

### Состав работ

- Зафиксировать стек (ориентир: Python 3.12+, uv, ruff из vision; HTTP-слой и ORM — явным решением).
- При существенном отклонении от уже описанного — дополнение ADR в `docs/adr/` (например рядом с [`docs/adr/adr-001-database.md`](../adr/adr-001-database.md)).
- Обновить **соглашения репозитория** для backend: структура каталога `backend/`, именование, границы модулей (KISS).
- Актуализировать проектную документацию при изменении фактов: [`docs/vision.md`](../vision.md) (таблица технологий backend, при необходимости структура репозитория), [`docs/plan.md`](../plan.md) (если меняются зависимости этапов), [`README.md`](../../README.md), [`.env.example`](../../.env.example) (переменные backend: порт, `DATABASE_URL`, ключи только через примеры имён).

### Definition of Done

**Агент (самопроверка):**

- Решение по стеку записано (ADR или `plan.md` итерации + ссылка из tasklist).
- `conventions.mdc` отражает реальные правила для `backend/` и не спорит с vision.
- Все новые переменные окружения backend присутствуют в `.env.example` с комментариями.

**Пользователь:**

- Открыть `docs/adr/` и `.cursor/rules/conventions.mdc` — видно, на чём пишется backend.
- Сверить [`docs/vision.md`](../vision.md) — технологии backend не расходятся с выбранным стеком.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Убедиться, что ссылки из tasklist на ADR/conventions согласованы; нет «висящих» упоминаний старого одно-компонентного MVP только для bot в conventions. |
| **Пользователь** | Прочитать итерационный `summary.md` (после завершения) и diff в `conventions.mdc`. |
| **Команды** | При появлении `backend/` — добавить в `Makefile` цели вроде `lint-backend`, `run-backend` (см. итерацию 8); на шаге 1 достаточно зафиксировать это в плане итерации. |
| **Результат** | Понятный зафиксированный стек и правила кода; дальнейшие итерации опираются на этот документ. |

---

## Итерация 2: Проектирование API-контрактов

**Цель:** Специфицировать REST-контракты для двух базовых сценариев: **вопрос к ассистенту** (сообщение → ответ с учётом истории и промпта потока) и **фиксация выполненного ДЗ** (идентификация пользователя/участника, задание, запись [`Submission`](../data-model.md)). Учесть связи User → Participant → Flow, Assignment, DialogMessage.

### Состав работ

- Описать ресурсы, методы, тела запросов/ответов, коды ошибок; по возможности черновик OpenAPI (yaml/json) в репозитории или путь генерации из кода.
- Согласовать идентификаторы в API с [`docs/data-model.md`](../data-model.md) (UUID, роли, статусы `Submission`).
- Уточнить [`docs/integrations.md`](../integrations.md): кто вызывает backend (бот), заголовки/аутентификация сервиса на MVP (например внутренний токен или доверенная сеть — явно задокументировать).
- Обновить при необходимости [`docs/vision.md`](../vision.md) (диаграммы последовательностей, если пути отличаются от POST `/messages` / `/submissions`).

### Definition of Done

**Агент:**

- Есть согласованный список endpoint'ов и схем DTO; противоречий с data-model нет.
- Зафиксирован способ идентификации пользователя из бота (например `telegram_id` → User/Participant).

**Пользователь:**

- Открыть артефакт контракта (markdown/OpenAPI) и пройти сценарий «одно сообщение» и «одна сдача» глазами.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Cross-check полей с `data-model.md`; отметить в `plan.md` итерации ссылку на файл контракта. |
| **Пользователь** | Ревью OpenAPI/описания endpoint'ов. |
| **Команды** | Не обязательны; при наличии генерации схемы — задокументировать в итерации 6. |
| **Результат** | Реализация в итерации 5 не начинается с «придуманного на ходу» URL. |

---

## Итерация 3: Каркас backend-сервиса

**Цель:** Поднять минимальный повторяемый каркас: входная точка, конфиг из окружения, подключение к PostgreSQL, заготовка маршрутов, миграции для сущностей этапа 1 [`docs/plan.md`](../plan.md) (User, Flow, Participant и связи по [`docs/data-model.md`](../data-model.md)).

**Ценность:** «Пустой, но живой» backend с накатываемыми миграциями базового домена — основа для API-тестов (итерация 4) и реализации контрактов v1 (итерация 5).

**План итерации:** [`impl/backend/iteration-3-skeleton/plan.md`](impl/backend/iteration-3-skeleton/plan.md).

### Состав работ

- Создать `backend/` (или расширить заготовку из vision): `main`/приложение, `config`, модуль API, слой доступа к БД.
- Настроить миграции (инструмент — согласно итерации 1); начальная схема под базовый домен.
- Расширить [`.env.example`](../../.env.example), [`README.md`](../../README.md) черновиком запуска backend.

### Задачи

| Задача | Папка |
|--------|--------|
| Каркас FastAPI | [`impl/backend/iteration-3-skeleton/tasks/task-01-scaffold-fastapi/`](impl/backend/iteration-3-skeleton/tasks/task-01-scaffold-fastapi/) |
| Конфиг и сессия БД | [`impl/backend/iteration-3-skeleton/tasks/task-02-config-database-session/`](impl/backend/iteration-3-skeleton/tasks/task-02-config-database-session/) |
| ORM и Alembic | [`impl/backend/iteration-3-skeleton/tasks/task-03-orm-alembic/`](impl/backend/iteration-3-skeleton/tasks/task-03-orm-alembic/) |
| Makefile, README, зависимости | [`impl/backend/iteration-3-skeleton/tasks/task-04-tooling-docs/`](impl/backend/iteration-3-skeleton/tasks/task-04-tooling-docs/) |

### Definition of Done

**Агент:**

- Сервис стартует, логирует старт без секретов; к БД есть успешное подключение.
- Миграции накатываются одной командой (зафиксировать в README/Makefile).

**Пользователь:**

- Скопировать `.env`, выполнить шаги README, убедиться что процесс слушает порт и миграции проходят.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Прогнать миграции на чистой БД; проверить `ruff` для `backend/` если цель уже добавлена. |
| **Пользователь** | `make …` (как задокументировано) — сервер поднимается. |
| **Команды** | Добавить/обновить в `Makefile`: например `run-backend`, `migrate` или эквивалент uv/alembic. |
| **Результат** | Пустой но живой каркас с БД, готовый к реализации контрактов. |

---

## Итерация 4: Базовые API-тесты

**Цель:** Автотесты, покрывающие сценарии сообщений, **эквивалентные уже существующему потоку бота** (вопрос → ответ; при необходимости заглушка LLM/OpenRouter в тестах).

**План итерации:** [`impl/backend/iteration-4-api-tests/plan.md`](impl/backend/iteration-4-api-tests/plan.md).

### Состав работ

- Поднять приложение в тестах (TestClient / httpx ASGI); фикстуры БД.
- Тесты: happy-path для операции «сообщение ассистенту» и подготовка к тесту «сдача ДЗ» (после реализации endpoint'а).
- Не логировать и не ассертить содержимое пользовательских сообщений в открытом виде там, где это дублирует vision о приватности — достаточно статусов и идентификаторов.

### Задачи

| Задача | Папка |
|--------|-------|
| Зависимости и Makefile | [`impl/backend/iteration-4-api-tests/tasks/task-01-deps-makefile/`](impl/backend/iteration-4-api-tests/tasks/task-01-deps-makefile/) |
| conftest и фикстуры БД | [`impl/backend/iteration-4-api-tests/tasks/task-02-tests-fixtures/`](impl/backend/iteration-4-api-tests/tasks/task-02-tests-fixtures/) |
| Диалог и LLM-порт | [`impl/backend/iteration-4-api-tests/tasks/task-03-dialog-route/`](impl/backend/iteration-4-api-tests/tasks/task-03-dialog-route/) |
| Тесты и документация | [`impl/backend/iteration-4-api-tests/tasks/task-04-tests-and-docs/`](impl/backend/iteration-4-api-tests/tasks/task-04-tests-and-docs/) |

### Definition of Done

**Агент:**

- `pytest` (или принятый в проекте раннер) проходит локально для помеченного набора.
- Мок границы LLM не протекает в прод-код как единственный путь.

**Пользователь:**

- Запустить одну команду из README/Makefile и увидеть зелёные тесты.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Убедиться, что CI (если есть) или документация содержит команду тестов backend. |
| **Пользователь** | `make test-backend` / `uv run pytest backend/tests` — как зафиксировано. |
| **Команды** | **Актуализировать `Makefile`:** `test-backend` (и при необходимости `lint-backend`). |
| **Результат** | Регресс по контрактам диалога ловится тестами до ручной проверки через Telegram. |

---

## Итерация 5: Основные endpoint'ы и серверная логика

**Цель:** Реализовать договорённые endpoint'ы: персистентность DialogMessage, вызов OpenRouter по [`docs/integrations.md`](../integrations.md), операция создания Submission (и чтение статуса при необходимости для бота).

**План итерации:** [`impl/backend/iteration-5-implementation/plan.md`](impl/backend/iteration-5-implementation/plan.md). **Итог:** [`impl/backend/iteration-5-implementation/summary.md`](impl/backend/iteration-5-implementation/summary.md).

### Состав работ

- Реализация согласно итерации 2 и схеме данных; обработка ошибок и коды ответов.
- Логирование по [`docs/vision.md`](../vision.md): `user_id`/события, без текста сообщений и секретов.
- Актуализировать [`docs/data-model.md`](../data-model.md) только если в процессе выявлены необходимые уточнения полей; [`docs/plan.md`](../plan.md) — статусы итераций при завершении.

### Definition of Done

**Агент:**

- Интеграционные/контрактные тесты зелёные; ручной вызов curl/httpie к API даёт ожидаемую структуру ответа.
- Секреты только из env.

**Пользователь:**

- По README вызвать пример запроса к API (Postman/curl) и получить ответ ассистента на тестовой БД.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Прогнать `make lint` / полный набор линтеров репозитория; проверить отсутствие текста пользовательских сообщений в логах тестов. |
| **Пользователь** | Сквозной сценарий с реальным ключом OpenRouter на dev-стенде (опционально). |
| **Команды** | `make run-backend`, тесты, линт — единообразно в Makefile. |
| **Результат** | Backend выполняет роль ядра для диалога и фиксации сдачи на уровне MVP. |

---

## Итерация 6: Документирование backend

**Цель:** Воспроизводимый запуск, переменные окружения, OpenAPI (если есть), команды Make/README.

**План итерации:** [`impl/backend/iteration-6-docs/plan.md`](impl/backend/iteration-6-docs/plan.md). **Итог:** [`impl/backend/iteration-6-docs/summary.md`](impl/backend/iteration-6-docs/summary.md).

### Состав работ

- [`README.md`](../../README.md): раздел backend (установка, миграции, запуск, тесты).
- [`.env.example`](../../.env.example): полный перечень переменных backend + краткие комментарии.
- Экспорт/путь к OpenAPI (`/openapi.json` или статический файл) — описать в README.
- При изменении внешних контрактов — [`docs/integrations.md`](../integrations.md); общая дорожка — [`docs/plan.md`](../plan.md).

### Definition of Done

**Агент:**

- Новый разработчик по README поднимает backend без «скрытых» шагов.
- OpenAPI доступен или явно помечен как «генерируется при старте».

**Пользователь:**

- Пройти README с нуля на чистой машине (или новом клоне).

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Сверить README с фактическим Makefile. |
| **Пользователь** | Открыть Swagger UI / скачать `openapi.json`. |
| **Команды** | Все команды из README существуют в `Makefile`. |
| **Результат** | Документация не отстаёт от кода. |

---

## Итерация 7: Рефакторинг бота под backend API

**Цель:** Бот выступает HTTP-клиентом: вопросы и (по готовности) сдачи идут в backend, локальный `llm_client` в боте не используется для боевого пути.

### Состав работ

- Заменить прямые вызовы LLM на клиент к API (base URL, таймауты, обработка ошибок).
- Конфиг бота: URL backend, при необходимости служебный ключ; обновить [`.env.example`](../../.env.example).
- Синхронизировать с **`tasklist-bot.md`** (если выделен отдельно): цели и DoD бота.

### Definition of Done

**Агент:**

- В коде бота нет обхода backend для сценария ответа ассистента.
- Линт для `bot/` проходит.

**Пользователь:**

- Запустить backend + бот, отправить сообщение в Telegram — ответ приходит через API.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | E2E-smoke: поднять оба процесса, проверить логи (без контента сообщений). |
| **Пользователь** | Тот же сценарий в своём Telegram. |
| **Команды** | `make run-backend`, `make run` (бот) — в README порядок запуска. |
| **Результат** | Схема из [`docs/vision.md`](../vision.md) «Bot → Backend → DB/LLM» соблюдена. |

---

## Итерация 8: Базовое качество и инженерные практики

**Цель:** Единые команды качества для монорепозитория, линт и тесты backend не хуже bot.

**План итерации:** [`impl/backend/iteration-8-quality/plan.md`](impl/backend/iteration-8-quality/plan.md). **Итог:** [`impl/backend/iteration-8-quality/summary.md`](impl/backend/iteration-8-quality/summary.md).

### Состав работ

- `Makefile`: агрегаты `lint` (bot + backend + `scripts/`), цель `test` (= `test-backend`).
- Pre-commit или документированный чеклист перед коммитом — по желанию команды, минимум — `ruff` для `backend/`.
- Обновить [`docs/plan.md`](../plan.md) и строку статуса в **этом** tasklist для завершённых итераций.

### Definition of Done

**Агент:**

- Одна команда проверяет весь затронутый Python-код репозитория.
- В tasklist обновлены статусы итераций ✅ после реальных summary.

**Пользователь:**

- Выполнить `make lint` и `make test` (или эквивалент) — без ошибок.

### Проверки после блока

| Кто | Что сделать |
|-----|-------------|
| **Агент** | Убедиться, что CI (если подключится) использует те же цели. |
| **Пользователь** | Прочитать раздел README «Проверки качества». |
| **Команды** | **`make lint`**, **`make test`** / **`make test-backend`** — актуальны и задокументированы. |
| **Результат** | Репозиторий готов к следующей фазе ([`docs/plan.md`](../plan.md) итерация 3). |

---

## Краткая карта актуализации документации

| Файл | Когда трогать |
|------|----------------|
| [`docs/vision.md`](../vision.md) | Стек, диаграммы API, структура репозитория |
| [`docs/data-model.md`](../data-model.md) | Уточнение полей после проектирования или реализации |
| [`docs/integrations.md`](../integrations.md) | Аутентификация bot→backend, OpenRouter, URL |
| [`docs/plan.md`](../plan.md) | Статусы дорожной карты, зависимости этапов |
| [`README.md`](../../README.md) | Запуск, команды, порядок сервисов |
| [`.env.example`](../../.env.example) | Каждая новая переменная backend и бота |
