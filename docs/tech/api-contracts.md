# HTTP API backend (v1)

Краткий обзор контракта для разработчиков бота, веб-клиента и интеграций. **Источник правды по полям, схемам и кодам ответов** — OpenAPI в репозитории: [`docs/api/backend-v1.openapi.yaml`](../api/backend-v1.openapi.yaml).

## Роль API в продукте

По [`docs/vision.md`](../vision.md) ядро системы — backend: потоки, прогресс, диалог с ассистентом, роли. Telegram-бот и веб-приложение — клиенты одного REST API с префиксом `/v1/`. Диалоги и сдачи сохраняются в БД; генерация ответов ассистента идёт через backend к внешнему LLM ([`docs/integrations.md`](../integrations.md) — OpenRouter, OpenAI-compatible).

## Аутентификация

| Механизм | Когда | Подробнее |
|----------|--------|-----------|
| `Authorization: Bearer <INTERNAL_API_TOKEN>` | Вызовы от **бота** (и прочие серверные клиенты с общим секретом из `.env`) | [`docs/integrations.md`](../integrations.md): `INTERNAL_API_TOKEN`, `BACKEND_BASE_URL` |
| `POST /v1/auth/web-session` **без** Bearer | Вход **веб-клиента**: тело `telegram_username` + `flow_id` → JWT | Резолв пользователя по username (без `@`, регистр не важен) и участия в потоке |
| `Authorization: Bearer <JWT>` | Защищённые **веб**-маршруты (дашборд, ленты, матрица, лидерборд, диалог по `participant_id`) | В JWT зашиты `user_id`, `participant_id`, `flow_id`, роль `student` \| `teacher`; `flow_id` в пути должен совпадать с токеном |

Браузерные запросы к API с другого origin (например Next.js на порту 3000) требуют **CORS** на backend: переменная **`CORS_ORIGINS`** (через запятую) или значения по умолчанию `http://127.0.0.1:3000`, `http://localhost:3000` в [`backend/config.py`](../../backend/config.py).

На веб-маршрутах с проверкой JWT **нельзя** подставить тот же Bearer, что у бота (`INTERNAL_API_TOKEN`): сервер отвечает `403` — иначе общий секрет был бы полноценной сессией пользователя.

Подробности схемы `bearerAuth` в OpenAPI: [`components.securitySchemes.bearerAuth`](../api/backend-v1.openapi.yaml).

## Идентификация субъекта

- **Бот:** в теле запросов к диалогу и сдачам — `telegram_user_id` (целое) и `flow_id` (UUID); backend находит `User` и `Participant` (см. также [`docs/data-model.md`](../data-model.md)).
- **Веб после логина:** запросы завязаны на JWT; для диалога по пути `/v1/participants/{participant_id}/dialog-messages` обязательны согласованные `participant_id`, `flow_id` (query) и права участника из токена.

## Каталог методов (обзор)

| Метод и путь | Назначение | Типичный клиент | Auth |
|--------------|------------|-----------------|------|
| `POST /v1/dialog-messages` | Сообщение в диалог + ответ LLM, резолв по `telegram_user_id` | Бот | Bearer (internal) |
| `POST /v1/voice/dialog-messages` | Голос: multipart `audio` + `flow_id` (+ `telegram_user_id` только internal), ответ включает `transcription` | Бот / веб | Bearer (internal или JWT) |
| `POST /v1/submissions` | Создать сдачу (`submitted`) | Бот | Bearer (internal) |
| `GET /v1/flows/{flow_id}/modules` | Дерево модулей и занятий | Бот / веб | Bearer |
| `GET /v1/participants/{participant_id}/submissions` | Сдачи участника (новые первыми) | Веб / бот | Bearer (internal; в контракте единая схема) |
| `POST /v1/auth/web-session` | Выдача JWT веб-сессии | Веб | Нет |
| `GET /v1/flows/{flow_id}/dashboard` | KPI и активность 14 дней | Веб (teacher) | JWT |
| `GET /v1/flows/{flow_id}/questions` | Лента вопросов к ассистенту, курсор | Веб (teacher) | JWT |
| `GET /v1/flows/{flow_id}/submissions` | Лента сдач по потоку (не путать с `POST /v1/submissions`) | Веб (teacher) | JWT |
| `GET /v1/flows/{flow_id}/progress-matrix` | Матрица прогресса по урокам | Веб (teacher) | JWT |
| `GET /v1/flows/{flow_id}/leaderboard` | Лидерборд | Веб (member: student или teacher) | JWT |
| `GET/POST .../participants/{participant_id}/dialog-messages` | История и новое сообщение диалога в вебе | Веб | JWT |
| `POST /v1/flows/{flow_id}/data-query` | Вопрос преподавателя к агрегированным данным потока (LLM → intent, allowlist SQL) | Веб (teacher) | JWT |

