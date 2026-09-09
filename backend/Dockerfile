FROM public.ecr.aws/docker/library/python:3.12-slim AS base

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic
COPY tests/fixtures ./tests/fixtures

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "near_misses.main:app", "--host", "0.0.0.0", "--port", "8000"]
