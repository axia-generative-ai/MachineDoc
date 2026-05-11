# ai-service/Dockerfile
# Locked at the 2026-05-08 integration sync. Runs on :8001 alongside the
# backend on :8000. uv-managed dependency tree (pyproject.toml + uv.lock).
FROM python:3.13-slim

# uv is the package manager. Install via the official static binary so we
# don't need pip and can keep the layer cache stable.
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /usr/local/bin/

WORKDIR /code

# Copy lock + manifest first so dependency install caches independently of
# source code changes. --frozen forces uv to honor uv.lock exactly.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Now copy the rest of the source. uv sync below installs the project
# itself (`app` package) into the venv.
COPY . .
RUN uv sync --frozen

ENV PYTHONPATH=/code \
    PATH="/code/.venv/bin:${PATH}"

EXPOSE 8001
