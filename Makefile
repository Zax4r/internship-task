.PHONY: build
build:
	docker compose build

.PHONY: run
run:
	docker compose up

.PHONE: stop
stop:
	docker compose down

.PHONY: lint
lint:
	poetry run ruff format .
	poetry run ruff check . --fix
 	#poetry run mypy .
