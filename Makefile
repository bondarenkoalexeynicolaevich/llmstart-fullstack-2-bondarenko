ifeq ($(OS),Windows_NT)
  PY := .venv/Scripts/python.exe
else
  PY := .venv/bin/python
endif

.PHONY: install run lint format

install:
	python -m venv .venv
	uv pip install -r requirements.txt --python $(PY)

run:
	$(PY) -m bot.main

lint:
	$(PY) -m ruff check bot/

format:
	$(PY) -m ruff format bot/
