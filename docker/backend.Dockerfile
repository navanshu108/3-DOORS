# Multi-stage Dockerfile for Local Research Agent Backend using uv
FROM python:3.12-slim-bookworm AS builder

# Install uv for fast, reliable package management
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies first for efficient caching
COPY backend/pyproject.toml backend/uv.lock /app/backend/
WORKDIR /app/backend
RUN uv pip install --system .

# Production runtime stage
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Install runtime system libraries needed for fitz / curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create unprivileged application user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy application source code
COPY backend/app /app/app
COPY backend/pyproject.toml /app/

# Create data directories with appropriate permissions
RUN mkdir -p /app/data/documents /app/data/vector_store /app/data/cache \
    && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DATABASE_PATH=/app/data/vector_store
ENV DOCUMENTS_PATH=/app/data/documents
ENV CACHE_PATH=/app/data/cache

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
