.PHONY: build
build:
	docker compose build

.PHONY: run
run:
	docker compose up

.PHONY: local
local:
	docker compose -f docker-compose.dev.yml up -d
	ENV_FILE=.env.local uvicorn main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: stop
stop:
	docker compose down

.PHONY: lint
lint:
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy .
