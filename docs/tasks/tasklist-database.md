# Database — Tasklist

## Обзор

Рабочий список итераций для **полноценного слоя данных** на текущем этапе: от продуктовых сценариев и согласованной схемы до инфраструктуры PostgreSQL, seed из `data/progress-import.v1.json`, ORM/доступа к данным и интеграции в backend (в т.ч. замена упрощённой модели `Assignment.flow_id` на `Assignment.lesson_id` и введение `Module` / `Lesson`). Согласуется с `[docs/plan.md](../plan.md)`, `[docs/vision.md](../vision.md)`, `[docs/data-model.md](../data-model.md)`, `[docs/api/backend-v1.openapi.yaml](../api/backend-v1.openapi.yaml)`, ADR `[docs/adr/adr-001-database.md](../adr/adr-001-database.md)`, `[docs/adr/adr-002-backend-http-orm.md](../adr/adr-002-backend-http-orm.md)`, `[docs/adr/adr-003-enum-strategy.md](../adr/adr-003-enum-strategy.md)` (enum в PostgreSQL).

**Текущее состояние репозитория (на момент составления tasklist):**

- SQLAlchemy ORM + Alembic: `001` … `004` (в т.ч. `modules` / `lessons` / `materials`, `assignments.lesson_id`, `knowledge_items`, VIEW прогресса; см. `docs/data-model.md`).
- **Итерация 4 (инфра/seed):** в корне есть `docker-compose.yml`, `data/progress-import.v1.json`, цели `make db-*` и скрипты `scripts/seed_data.py`, `scripts/db_inspect.py` (см. [iteration-4-infra-seed](impl/database/iteration-4-infra-seed/summary.md)).

**Skills:** на этапе проектирования таблиц — skill `**postgresql-table-design`** (ревью индексов, constraints, типов). Подбор прочих skills — через `**/find-skills**` в Cursor (uv, async Python, pytest и т.д.).

### Аудит tasklist ↔ postgresql-table-design (целевая схема)

Сверка требований skill **postgresql-table-design** с целевым DDL в [`docs/data-model.md`](../data-model.md) (не с ещё не накатанными миграциями в `backend/`).

| Критерий skill | Статус | Комментарий |
| ---------------- | ------ | ------------- |
| PK на справочных таблицах | OK | UUID + `gen_random_uuid()` — осознанный компромисс с уже существующими миграциями (skill предпочитает `bigint identity`). |
| `timestamptz` для событий | OK | `created_at`, `joined_at`, `submitted_at`, `scheduled_at`; границы потока — `date`. |
| Строки — `TEXT` | Частично | В целевом DDL — `TEXT`. В уже применённых миграциях возможны `VARCHAR(n)` — зафиксировано как tech debt в data-model. |
| Индексы на FK | OK | В целевом DDL отдельный B-tree на каждой ссылающейся колонке. |
| Уникальность при nullable `email` / `telegram_id` | OK | Частичные уникальные индексы (`WHERE … IS NOT NULL`), не `NULLS NOT DISTINCT` на всю колонку (иначе только одна строка с NULL). |
| Составные UNIQUE | OK | `(user_id, flow_id)`, порядок в module/lesson, `(participant_id, assignment_id)`. |
| CHECK / доменные ограничения | OK | `materials`: тип и наличие `url`/`content`; роли и статусы в документируемом DDL. |
| Enum в PostgreSQL | OK | Проект использует native PG ENUM; зафиксировано в [ADR-003](../adr/adr-003-enum-strategy.md) и [sqlalchemy-alembic-guide.md](../tech/sqlalchemy-alembic-guide.md). |
| pgvector | OK | `knowledge_items.embedding`, IVFFlat после наполнения; `CREATE EXTENSION vector` в миграции при внедрении. |
| Нормализация | OK | Связи поток → модуль → занятие → задание; VIEW прогресса без дублирования фактов сдачи. |

