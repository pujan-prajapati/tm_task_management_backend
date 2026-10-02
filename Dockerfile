# BUILD STAGE
FROM python:3.14-slim AS builder

# Copy UV binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# UV Docker optimizations
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Install dependencies first (cached if unchanged)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Copy app code and install project
COPY . .
RUN uv sync --locked --no-dev

# PRODUCTION STAGE
FROM python:3.14-slim AS production

WORKDIR /app

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy app and dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