**Важно:** `POST /v1/submissions` (создание одной сдачи) и `GET /v1/flows/{flow_id}/submissions` (лента по потоку) — разные ресурсы и сценарии; это зафиксировано в описании OpenAPI [`info.description`](../api/backend-v1.openapi.yaml).

## `POST /v1/flows/{flow_id}/data-query`

- **Auth:** JWT веб-сессии, роль **`teacher`**, `flow_id` в пути совпадает с токеном.
- **Тело:** `{ "question": "<строка 1..2000>" }` — свободная формулировка; **текст вопроса не пишется в логи** (только `correlation_id` и выбранный `intent`).
- **Ответ 200:** `intent`, `params` (параметры после классификации), `result` (массив объектов-строк, не более 100), `explanation` (краткий человекочитаемый итог), `correlation_id` (UUID).
- **Ошибки:** `401` / `403` как у других веб-маршрутов потока; `404` если поток не найден; `400` с `error.code: unrecognized_intent` если классификатор вернул `unknown` или неподдерживаемый intent / невалидный JSON от LLM; `422` при ошибке валидации тела; `500` при сбое LLM или БД.

Архитектура и whitelist intent: [`docs/adr/adr-005-text-to-sql.md`](../adr/adr-005-text-to-sql.md). Канонические схемы — в OpenAPI (`DataQueryRequest`, `DataQueryResponse`).

## Демо-данные (локально)

После `make migrate-upgrade`: `make db-seed` или `make db-seed-frontend-demo` — файл [`data/progress-import.v1.json`](../../data/progress-import.v1.json). Фиксированный демо-поток `00000000-0000-0000-0000-000000000001`; преподаватель для веб-входа — `telegram_id=459032551`, `telegram_username` в seed — `bondarenko_alexey_nikolaevich` (Telegram handle @Bondarenko_Alexey_Nikolaevich). Демо-студенты (фамилии в `name`, `telegram_username` без `@`): `ivanov_ivan`, `petrov_petr`, `sidorov_sergey`, `vaseckin_viktor`, `kozlov_konstantin` — `telegram_id` 401001–401005 для проверки бота и веб-входа.

## Пагинация и заголовки

- Ленты вопросов и сдач по потоку: query `limit`, `cursor`; в ответе — `next_cursor` (контракт страницы в YAML).
- Успешные `POST` диалога возвращают `201` и заголовок `Location` на коллекцию сообщений (см. операции в YAML).

## Ошибки и коды

Стандартное тело ошибки — `ErrorBody`: `error.code` (стабильный идентификатор для клиента), `error.message`, опционально `error.details` для валидации. Перечень ответов по операциям — в OpenAPI.

Политика **403 vs 404**: для части защищённых ресурсов по UUID допустим ответ `403` вместо `404`, чтобы не раскрывать существование объекта — детали в [`info.description`](../api/backend-v1.openapi.yaml).

## Документация в runtime

При запущенном сервисе доступны `GET /openapi.json`, `GET /docs`, `GET /redoc` (см. [`docs/integrations.md`](../integrations.md)). При расхождении с YAML репозитория для ревью контракта ориентир — файл `docs/api/backend-v1.openapi.yaml`.

## Переменные окружения (связанные с API)

Имена и смысл — в [`.env.example`](../../.env.example) и [`docs/integrations.md`](../integrations.md): в том числе `INTERNAL_API_TOKEN`, URL backend, секреты JWT (`JWT_SECRET`, срок жизни токена) для веб-сессии, **`OPENAI_API_KEY`** для `POST /v1/voice/dialog-messages` (Whisper).

## Будущее: OAuth

Вход через Google/GitHub для веб-приложения описан в [`docs/integrations.md`](../integrations.md) как **Future**; текущий MVP веб-входа в контракте — `POST /v1/auth/web-session` без OAuth-провайдера.
