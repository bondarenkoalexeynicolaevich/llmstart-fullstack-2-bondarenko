MVP Telegram Bot — план реализации

Создаваемые файлы





requirements.txt — зависимости



.env.example — шаблон переменных



.gitignore



Makefile



bot/config.py



bot/llm_client.py



bot/handlers.py



bot/main.py



README.md

1. requirements.txt

aiogram==3.*
openai
python-dotenv
ruff

Установка через uv pip install -r requirements.txt.

2. .env.example

BOT_TOKEN=
OPENROUTER_API_KEY=
LLM_MODEL=openai/gpt-4o-mini
SYSTEM_PROMPT=
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=
MAX_HISTORY_MESSAGES=
LOG_LEVEL=INFO

3. bot/config.py

Датакласс Settings, загружаемый один раз через python-dotenv. Обязательные поля (BOT_TOKEN, OPENROUTER_API_KEY, LLM_MODEL, SYSTEM_PROMPT) валидируются при старте — если отсутствуют, бот не запускается.

4. bot/llm_client.py

Класс LLMClient с методом async chat(messages: list[dict]) -> str. Инициализирует AsyncOpenAI с base_url="https://openrouter.ai/api/v1". При ошибке логирует ERROR и пробрасывает исключение.

5. bot/handlers.py

Хранит историю: dict[int, list[dict]] (ключ — user_id).

Обработчики:





/start — приветствие, сброс истории



/reset — сброс истории



текстовое сообщение — добавить в историю, вызвать LLMClient.chat, добавить ответ в историю, ответить пользователю



нетекстовое сообщение — сообщить о неподдержке



ошибка LLM — нейтральное сообщение, история не изменяется

MAX_HISTORY_MESSAGES: если задан, перед запросом обрезать историю (кроме system-сообщения).

6. bot/main.py

Точка входа: настройка logging, создание Bot + Dispatcher, регистрация роутера из handlers.py, запуск dp.start_polling(bot).

7. Makefile

install:
    python -m venv .venv
    .venv\Scripts\uv pip install -r requirements.txt

run:
    .venv\Scripts\python -m bot.main

lint:
    .venv\Scripts\ruff check bot/

format:
    .venv\Scripts\ruff format bot/

Поток данных

sequenceDiagram
    actor User
    participant handlers as handlers.py
    participant llm as llm_client.py
    participant OR as OpenRouter

    User->>handlers: текст
    handlers->>handlers: добавить в историю
    handlers->>llm: chat(history)
    llm->>OR: POST /chat/completions
    OR-->>llm: ответ
    llm-->>handlers: текст ответа
    handlers->>handlers: добавить ответ в историю
    handlers-->>User: reply

