# Задача 02: `.env.example`, интеграции, закрытие итерации

## Цель

Синхронизировать пример окружения с `backend.config.Settings`, добавить `TEST_DATABASE_URL`; дополнить `docs/integrations.md` про runtime OpenAPI; при необходимости скорректировать `docs/plan.md`; зафиксировать итоги в summary и tasklist.

## Состав работ

- `.env.example`: все ключи из `Settings` (`DATABASE_URL`, `API_*`, `INTERNAL_API_TOKEN`, `LOG_LEVEL`, OpenRouter/LLM, `MAX_HISTORY_MESSAGES`), плюс `TEST_DATABASE_URL` с пояснением приоритета в `conftest.py`; шаблон `DATABASE_URL` — закомментированный пример, без жёсткой учётки из чужого клона.
- `docs/integrations.md`: в блок Backend HTTP API — базовый URL + `/openapi.json` и `/docs`, дополнение к YAML в репо.
- `docs/plan.md` — только при явном рассинхроне с фактом наличия backend в репозитории.
- `summary.md` этой задачи и итерации; строка итерации 6 в `tasklist-backend.md`.

## Definition of Done

Новый разработчик видит полный список переменных backend и опцию отдельной БД для тестов; tasklist отражает завершение итерации 6.
