# Задача 01: pytest и цель test-backend

## Содержание

- В корневой `requirements.txt`: `pytest`, `pytest-asyncio`.
- `Makefile`: цель `test-backend` — запуск `pytest` для `backend/tests`.
- Корневой `pytest.ini`: `testpaths`, `asyncio_mode` для pytest-asyncio.

## Критерии готовности

- Установка зависимостей через существующий `make install` / `uv pip install -r requirements.txt` подключает тестовый раннер.