**Расхождение roadmap ↔ data-model:** в описании **итерации 5** ниже изначально не перечислены `materials`, `knowledge_items` и VIEW — добавлено в состав работ. **Итерация 4** (seed): при появлении полной схемы в JSON/скрипте учесть модули/занятия и при необходимости материалы.

## Легенда статусов


| Символ | Статус                 |
| ------ | ---------------------- |
| 📋     | Planned — запланирован |
| 🚧     | In Progress — в работе |
| ✅      | Done — завершён        |


## Сводная таблица итераций


| №   | Итерация                                            | Статус | Артефакты планирования                                                           |
| --- | --------------------------------------------------- | ------ | -------------------------------------------------------------------------------- |
| 1   | Сценарии пользователя и требования к данным         | ✅      | `docs/tasks/impl/database/iteration-1-scenarios/plan.md`, `summary.md`           |
| 2   | Проектирование схемы и ревью                        | ✅      | `docs/tasks/impl/database/iteration-2-schema/plan.md`, `summary.md`              |
| 3   | Практическое руководство по миграциям и ORM         | ✅      | `docs/tasks/impl/database/iteration-3-tooling-guide/plan.md`, `summary.md`       |
| 4   | Инфраструктура БД, seed, проверка данных            | ✅      | `docs/tasks/impl/database/iteration-4-infra-seed/plan.md`, `summary.md`          |
| 5   | ORM, сервисы, API read-контур, интеграция в backend | ✅      | `docs/tasks/impl/database/iteration-5-backend-integration/plan.md`, `summary.md` |


*Пути `docs/tasks/impl/database/...` — по `[docs/templates/workflow.md](../templates/workflow.md)`; перед работой создать каталоги и `plan.md` / `summary.md` по правилам workflow.*

---

## Итерация 1: Пользовательские сценарии и требования к данным

**Цель:** Зафиксировать без «технической кухни», что должны **видеть и уметь** студент и преподаватель в базовых сценариях, чтобы заложить основу под будущий frontend и однозначно понять, какие **сущности и связи** нужны в данных.

**Ценность:** Схема и API в следующих итерациях не проектируются «в вакууме» — каждая сущность привязана к сценарию.

### Состав работ

- Описать **2–3 сценария для студента** (бот и/или веб на уровне намерений): вопрос ассистенту и история; отметка сдачи и статус; просмотр прогресса по модулям/занятиям.
- Описать **2–3 сценария для преподавателя**: сводка по группе и сдачам; активность/обращения; управление структурой потока (модули → занятия → задания).
- Для каждого сценария явно указать, какие объекты из `[docs/data-model.md](../data-model.md)` участвуют; зафиксировать **пробелы** (если сущности не хватает).
- Добавить в `[docs/data-model.md](../data-model.md)` краткие аннотации вида «нужно для сценария …» (или отдельный подраздел со ссылками на сценарии).
- Подготовить артефакты итерации: `docs/tasks/impl/database/iteration-1-scenarios/plan.md`, по завершении — `summary.md`.

### Задачи (кратко)


| Задача | Содержание                                              |
| ------ | ------------------------------------------------------- |
| 01     | Сценарии студента (текст + маппинг на сущности)         |
| 02     | Сценарии преподавателя (текст + маппинг)                |
| 03     | Аннотации в `docs/data-model.md`, итоговый `summary.md` |


### Definition of Done

**Агент (самопроверка):**

- Описаны 2–3 сценария для студента и 2–3 для преподавателя без технических деталей реализации.
- Каждый сценарий явно отображён на сущности из `docs/data-model.md` или зафиксированы пробелы.
- `docs/data-model.md` содержит аннотации «нужно для сценария X».

**Пользователь:**

- Прочитать описания сценариев и проверить соответствие ожиданиям продукта.
- Убедиться, что в `docs/data-model.md` нет сущностей без привязки хотя бы к одному сценарию (или явно помечены как «вне текущей фазы»).

### Проверки после блока


