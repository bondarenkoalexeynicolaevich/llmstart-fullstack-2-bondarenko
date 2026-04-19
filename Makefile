ifeq ($(OS),Windows_NT)
  PY := .venv/Scripts/python.exe
else
  PY := .venv/bin/python
endif

.PHONY: install run run-backend migrate-upgrade db-up db-down db-reset db-shell db-logs db-status db-seed lint lint-bot lint-backend lint-scripts format test test-backend smoke-dialog

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

format:
	$(PY) -m ruff format bot/ backend/ scripts/
