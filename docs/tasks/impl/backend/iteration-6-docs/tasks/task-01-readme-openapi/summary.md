# Задача 01: итог

## Сделано

- В [`README.md`](../../../../../../README.md) расширен блок **Backend**: краткая подсказка по PostgreSQL (в т.ч. пример `docker run`), уточнены переменные и приоритет `TEST_DATABASE_URL` для тестов.
- Добавлен подраздел **OpenAPI / схема API**: `/openapi.json`, `/docs`, `/redoc`, связь с [`docs/api/backend-v1.openapi.yaml`](../../../../../../docs/api/backend-v1.openapi.yaml) и примечание о возможном расхожении до синхронизации.
- Упомянуты `make format`; цели `install`, `run-backend`, `migrate-upgrade`, `test-backend`, `lint`, `lint-backend` сверены с [`Makefile`](../../../../../../Makefile) (`format` уже в `.PHONY`).
- В примерах curl добавлена отсылка к разделу OpenAPI.

## Отклонений от плана нет