| Кто              | Действие                                                                                                             |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Агент**        | Cross-check с `[docs/vision.md](../vision.md)`; нет противоречий ролям и сценариям.                                  |
| **Пользователь** | Ревью `iteration-1-scenarios/plan.md` и diff в `data-model.md`.                                                      |
| **Команды**      | Не обязательны.                                                                                                      |
| **Документация** | `[docs/data-model.md](../data-model.md)`, `[docs/plan.md](../plan.md)` — при необходимости ссылка на новый tasklist. |


---

## Итерация 2: Проектирование схемы данных и ревью

**Цель:** Актуализировать **логическую** и **физическую** модель, нарисовать физическую ER-диаграмму, провести ревью через skill `**postgresql-table-design*`*.

### Состав работ

- В `[docs/data-model.md](../data-model.md)`: добавить сущности **Module** (id, flow_id, title, order), **Lesson** (id, module_id, title, order, scheduled_at).
- Исправить модель **Assignment**: связь с **lesson_id** (не `flow_id`); согласовать с OpenAPI/контрактом сдач при необходимости отдельной задачей в итерации 5.
- Задокументировать **Material** (таблица `materials`), **KnowledgeItem** (таблица `knowledge_items` + pgvector), **Progress** (VIEW `participant_assignment_progress`).
- Добавить **физическую** ER-диаграмму (Mermaid в `data-model.md` и/или файл в `docs/`): таблицы, FK, ключевые индексы, constraints, nullable.
- Ревью по `**postgresql-table-design`**: индексы под типичные запросы (participant_id, flow_id, telegram_id и т.д.), UNIQUE/NOT NULL/CHECK, именование (snake_case), согласованность типов PK.
- Артефакты: `docs/tasks/impl/database/iteration-2-schema/plan.md`, `summary.md`.

### Задачи (кратко)


| Задача | Содержание                                                     |
| ------ | -------------------------------------------------------------- |
| 01     | Обновление логической модели в `docs/data-model.md`            |
| 02     | Физическая ER-диаграмма                                        |
| 03     | Ревью postgresql-table-design, фиксация решений в `summary.md` |


### Definition of Done

**Агент (самопроверка):**

- `docs/data-model.md` содержит Module и Lesson; Assignment ссылается на `lesson_id`.
- Физическая диаграмма отражает таблицы, FK, ключевые индексы и constraints.
- Ревью `postgresql-table-design` проведено; замечания устранены или явно приняты как компромисс.
- Нет расхождений между текстом логической модели и диаграммой.

**Пользователь:**

- Открыть `docs/data-model.md` и пройти диаграмму: все сущности, нужные для итерации 1, присутствуют.
- Убедиться, что в логической модели Assignment больше не опирается на `flow_id`.

### Проверки после блока


| Кто              | Действие                                                                                                 |
| ---------------- | -------------------------------------------------------------------------------------------------------- |
| **Агент**        | При изменении контракта — завести задачу на синхронизацию OpenAPI в итерации 5.                          |
| **Пользователь** | Ревью диаграммы и разделов Material / KnowledgeItem / Progress (VIEW).                                 |
| **Команды**      | Не обязательны.                                                                                          |
| **Документация** | `[docs/data-model.md](../data-model.md)`; при существенных решениях — черновик для ADR-003 в итерации 3. |


---

## Итерация 3: Инструменты миграций и доступа к БД — ADR и практическое руководство

**Цель:** Зафиксировать выбор инструментов (опираясь на уже принятые ADR) и дать **короткую практическую справку**, как ими пользоваться в этом репозитории.

### Состав работ

