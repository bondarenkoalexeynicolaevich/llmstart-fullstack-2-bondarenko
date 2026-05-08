# Frontend — Tasklist

## Обзор

Итерации веб-клиента: спецификация UI и HTTP-контрактов, API под экраны в backend, каркас Next.js (App Router) + shadcn/ui + Tailwind + pnpm, реализация дашборда преподавателя, лидерборда, чата (плавающий и полноэкранный), последующие усиления (качество кода, голос, ответы по данным БД).

Согласуется с `[docs/vision.md](../vision.md)`, `[docs/data-model.md](../data-model.md)`, `[docs/integrations.md](../integrations.md)`, `[docs/plan.md](../plan.md)`, шаблоном процесса `[docs/templates/workflow.md](../templates/workflow.md)`.

**Стек:** Next.js (App Router) + React, TypeScript, shadcn/ui, Tailwind CSS, **pnpm**.

**Skills (рекомендации по шагам):** `/find-skills` в Cursor; в итерациях 2–3 и 7 — `shadcn`, `vercel-react-best-practices`, `nextjs-app-router-patterns`; в итерации 1 — `api-design-principles`.

## Легенда статусов


| Символ | Статус                 |
| ------ | ---------------------- |
| 📋     | Planned — запланирован |
| 🚧     | In Progress — в работе |
| ✅      | Done — завершён        |


## Сводная таблица итераций


| №   | Итерация                                        | Статус | Артефакты планирования                                                         |
| --- | ----------------------------------------------- | ------ | ------------------------------------------------------------------------------ |
| 0   | Требования к UI и API-контракты                 | ✅      | `docs/tasks/impl/frontend/iteration-0-ui-api-contracts/plan.md`, `summary.md`  |
| 1   | Backend API для frontend                        | ✅      | `docs/tasks/impl/frontend/iteration-1-backend-api/plan.md`, `summary.md`       |
| 2   | Каркас frontend-проекта                         | ✅      | `docs/tasks/impl/frontend/iteration-2-skeleton/plan.md`, `summary.md`          |
| 3   | Панель преподавателя                            | ✅      | `docs/tasks/impl/frontend/iteration-3-teacher-dashboard/plan.md`, `summary.md` |
| 4   | Лидерборд                                       | ✅      | `docs/tasks/impl/frontend/iteration-4-leaderboard/plan.md`, `summary.md`       |
| 5   | Чат с ассистентом (виджет/полноэкранный контур) | ✅      | `docs/tasks/impl/frontend/iteration-5-assistant-chat/plan.md`, `summary.md`    |
| 6   | Чат в основной области («Чат»)                  | ✅      | `docs/tasks/impl/frontend/iteration-6-main-chat-page/plan.md`, `summary.md`    |
| 7   | Ревью качества frontend                         | ✅      | `docs/tasks/impl/frontend/iteration-7-code-review/summary.md`                  |
| 8   | Голосовой режим чата                            | ✅      | `docs/tasks/impl/frontend/iteration-8-voice-chat/plan.md`, `summary.md`        |
| 9   | Ответы по данным БД (Text-to-SQL)               | ✅      | `docs/tasks/impl/frontend/iteration-9-text-to-sql/plan.md`, `summary.md`       |


*Пути `docs/tasks/impl/frontend/...` — по `[docs/templates/workflow.md](../templates/workflow.md)`; при старте итерации создать каталоги и `plan.md` / `summary.md`.*

---

## Итерация 0: Требования к UI и API-контракты

**Цель:** Зафиксировать функциональные требования к четырём зонам интерфейса, общий визуальный стиль, модель «входа» без сложной авторизации и проект HTTP API, достаточного для отрисовки экранов.

**План итерации:** `[docs/tasks/impl/frontend/iteration-0-ui-api-contracts/plan.md](impl/frontend/iteration-0-ui-api-contracts/plan.md)`


