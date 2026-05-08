ifeq ($(OS),Windows_NT)
  PY := .venv/Scripts/python.exe
else
  PY := .venv/bin/python
endif

.PHONY: install run run-backend migrate-upgrade db-up db-down db-reset db-shell db-logs db-status db-seed db-seed-frontend-demo db-verify-web-demo lint lint-bot lint-backend lint-scripts format test test-backend smoke-dialog voice-smoke web-install web-dev web-build web-lint

install:
	python -m venv .venv
	uv pip install -r requirements.txt --python $(PY)

run:
	$(PY) -m bot.main

run-backend:
	$(PY) -m backend

migrate-upgrade:
	$(PY) -m alembic -c backend/alembic.ini upgrade head

db-up:
	docker compose up -d --wait db

db-down:
	docker compose down

db-reset:
	docker compose down -v
	$(MAKE) db-up
	$(MAKE) migrate-upgrade

db-shell:
	docker compose exec db psql -U app -d app

db-logs:
	docker compose logs -f db

db-status:
	$(PY) -m alembic -c backend/alembic.ini current

db-seed:
	$(PY) scripts/seed_data.py

# Алиас под tasklist-frontend: те же данные, демо-поток 00000000-0000-0000-0000-000000000001, учитель 459032551
db-seed-frontend-demo: db-seed

# Проверка: демо-flow и преподаватель есть в БД из .env (тот же DATABASE_URL, что у seed/backend)
db-verify-web-demo:
	$(PY) scripts/db_verify_web_demo.py

lint: lint-bot lint-backend lint-scripts

lint-bot:
	$(PY) -m ruff check bot/

lint-backend:
	$(PY) -m ruff check backend/

lint-scripts:
	$(PY) -m ruff check scripts/

test: test-backend

test-backend:
	$(PY) -m pytest backend/tests

smoke-dialog:
	$(PY) scripts/smoke_dialog_api.py

# Ручной smoke голоса: OPENAI_API_KEY в .env, backend + seed, затем веб (кнопка микрофона) и голосовое в Telegram. Автотесты: pytest backend/tests/test_voice_dialog.py
voice-smoke:
	@echo "Голос: задайте OPENAI_API_KEY, запустите backend и используйте микрофон в веб-чате или voice в Telegram. См. docs/adr/adr-004-voice-stt.md"

format:
	$(PY) -m ruff format bot/ backend/ scripts/

# --- Web (Next.js в web/; зависимости через npm из web/package.json) ---
web-install:
	npm install --prefix web

web-dev:
	npm run dev --prefix web

web-build:
	npm run build --prefix web

web-lint:
	npm run lint --prefix web
