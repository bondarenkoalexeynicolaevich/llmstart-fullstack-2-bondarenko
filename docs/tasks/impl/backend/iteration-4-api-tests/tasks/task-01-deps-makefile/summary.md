# Задача 01: итог

- В [`requirements.txt`](../../../../../../../requirements.txt): `pytest`, `pytest-asyncio`, `psycopg[binary]` (sync TRUNCATE/seed без конфликта loop с `TestClient`).
- [`Makefile`](../../../../../../../Makefile): цель `test-backend`.
- Корневой [`pytest.ini`](../../../../../../../pytest.ini): `testpaths = backend/tests`, `asyncio_mode = auto`.
