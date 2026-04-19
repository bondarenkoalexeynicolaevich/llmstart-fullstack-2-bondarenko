# Итерация 5 — summary

**Сделано:** ORM и миграции 003–004 по [`docs/data-model.md`](../../../data-model.md); read API для структуры потока и списка сдач; исправлена логика `POST /v1/submissions`; seed и интеграционные тесты; OpenAPI, `docs/tests.md`. `knowledge_items.embedding` в БД — `double precision[]` (без расширения pgvector) для совместимости с обычным PostgreSQL 16.

**Отклонения от DDL в data-model:** целевой тип `vector(1536)` заменён на `float8[]` до отдельной миграции на pgvector.

**Отклонения:** отдельный `make smoke-full` не добавлялся — достаточно существующих `make test-backend` и `smoke-dialog`.
