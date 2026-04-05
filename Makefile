ifeq ($(OS),Windows_NT)
  PY := .venv/Scripts/python.exe
else
  PY := .venv/bin/python
endif

.PHONY: install run run-backend migrate-upgrade lint lint-bot lint-backend format test-backend smoke-dialog

install:
	python -m venv .venv
	uv pip install -r requirements.txt --python $(PY)

run:
	$(PY) -m bot.main

run-backend:
	$(PY) -m backend

migrate-upgrade:
	$(PY) -m alembic -c backend/alembic.ini upgrade head

lint: lint-bot lint-backend

lint-bot:
	$(PY) -m ruff check bot/

lint-backend:
	$(PY) -m ruff check backend/

test-backend:
	$(PY) -m pytest backend/tests

smoke-dialog:
	$(PY) scripts/smoke_dialog_api.py

format:
	$(PY) -m ruff format bot/ backend/
