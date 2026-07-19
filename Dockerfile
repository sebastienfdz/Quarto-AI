# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Runtime stage
FROM python:3.12-slim-bookworm

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY quarto_ai/ /app/quarto_ai/
COPY main.py /app/main.py

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

ENTRYPOINT ["python", "main.py"]
