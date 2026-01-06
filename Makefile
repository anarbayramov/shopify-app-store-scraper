
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: setup install lint format run destroy clean build

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install poetry black
	$(VENV)/bin/poetry install

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/poetry install

lint:
	$(VENV)/bin/poetry run black --check --diff .

format:
	$(VENV)/bin/poetry run black .

destroy:
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf storage/cache

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0
