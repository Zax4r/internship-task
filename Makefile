.PHONY: lint
lint:
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy .
