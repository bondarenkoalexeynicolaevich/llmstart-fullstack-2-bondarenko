# task-02: README и docs/tests.md

## Что сделать

- В [`README.md`](../../../../../../README.md) добавить раздел **Quality** (или «Проверки качества»): `make lint`, `make test`, `make format`; указать зависимость тестов от PostgreSQL и переменных из [`docs/tests.md`](../../../../../../docs/tests.md).
- В [`docs/tests.md`](../../../../../../docs/tests.md) при необходимости одна строка: запуск через **`make test`** наряду с `make test-backend`.

## Критерий готовности

- Новый разработчик видит единую точку входа для тестов и линта без чтения только Makefile.
