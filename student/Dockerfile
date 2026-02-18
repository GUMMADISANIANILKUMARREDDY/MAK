# Build stage: create wheel (optional, for install)
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
COPY app.py main.py ./
COPY config config
COPY api api
COPY services services
COPY schemas schemas
COPY utils utils
COPY db db
RUN pip install --no-cache-dir build && python -m build --wheel 2>/dev/null || true

# Runtime image
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py main.py ./
COPY config config
COPY api api
COPY services services
COPY schemas schemas
COPY utils utils
COPY db db

# Optional: copy .env at build time (override at run with env file or env vars)
# COPY .env .env

EXPOSE 8001
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