- Сверка с `[docs/adr/adr-002-backend-http-orm.md](../adr/adr-002-backend-http-orm.md)`: стек (FastAPI, SQLAlchemy 2 async, Alembic) уже выбран; при полном совпадении с практикой — **не дублировать** новым ADR, а сослаться в руководстве.
- Если обнаружено **существенное** расхождение (паттерны миграций, работа с enum, стратегия autogenerate) — оформить `**docs/adr/adr-003-*.md`** и обновить `[docs/adr/README.md](../adr/README.md)`.
- Создать `**docs/tech/sqlalchemy-alembic-guide.md**`: async-сессии и DI в FastAPI (`AsyncSession`), цикл Alembic (`revision`, `upgrade head`, `downgrade`), именование ревизий (как в проекте), seed через скрипт, enum в PostgreSQL (`CREATE TYPE`, `native_enum`).
- Артефакты: `docs/tasks/impl/database/iteration-3-tooling-guide/plan.md`, `summary.md`.

### Задачи (кратко)


| Задача | Содержание                                           |
| ------ | ---------------------------------------------------- |
| 01     | Сверка с ADR-002; при необходимости ADR-003 + README |
| 02     | Написание `docs/tech/sqlalchemy-alembic-guide.md`    |
| 03     | `summary.md` итерации                                |


### Definition of Done

**Агент (самопроверка):**

- `docs/tech/sqlalchemy-alembic-guide.md` создан и покрывает: async-сессии, цикл миграции, именование версий, enum, паттерн seed.
- Содержимое соответствует фактическому коду в `backend/` (нет устаревших путей и команд).
- Если создан ADR-003 — есть запись в `docs/adr/README.md`.

**Пользователь:**

- Открыть `docs/tech/sqlalchemy-alembic-guide.md` и найти ответ на «как создать и применить новую миграцию в этом проекте».
- Сверить раздел async-сессий с `backend/database.py` и `backend/api/deps.py`.

### Проверки после блока


| Кто              | Действие                                                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Агент**        | Ссылка на руководство из `[README.md](../../README.md)` при появлении раздела про БД.                                                          |
| **Пользователь** | Быстрая вычитка гайда.                                                                                                                         |
| **Команды**      | При необходимости уточнить в гайде существующие `make migrate-upgrade`.                                                                        |
| **Документация** | `docs/tech/sqlalchemy-alembic-guide.md`, `docs/adr/*`, `[docs/integrations.md](../integrations.md)` — только если меняется способ подключения. |


---

## Итерация 4: Инфраструктура БД, миграции, seed и проверка

**Цель:** Воспроизводимо поднимать PostgreSQL, накатывать миграции, **пересоздавать** окружение, смотреть данные, наполнять БД из `**data/progress-import.v1.json`** (выгрузка реального прогресса, минимальный осмысленный набор в репозитории).

### Состав работ

- `**docker-compose.yml**`: сервис `db` (например `postgres:16`), volume, `healthcheck`.
- **Makefile**: `db-up`, `db-down`, `db-reset` (остановка + удаление volume + `db-up` + `migrate-upgrade`), `db-shell`, `db-logs`, `db-status` (например `alembic current`), `**db-seed`**.
- `**[.env.example](../../.env.example)**`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, согласование с `DATABASE_URL` для локального compose.
- `**data/progress-import.v1.json**`: задокументировать формат (в файле или в `docs/`); содержимое — минимум: **1 поток, 2 модуля, 3 занятия, 5 заданий, 2 студента** с разным прогрессом сдач; по [`data-model.md`](../data-model.md) при необходимости — **материалы** (`materials`) и/или заготовка под **knowledge_items** (опционально для MVP). После итерации 5 — согласовать с фактической схемой; до migration003 — под текущую схему или с пометкой «обновить после migration003» в `plan.md`.
- `**scripts/seed_data.py`**: импорт через SQLAlchemy/async — согласовать с гайдом итерации 3.
- `**scripts/db_inspect.py**`: сводка `COUNT(*)` по таблицам (или эквивалент).
- Обновить `**[README.md](../../README.md)**`: порядок «с нуля»: `db-up` → `migrate-upgrade` → `db-seed` → проверка.

### Задачи (кратко)


