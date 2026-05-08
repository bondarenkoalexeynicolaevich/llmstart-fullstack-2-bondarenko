# Задача 01: Gap-анализ модели данных и контрактов

## Цель

Сверить [`docs/api/backend-v1.openapi.yaml`](../../../../../../api/backend-v1.openapi.yaml) и экраны итерации 0 с [`docs/data-model.md`](../../../../../../data-model.md) и текущим backend: зафиксировать, чего не хватает в БД/ORM/индексах до начала реализации маршрутов.

## Входы

- OpenAPI: `WebSessionCreate*`, `TeacherDashboardResponse`, ленты, матрица, лидерборд, веб-диалог.
- Модель: `User`, `Participant`, `Flow`, `Submission`, `DialogMessage`, `Material`, VIEW `participant_assignment_progress`.
- Текущий код: `backend/api/router.py`, существующие модели и миграции.

## Проверочный чек-лист

| Область | Вопрос | Действие при пробеле |
|---------|--------|----------------------|
| Веб-сессия | Есть ли способ резолва `telegram_username` → `User`? | Колонка `users.telegram_username` (CI unique partial) или явный seed-маппинг + ADR/summary |
| Роль teacher | Как проверить `Participant.role = teacher` для `flow_id`? | Использовать `participants`; убедиться в индексе `(flow_id, user_id)` / существующих FK |
| KPI / дельта | Откуда берутся «текущее» и «предыдущее» окна? | Зафиксировать в сервисе: например скользящие 7 дней vs предыдущие 7 (уточнить в summary при реализации) |
| Активность 14 дней | Что считаем событием (сообщения user, сдачи, оба)? | Одно правило на весь API; документировать в `api-contracts.md` |
| Лента вопросов | Как получить пары user→assistant? | SQL: оконные функции или два прохода; пустой `answer_summary` если нет пары |
| Лента сдач + материалы | JOIN `Submission`→`Assignment`→`Lesson`→`Material[]` | Проверить индексы на FK |
| Матрица | Достаточно ли VIEW `participant_assignment_progress`? | Ответ API = колонки уроков в порядке модуль/lesson `order`; ячейки `status`/`submitted_at` |
| Лидерборд | Как считать `overall_progress`, `lesson_statuses.state`, оси scatter? | Формула в сервисе (напр. доля заданий с непустой сдачей); подписи осей — как в OpenAPI |
| Диалог веб | `participant_id` + query `flow_id` — проверка принадлежности | FK `participants`; 403 если чужой UUID политики API |

## Выходы задачи

- Краткая таблица «поле контракта → таблица/поле или вычисление» в этом `plan.md` (в конце блока результатов после анализа) или в общем [`../../plan.md`](../../plan.md) — по выбору исполнителя.
- Решение: нужна ли миграция только для username / индексов — передаётся в [task-04](../task-04-migrations-and-seed/plan.md).

## Не входит

- Реализация SQL и эндпоинтов — задачи 02–03.
- Написание LLM-пайплайна (если вынесено) — явно указать заглушку в summary задачи 03.
