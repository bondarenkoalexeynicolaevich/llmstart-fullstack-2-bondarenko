# Задача 01: README, OpenAPI, Makefile

## Цель

Явно описать доступ к схеме API при запущенном FastAPI и связь с YAML в репозитории; сверить команды README с Makefile; кратко подсказать PostgreSQL «с нуля».

## Состав работ

- Раздел **OpenAPI / схема API**: `http://<API_HOST>:<API_PORT>/openapi.json`, UI `/docs` и `/redoc`; design-time — `docs/api/backend-v1.openapi.yaml`, честное примечание о возможном расхождении с JSON до синхронизации.
- Проверить цели: `install`, `run-backend`, `migrate-upgrade`, `test-backend`, `lint`, `lint-backend`, при желании строка про `make format`.
- При необходимости — минимальная подсказка по PostgreSQL (свой инстанс или docker one-liner).

## Definition of Done

После `make run-backend` по README понятно, куда открыть браузер за схемой; каждая упомянутая цель `make` существует.
