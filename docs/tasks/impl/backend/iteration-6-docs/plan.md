# Итерация 6: Документирование backend

## Цель

Воспроизводимый запуск, полнота переменных окружения, описание OpenAPI (runtime и YAML), согласованность README с Makefile, точечное обновление интеграций.

## Ценность

Новый разработчик поднимает backend по README без скрытых шагов; контракт API находится и в репозитории (YAML), и на запущенном сервисе (`/openapi.json`, `/docs`).

## Задачи

| Задача | Папка |
|--------|--------|
| README, OpenAPI, Makefile | [`tasks/task-01-readme-openapi/`](tasks/task-01-readme-openapi/) |
| `.env.example`, интеграции, закрытие итерации | [`tasks/task-02-env-integrations-close/`](tasks/task-02-env-integrations-close/) |

## Definition of Done

- README описывает `/openapi.json`, `/docs` (/redoc), связь с `docs/api/backend-v1.openapi.yaml`; команды совпадают с Makefile.
- `.env.example` покрывает поля `Settings` из `backend/config.py` и `TEST_DATABASE_URL`; шаблон `DATABASE_URL` не привязан к одному порту учебника.
- В `docs/integrations.md` указан discovery схемы при работающем backend.
- `summary.md` итерации, `summary.md` задач, строка итерации 6 в `tasklist-backend.md` обновлены.

## Ссылки

- Контракт: `docs/api/backend-v1.openapi.yaml`
- Тесты и БД: `docs/tests.md`, `backend/tests/conftest.py`