| Задача | Содержание                                              |
| ------ | ------------------------------------------------------- |
| 01     | docker-compose + переменные окружения                   |
| 02     | Цели Makefile `db-*`                                    |
| 03     | `data/progress-import.v1.json` + `scripts/seed_data.py` |
| 04     | `scripts/db_inspect.py`, README                         |


### Definition of Done

**Агент (самопроверка):**

- `make db-up` поднимает PostgreSQL; `make db-down` останавливает; `make db-reset` пересоздаёт данные с нуля и накатывает миграции.
- `make migrate-upgrade` на чистой БД проходит без ошибок.
- `make db-seed` завершается успешно; `db_inspect` показывает ненулевые счётчики там, где ожидается.
- `data/progress-import.v1.json` соответствует заявленному минимуму (после появления Module/Lesson в БД — структура обновлена).
- `.env.example` содержит все новые переменные с комментариями.

**Пользователь:**

- Выполнить на чистой машине: `make db-reset` (или `db-up` + `migrate-upgrade`) без ошибок.
- `make db-seed` → `make db-shell` → проверить, что в ключевых таблицах есть строки (например `participants`).
- Запустить `python scripts/db_inspect.py` — увидеть сводку в терминале.

### Проверки после блока


| Кто              | Действие                                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| **Агент**        | Windows: проверить совместимость команд в `Makefile` (как в существующем `ifeq ($(OS),Windows_NT)`). |
| **Пользователь** | Пройти раздел README про БД.                                                                         |
| **Команды**      | **Актуализировать `[Makefile](../../Makefile)`** — все новые цели задокументированы в README.        |
| **Документация** | `[README.md](../../README.md)`, `[.env.example](../../.env.example)`.                                |


---

## Итерация 5: ORM-модели, слой доступа к данным и интеграция в backend

**Цель:** Довести проект до **персистентности по согласованной схеме** в [`docs/data-model.md`](../data-model.md): Module, Lesson, Material, KnowledgeItem (при включении RAG), Assignment.lesson_id, VIEW `participant_assignment_progress`, правки `users.email`; минимальный **read-API** для фронта и **проверяемый** сценарий «данные после перезапуска — из БД».

### Состав работ

- **Модели:** `backend/models/module.py`, `backend/models/lesson.py`, `backend/models/material.py`, `backend/models/knowledge_item.py`; обновить `backend/models/assignment.py` (`lesson_id`, убрать `flow_id`); `backend/models/user.py` (nullable `email`, убрать `default=""`, частичные уникальные индексы в миграции); `backend/models/__init__.py`; обновить связи в `Flow` и др.
- **Миграция Alembic `003_*` (и при необходимости `004_*`):** CREATE `modules`, `lessons`, `materials`, `knowledge_items`; `CREATE EXTENSION IF NOT EXISTS vector` (если включаем RAG в БД); VIEW `participant_assignment_progress`; ALTER `users` (email); ALTER `assignments`; перенос/миграция данных при необходимости (или допустимый сброс dev-данных — зафиксировать в `plan.md`). Разбиение на две ревизии допустимо (например сначала структура потока, затем pgvector).
- **Сервисы:** `backend/services/modules.py`, `backend/services/lessons.py`; обновить `backend/services/submissions.py` и эндпоинты сдач под принадлежность задания потоку через `Lesson → Module → Flow`.
- **API (read, Bearer как в контракте):** например `GET /v1/flows/{flow_id}/modules` (модули с занятиями), `GET /v1/participants/{participant_id}/submissions` (прогресс); обновить `[docs/api/backend-v1.openapi.yaml](../api/backend-v1.openapi.yaml)`.
- **Тесты:** интеграционный тест цепочки поток → модуль → занятие → задание → `POST /v1/submissions` → проверка статуса/чтения.
- **Smoke:** обновить `make smoke-dialog` или добавить `make smoke-full` (по согласованию в `plan.md`).
- Артефакты: `docs/tasks/impl/database/iteration-5-backend-integration/plan.md`, `summary.md`.