| Задача               | `plan.md`                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Панель преподавателя | [task-01-teacher-dashboard-spec](impl/frontend/iteration-0-ui-api-contracts/tasks/task-01-teacher-dashboard-spec/plan.md) |
| Лидерборд            | [task-02-leaderboard-spec](impl/frontend/iteration-0-ui-api-contracts/tasks/task-02-leaderboard-spec/plan.md)             |
| Чат                  | [task-03-chat-spec](impl/frontend/iteration-0-ui-api-contracts/tasks/task-03-chat-spec/plan.md)                           |
| Стиль и вход         | [task-04-style-and-login](impl/frontend/iteration-0-ui-api-contracts/tasks/task-04-style-and-login/plan.md)               |
| API и OpenAPI        | [task-05-api-contracts](impl/frontend/iteration-0-ui-api-contracts/tasks/task-05-api-contracts/plan.md)                   |


### Состав работ

- **Экран 1 — панель преподавателя:** 4 KPI с дельтой к прошлому периоду; линейный график активности по дням (14 дней); лента вопросов (кто, когда, текст вопроса + ответ/резюме ответа); лента сдач (кликабельно — отчёт/детали и ссылки на материалы при наличии); матрица прогресса (строки — студенты, колонки — уроки; при наведении — дата/статус).
- **Экран 2 — лидерборд:** переключатель «Таблица / карта» (scatter plot); в таблице — место, общий прогресс (progress bar), иконки по урокам, топ-3 с медалями.
- **Глобальный чат с ассистентом:** плавающая кнопка/панель на всех экранах (краткая переписка или раскрытие — зафиксировать в макете/требованиях).
- **Стиль:** тёмная тема, «dev» эстетика (ориентир: [tbench.ai](https://www.tbench.ai/)); типографика, сетка, акценты — кратко в требованиях.
- **Вход:** без OAuth на этом этапе — ввод Telegram username (и при необходимости привязка к текущему потоку — явно описать в сценарии).
- **API:** спроектировать контракты для всех экранов (пути, query, тела, форматы дат, пагинация лент, агрегации KPI и графика, данные для scatter — поля осей и подписей).
- Актуализировать документацию: черновик/раздел в `[docs/vision.md](../vision.md)` (таблица Web при необходимости), `[README.md](../../README.md)` (если меняется описание клиентов), ссылка из `[docs/plan.md](../plan.md)` на `tasklist-frontend.md` при расхождении с `tasklist-web.md`.

### Definition of Done

**Агент (самопроверка):**

- В `plan.md` итерации перечислены зоны UI, поля виджетов и ожидаемые состояния (loading/empty/error).
- Описаны JSON-схемы ответов для каждого экрана (или ссылка на черновик в репозитории).
- Нет противоречий с `[docs/data-model.md](../data-model.md)` для базовых сущностей (User, Participant, Lesson, Submission, DialogMessage и т.д.).
- Созданы папки задач с `plan.md` по workflow; статусы в таблице tasklist при необходимости обновлены после завершения.

**Пользователь:**

- Открыть `docs/tasks/impl/frontend/iteration-0-ui-api-contracts/plan.md` — понятно, что строим и какие данные нужны.
- Сверить визуальные ожидания (тема, четыре зоны) с описанием в плане.

### Проверки после блока


| Кто           | Что сделать                                                                                          |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| **Агент**     | Убедиться, что итерация 1 может начаться без «договаривания в чате» — контракты достаточно детальны. |
| **Команды**   | Не требуются (только документация).                                                                  |
| **Результат** | Единая спецификация UI + API для frontend/backend.                                                   |


---

## Итерация 1: Реализация API для frontend

**Цель:** Обеспечить backend данными и endpoint’ами для всех экранов итераций 3–6; при необходимости доработать схему БД и сиды; задокументировать контракты.

**План итерации:** `[docs/tasks/impl/frontend/iteration-1-backend-api/plan.md](impl/frontend/iteration-1-backend-api/plan.md)`

**Канонический контракт:** `[docs/api/backend-v1.openapi.yaml](../api/backend-v1.openapi.yaml)` (поведение и схемы не ломать без версии или осознанной миграции клиента).


| Задача                           | `plan.md`                                                                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Gap-анализ БД vs контракт        | [task-01-data-gap-analysis](impl/frontend/iteration-1-backend-api/tasks/task-01-data-gap-analysis/plan.md)                   |
| Dashboard, ленты, матрица        | [task-02-dashboard-feed-matrix-api](impl/frontend/iteration-1-backend-api/tasks/task-02-dashboard-feed-matrix-api/plan.md)   |
| Лидерборд и веб-диалог           | [task-03-leaderboard-and-dialog-api](impl/frontend/iteration-1-backend-api/tasks/task-03-leaderboard-and-dialog-api/plan.md) |
| Миграции и seed (demo-data)      | [task-04-migrations-and-seed](impl/frontend/iteration-1-backend-api/tasks/task-04-migrations-and-seed/plan.md)               |
| Тесты и синхронизация документов | [task-05-tests-and-contract-docs](impl/frontend/iteration-1-backend-api/tasks/task-05-tests-and-contract-docs/plan.md)       |


### Состав работ

- Сопоставить требования итерации 0 с `[docs/data-model.md](../data-model.md)`: зафиксировать пробелы (новые поля, представления, индексы).
- Реализовать новые маршруты в `backend/api/` + сервисы в `backend/services/` (KISS): дашборд преподавателя (KPI, series за 14 дней, вопросы, сдачи, матрица), лидерборд (таблица + данные для scatter), история чата для веб-клиента (согласовать с существующим диалоговым API при наличии).
- Alembic: миграции под изменения схемы; отдельная миграция/сиды с **mock-данными** для «красивого» UI (реалистичные объёмы, статусы, даты).
- Добавить преподавателя в БД: пользователь с **telegram_id = 459032551** (упоминание `@Bondarenko_Alexey_Nikolaevich` — в комментарии к миграции или в seed-скрипте, без секретов).
- Прогнать ревью контрактов по skill `**api-design-principles`** (именование ресурсов, коды ошибок, консистентность).
- Обновить `[docs/tech/api-contracts.md](../tech/api-contracts.md)` (создать при отсутствии): полное описание новых/изменённых endpoint’ов; при необходимости — `[docs/integrations.md](../integrations.md)` (как веб вызывает API, заголовки).
- Доработать тесты `backend/tests/` на новые сценарии; `make lint-backend`, `make test-backend`.

### Definition of Done

**Агент (самопроверка):**

- Все маршруты из `[docs/api/backend-v1.openapi.yaml](../api/backend-v1.openapi.yaml)`, необходимые для экранов итераций 3–6 (`web-session`, `dashboard`, вопросы/сдачи по потоку, матрица, лидерборд, `participants/.../dialog-messages`), реализованы в коде или **явно отложены** с обоснованием в `[docs/tasks/impl/frontend/iteration-1-backend-api/summary.md](impl/frontend/iteration-1-backend-api/summary.md)` после закрытия итерации.
- По каждой задаче есть `plan.md` до начала работ и `summary.md` после — см. каталог `[iteration-1-backend-api/](impl/frontend/iteration-1-backend-api/)`.
- Миграции применяются на чистой БД; seed/mock даёт данные для UI.
- Преподаватель с `telegram_id = 459032551` создаётся миграцией или idempotent seed.
- `[docs/tech/api-contracts.md](../tech/api-contracts.md)` синхронна с кодом; замечания из `api-design-principles` учтены или зафиксированы как исключения.

**Пользователь:**

- `make db-up && make migrate-upgrade` (и при необходимости seed из итерации) — затем `make run-backend`.
- Проверить OpenAPI/Swagger backend (если включён) или примеры из `docs/tech/api-contracts.md` через curl/HTTP-клиент.

### Проверки после блока


| Кто           | Что сделать                                                                                                                         |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Агент**     | `make lint-backend` и `make test-backend` проходят.                                                                                 |
| **Makefile**  | Цель `**make db-seed-frontend-demo`** добавлена (алиас `**make db-seed**`); при расширении отдельного демо-скрипта — обновить цель. |
| **Результат** | Frontend может перейти от моков к реальному API без переделки контракта.                                                            |


---

## Итерация 2: Каркас frontend-проекта

**Цель:** Поднять проект в `web/` (или согласованное имя каталога), базовую тему, навигацию, «вход» по Telegram username, плавающий чат-виджет-заготовку и команды запуска.

### Состав работ

- Инициализация: **pnpm**, Next.js **App Router**, TypeScript, Tailwind, **shadcn/ui** (skills: `shadcn`, `vercel-react-best-practices`, `nextjs-app-router-patterns`).
- Тема: тёмная палитра в духе dev-dashboard; токены в Tailwind/shadcn theme.
- **Вход:** форма ввода Telegram username; отображение текущего «пользователя сессии» и кнопка выхода (локальное состояние / cookie / storage — зафиксировать в `plan.md`, KISS).
- **Layout:** навигация между экранами (преподаватель, лидерборд, чат); placeholder для данных.
- **Глобальный чат:** плавающая кнопка на всех страницах, маршрут или drawer — согласно итерации 0.
- Env: базовый URL backend (`NEXT_PUBLIC_…`), пример в `web/.env.example`; обновить корневой `[.env.example](../../.env.example)` при необходимости.
- **Makefile:** цели `web-install`, `web-dev`, `web-build`, `web-lint` (или эквивалент через `pnpm`).
- Документация: `[README.md](../../README.md)` — как установить pnpm deps и запустить web рядом с backend.

### Definition of Done

**Агент (самопроверка):**

- `pnpm install` и dev-сервер запускаются без ошибок; production `build` проходит.
- Линт/проверки типов (если настроены) проходят; shadcn-компоненты подключены минимально необходимым набором.
- Навигация и плавающий чат видны на всех основных страницах-заглушках.

**Пользователь:**

- `make web-install && make web-dev` (или `pnpm dev` из `web/`).
- Пройти по пунктам меню; ввести username, убедиться что блок «пользователь» и «выход» работают.

### Проверки после блока


| Кто           | Что сделать                                                                                         |
| ------------- | --------------------------------------------------------------------------------------------------- |
| **Агент**     | При необходимости обновить `[docs/vision.md](../vision.md)` (секция Web — стек и структура `web/`). |
| **Makefile**  | Цели для web добавлены и задокументированы в README.                                                |
| **Результат** | Готов каркас для наполнения экранами 3–6.                                                           |


---

## Итерация 3: Панель преподавателя

**Цель:** Страница дашборда с KPI, графиком, таблицей вопросов, лентой сдач и матрицей прогресса по данным API итерации 1.

**План итерации:** `[docs/tasks/impl/frontend/iteration-3-teacher-dashboard/plan.md](impl/frontend/iteration-3-teacher-dashboard/plan.md)`


| Задача              | `plan.md`                                                                                                                                          |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Маршрут и API-слой  | [task-01-dashboard-route-and-data-contracts](impl/frontend/iteration-3-teacher-dashboard/tasks/task-01-dashboard-route-and-data-contracts/plan.md) |
| KPI и график        | [task-02-kpi-and-activity-chart](impl/frontend/iteration-3-teacher-dashboard/tasks/task-02-kpi-and-activity-chart/plan.md)                         |
| Лента вопросов      | [task-03-questions-feed](impl/frontend/iteration-3-teacher-dashboard/tasks/task-03-questions-feed/plan.md)                                         |
| Лента сдач и детали | [task-04-submissions-feed-and-details](impl/frontend/iteration-3-teacher-dashboard/tasks/task-04-submissions-feed-and-details/plan.md)             |
| Матрица прогресса   | [task-05-progress-matrix-and-states](impl/frontend/iteration-3-teacher-dashboard/tasks/task-05-progress-matrix-and-states/plan.md)                 |
| Smoke и приёмка     | [task-06-smoke-docs-and-acceptance](impl/frontend/iteration-3-teacher-dashboard/tasks/task-06-smoke-docs-and-acceptance/plan.md)                   |


### Состав работ

- Страница маршрута `**/dashboard`** — см. `[iteration-3/plan.md](impl/frontend/iteration-3-teacher-dashboard/plan.md)` (группа `web/app/(app)/`).
- 4 KPI-карточки с дельтой; loading/skeleton.
- Линейный график активности (14 дней) — библиотека минимально достаточная (recharts/chart.js — решение в плане).
- Таблица вопросов с колонками из спеки; пагинация или «load more».
- Лента сдач с кликом по строке (модалка или боковая панель: детали, ссылки).
- Матрица прогресса: tooltip с датой/статусом; адаптив или горизонтальный скролл.
- Клиент API: типизированный `fetch` без React Query (см. план итерации).
- Документация: при отклонениях от контракта — правка `[docs/tech/api-contracts.md](../tech/api-contracts.md)`.

### Definition of Done

**Агент (самопроверка):**

- Все блоки из спеки отображают реальные данные с backend (или согласованный mock только на время — тогда явно в `summary.md`).
- Ошибки сети и пустые состояния обработаны не ломая layout.

**Пользователь:**

- Запустить backend с сидами, затем `make web-dev`; открыть панель преподавателя и проверить KPI, график, таблицы, клики по сдачам и матрицу.

### Проверки после блока


| Кто           | Что сделать                                                                           |
| ------------- | ------------------------------------------------------------------------------------- |
| **Агент**     | Пройтись по skill `vercel-react-best-practices` для критичных клиентских компонентов. |
| **Результат** | Преподаватель видит сводку потока в вебе.                                             |


---

## Итерация 4: Лидерборд

**Цель:** Страница рейтинга с переключателем «Таблица / карта» и визуализацией топ-3.

**План итерации:** `[docs/tasks/impl/frontend/iteration-4-leaderboard/plan.md](impl/frontend/iteration-4-leaderboard/plan.md)`


| Задача           | `plan.md`                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Типы и API       | [task-01-types-api](impl/frontend/iteration-4-leaderboard/tasks/task-01-types-api/plan.md)       |
| Таблица          | [task-02-table-view](impl/frontend/iteration-4-leaderboard/tasks/task-02-table-view/plan.md)     |
| Scatter          | [task-03-scatter-view](impl/frontend/iteration-4-leaderboard/tasks/task-03-scatter-view/plan.md) |
| Страница и smoke | [task-04-page-smoke](impl/frontend/iteration-4-leaderboard/tasks/task-04-page-smoke/plan.md)     |


### Состав работ

- Таблица: место, progress bar, иконки по урокам, медали для топ-3.
- Режим scatter plot: оси и легенда из контракта; доступность и перформанс на N студентах.
- Переключатель таб/карта (shadcn Tabs или аналог).
- Интеграция с API лидерборда; пустые/loading состояния.

### Definition of Done

**Агент (самопроверка):**

- Оба режима используют один и тот же источник данных без дублирования бизнес-логики.
- Топ-3 выделен согласно требованиям итерации 0.

**Пользователь:**

- Открыть лидерборд, переключить режимы, проверить несколько студентов и подписи осей на карте.

### Проверки после блока


| Кто           | Что сделать                                                |
| ------------- | ---------------------------------------------------------- |
| **Результат** | Студенты/преподаватель могут сравнивать прогресс наглядно. |


---

## Итерация 5: Чат с ассистентом (контур виджета)

**Цель:** Рабочий чат с ассистентом в контексте плавающего виджета: история, отправка сообщений, связь с backend.

**План итерации:** `[docs/tasks/impl/frontend/iteration-5-assistant-chat/plan.md](impl/frontend/iteration-5-assistant-chat/plan.md)`


| Задача               | `plan.md`                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------- |
| Типы и API           | [task-01-types-and-api](impl/frontend/iteration-5-assistant-chat/tasks/task-01-types-and-api/plan.md)           |
| ChatPanel            | [task-02-chat-panel](impl/frontend/iteration-5-assistant-chat/tasks/task-02-chat-panel/plan.md)                 |
| Виджет               | [task-03-widget-integration](impl/frontend/iteration-5-assistant-chat/tasks/task-03-widget-integration/plan.md) |
| Smoke и документация | [task-04-smoke-docs](impl/frontend/iteration-5-assistant-chat/tasks/task-04-smoke-docs/plan.md)                 |


### Состав работ

- UI панели чата (сообщения, input, индикатор отправки).
- Загрузка истории по participant/flow из API; POST нового сообщения (согласовать с `[docs/tech/api-contracts.md](../tech/api-contracts.md)`).
- Состояния offline/ошибка; не логировать содержимое в клиентских `console.log` в прод-сборке.

### Definition of Done

**Агент (самопроверка):**

- Отправка сообщения обновляет UI и сохраняется на backend; после перезагрузки история восстанавливается.
- Виджет доступен с основных экранов.

**Пользователь:**

- Открыть сайт, открыть плавающий чат, отправить несколько реплик, обновить страницу — история на месте.

### Проверки после блока


| Кто           | Что сделать                                                |
| ------------- | ---------------------------------------------------------- |
| **Результат** | Ассистент доступен из любой страницы без ухода с маршрута. |


---

## Итерация 6: Чат в основной области («Чат»)

**Цель:** Полноценная страница «Чат» в основном layout с той же историей и отправкой.

**План итерации:** `[docs/tasks/impl/frontend/iteration-6-main-chat-page/plan.md](impl/frontend/iteration-6-main-chat-page/plan.md)`


| Задача               | `plan.md`                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- |
| ChatContext          | [task-01-chat-context](impl/frontend/iteration-6-main-chat-page/tasks/task-01-chat-context/plan.md)               |
| Рефактор ChatPanel   | [task-02-chat-panel-refactor](impl/frontend/iteration-6-main-chat-page/tasks/task-02-chat-panel-refactor/plan.md) |
| Страница и layout    | [task-03-chat-page-layout](impl/frontend/iteration-6-main-chat-page/tasks/task-03-chat-page-layout/plan.md)       |
| Smoke и документация | [task-04-smoke-docs](impl/frontend/iteration-6-main-chat-page/tasks/task-04-smoke-docs/plan.md)                   |


### Состав работ

- Маршрут «Чат» в навигации; переиспользование компонентов из итерации 5.
- Адаптация layout (ширина, скролл, мобильная ширина при необходимости).
- Синхронизация состояния с виджетом (общий store/context — минимально достаточный вариант).

### Definition of Done

**Агент (самопроверка):**

- Пользователь может вести диалог с той же сессией в виджете и на странице без расхождения истории (или явное ограничение описано в `summary.md`).
- Навигация не сбрасывает непрочитанное состояние без необходимости.

**Пользователь:**

- Открыть «Чат» из меню; сравнить историю с виджетом после нескольких сообщений.

### Проверки после блока


| Кто           | Что сделать                      |
| ------------- | -------------------------------- |
| **Результат** | Два UX-контура чата согласованы. |


---

## Итерация 7: Ревью качества кода frontend

**Цель:** Привести код в соответствие с best practices и зафиксировать исправления.

### Состав работ

- Прогон рекомендаций skills `**vercel-react-best-practices`** и `**nextjs-app-router-patterns**` (границы Server/Client Components, данные, bundle, loading.tsx).
- Исправить критические замечания; некритические — backlog в `summary.md`.
- При необходимости добавить eslint/prettier или существующие правила shadcn/Next — в `web/package.json` и README.

### Definition of Done

**Агент (самопроверка):**

- Список проверок из skills пройден или для каждого исключения есть причина в `summary.md`.
- `web-build` без warning’ов, блокирующих деплой (или порог согласован).

**Пользователь:**

- `make web-build`, smoke-тест основных маршрутов вручную.

### Проверки после блока


| Кто           | Что сделать                                                           |
| ------------- | --------------------------------------------------------------------- |
| **Makefile**  | Убедиться, что `web-lint` / `web-build` отражены в корневом Makefile. |
| **Результат** | Код готов к дальнейшим фичам (голос, SQL).                            |


---

## Итерация 8: Голосовой режим чата

**Цель:** Пользователь может общаться голосом в вебе и в Telegram-боте.

**План итерации:** `[docs/tasks/impl/frontend/iteration-8-voice-chat/plan.md](impl/frontend/iteration-8-voice-chat/plan.md)` · **ADR:** `[docs/adr/adr-004-voice-stt.md](../adr/adr-004-voice-stt.md)`

### Состав работ

- **Web:** запись с микрофона (Web Audio / MediaRecorder), отправка на backend или прямой поток — вариант зафиксировать в ADR/`plan.md`; отображение статуса; fallback при отказе в разрешении.
- **Telegram:** интеграция voice message → backend (расширение `bot/handlers.py` и при необходимости новый endpoint); без хранения сырого аудио в логах.
- Безопасность: лимиты размера/длительности; соответствие `[docs/vision.md](../vision.md)` по логированию.
- Документация: `[docs/integrations.md](../integrations.md)`, `[docs/tech/api-contracts.md](../tech/api-contracts.md)`, при необходимости ADR в `docs/adr/`.

### Definition of Done

**Агент (самопроверка):**

- E2E сценарий: голосовое в вебе → текст ответа ассистента (или согласованный pipeline).
- E2E в Telegram: voice message обрабатывается ботом через backend.
- Тесты/скрипты smoke при необходимости в `scripts/` + цель в Makefile.

**Пользователь:**

- В браузере: записать фразу, получить ответ; в Telegram: отправить voice, получить ответ.

### Проверки после блока


| Кто           | Что сделать                                                    |
| ------------- | -------------------------------------------------------------- |
| **Makefile**  | Команды для локальной проверки голоса (если вводятся скрипты). |
| **Результат** | Парафраз сценария «голосом к ассистенту» в обоих клиентах.     |


---

## Итерация 9: Ответы по данным из БД (Text-to-SQL)

**Цель:** Ассистент (или отдельный режим) отвечает на вопросы по структурированным данным потока с прозрачным и безопасным доступом к БД.

**План итерации:** `[docs/tasks/impl/frontend/iteration-9-text-to-sql/plan.md](impl/frontend/iteration-9-text-to-sql/plan.md)`

### Состав работ

- Зафиксировать варианты (Text-to-SQL через LLM, ограниченный набор шаблонов запросов, read-only роль БД, allowlist таблиц) в `plan.md` и кратко в `docs/adr/` при выборе.
- Реализация в backend: сервис генерации SQL → валидация → выполнение только SELECT (или аналог); лимиты; отказ от опасных конструкций.
- API для веб/бота: «вопрос к данным» с Correlation ID; ответ с кратким объяснением и таблицей/агрегатом (без утечки схемы лишнему пользователю — политика в `plan.md`).
- Сценарии тестирования в `docs/` или `backend/tests/`; обновить `[docs/tech/api-contracts.md](../tech/api-contracts.md)`.
- Frontend: минимальный UI (в чате или отдельная команда) для режима «вопрос к данным».

### Definition of Done

**Агент (самопроверка):**

- Принятая архитектура описана; реализация соответствует threat-model (нет произвольного write; нет секретов в промпте логов).
- Набор сценариев из `plan.md` пройден автоматически или вручную с чек-листом.

**Пользователь:**

- Задать вопрос по числу сдач/студентам в тестовом потоке; сверить ответ с прямым SQL/control query (инструкция в `summary.md`).

### Проверки после блока


| Кто           | Что сделать                                                                              |
| ------------- | ---------------------------------------------------------------------------------------- |
| **Skills**    | При ревью безопасности — `sharp-edges` (опционально).                                    |
| **Результат** | Преподаватель может уточнять метрики естественным языком в рамках политики безопасности. |


---

*После завершения каждой итерации: `summary.md` по итерации, `summary.md` по каждой задаче, обновление статусов в таблице сверху.*