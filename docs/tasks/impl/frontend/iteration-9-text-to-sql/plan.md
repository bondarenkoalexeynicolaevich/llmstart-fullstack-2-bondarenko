# Итерация 9: Ответы по данным из БД (text-to-SQL / классификатор intent)

## Цель

Преподаватель задаёт свободный вопрос по метрикам потока и получает агрегированный результат из PostgreSQL без небезопасного произвольного SQL.

## Решение (кратко)

- **ADR-005:** LLM только возвращает JSON `intent` + `params` из whitelist; в БД — фиксированные параметризованные запросы SQLAlchemy.
- **`POST /v1/flows/{flow_id}/data-query`**, JWT и роль `teacher`; ответ включает `correlation_id` (без логирования текста вопроса).
- **Web:** режим «Данные» (иконка) в `web/components/chat-panel.tsx`: вызов API, табличный результат; только для учителя.

**Контракт:** `docs/api/backend-v1.openapi.yaml`; ADR: `docs/adr/adr-005-text-to-sql.md`.

## Задачи

| Задача | Каталог |
|--------|---------|
| ADR и контракт | [task-01-adr-and-contract](tasks/task-01-adr-and-contract/) |
| Backend сервис + endpoint | [task-02-backend-service](tasks/task-02-backend-service/) |
| Frontend UI | [task-03-frontend-ui](tasks/task-03-frontend-ui/) |
| Тесты и актуализация docs | [task-04-tests-and-docs](tasks/task-04-tests-and-docs/) |

## Артефакты кода

- `backend/services/data_query.py`
- `backend/api/data_query_web.py`
- `web/lib/api/data-query.ts`