### Задачи (кратко)


| Задача | Содержание                                            |
| ------ | ----------------------------------------------------- |
| 01     | ORM Module/Lesson/Material/KnowledgeItem, User.email, Assignment |
| 02     | Миграции 003 (+ при необходимости 004: vector, VIEW)   |
| 03     | Сервисы и правки submissions/dialog при необходимости |
| 04     | Read endpoints + OpenAPI                              |
| 05     | Тесты, smoke, `summary.md`                            |


### Definition of Done

**Агент (самопроверка):**

- Миграции `003` (и при наличии `004`) накатываются и откатываются без ошибок (если downgrade поддерживается политикой проекта).
- `make lint-backend` и `make test-backend` проходят.
- Новый интеграционный тест покрывает цепочку до сдачи и чтения прогресса.
- После `db-seed` read-endpoint'ы отдают структуру, согласованную с данными.
- `docs/api/backend-v1.openapi.yaml` синхронизирован с реализацией.

**Пользователь:**

- `make db-reset && make migrate-upgrade && make db-seed` — без ошибок.
- `make test-backend` — зелёный.
- `GET /v1/flows/{flow_id}/modules` (curl/Swagger) — видна структура из seed.
- `POST /v1/submissions` затем `GET /v1/participants/{id}/submissions` — статус `submitted` отображается.

### Проверки после блока


| Кто              | Действие                                                                                                                                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Агент**        | Убедиться, что бот и контракт сдач согласованы с `lesson_id`; обновить `[docs/integrations.md](../integrations.md)` при смене правил.                                                                                   |
| **Пользователь** | Сквозной сценарий локально: БД + backend + при необходимости бот.                                                                                                                                                       |
| **Команды**      | **Makefile:** `smoke-full` или обновлённый smoke; цели из итерации 4 актуальны.                                                                                                                                         |
| **Документация** | `[docs/data-model.md](../data-model.md)` (итог), `[docs/api/backend-v1.openapi.yaml](../api/backend-v1.openapi.yaml)`, `[docs/plan.md](../plan.md)` — статусы этапов при необходимости, `[README.md](../../README.md)`. |


---

## Связь с другими tasklist

- `**[tasklist-backend.md](tasklist-backend.md)`** — уже закрытые итерации каркаса и MVP API; эта работа **углубляет слой данных** и структуру потока, не отменяя контракты v1 без явного решения.
- После итерации 5 имеет смысл обновить строку в `[docs/plan.md](../plan.md)` (например, отметить прогресс по «ядру и данным» / структуре потока) и при необходимости добавить ссылку на этот tasklist в обзор дорожной карты.

---

## Карта актуализации документации


| Файл                                                                           | Итерации                                  |
| ------------------------------------------------------------------------------ | ----------------------------------------- |
| `[docs/data-model.md](../data-model.md)`                                       | 1, 2, 5                                   |
| `[docs/spec/user-scenarios.md](../spec/user-scenarios.md)`                     | 1, 2                                      |
| `[docs/tech/sqlalchemy-alembic-guide.md](../tech/sqlalchemy-alembic-guide.md)` | 3                                         |
| `[docs/api/backend-v1.openapi.yaml](../api/backend-v1.openapi.yaml)`           | 5                                         |
| `[docs/adr/README.md](../adr/README.md)`, `[docs/adr/adr-003-enum-strategy.md](../adr/adr-003-enum-strategy.md)` | 3 |
| `[.env.example](../../.env.example)`                                           | 4                                         |
| `[README.md](../../README.md)`                                                 | 4, 5                                      |
| `[Makefile](../../Makefile)`                                                   | 4, 5                                      |
| `[docs/plan.md](../plan.md)`                                                   | 5 (статусы / ссылки)                      |
| `[docs/integrations.md](../integrations.md)`                                   | 5 (при изменении контракта/идентификации) |


