# Telegram-бот (MVP)

Домашняя работа по 2 модулю "AI-driven Fullstack разработка"

Чат-бот на [aiogram](https://docs.aiogram.dev/) 3.x + [OpenRouter](https://openrouter.ai/) (OpenAI-compatible API). Подробности — в [docs/vision.md](docs/vision.md).

## Требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (для установки зависимостей)
- GNU Make (опционально; можно вызывать команды вручную)

## Быстрый старт

1. Скопируйте переменные окружения и заполните секреты:

   ```bash
   cp .env.example .env
   ```

   Обязательно: `BOT_TOKEN`, `OPENROUTER_API_KEY`, `LLM_MODEL`, `SYSTEM_PROMPT`.

2. Установка и запуск:

   ```bash
   make install
   make run
   ```

   Запуск из корня репозитория (чтобы импорт `bot` разрешался).

3. Линтинг:

   ```bash
   make lint
   make format
   ```

## Без Make

```bash
python -m venv .venv
uv pip install -r requirements.txt --python .venv/Scripts/python.exe   # Windows
# uv pip install -r requirements.txt --python .venv/bin/python        # Linux/macOS
.venv/Scripts/python.exe -m bot.main
```

## Команды бота

- `/start` — приветствие и сброс истории
- `/reset` — сброс истории диалога

История хранится в памяти процесса и теряется при перезапуске.
