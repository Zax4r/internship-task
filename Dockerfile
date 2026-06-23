# BUILDER

FROM python:3.12-slim AS builder

RUN pip install poetry==2.3.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# RUNTIME

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN chmod +x prestart.sh
ENTRYPOINT ["./prestart.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
