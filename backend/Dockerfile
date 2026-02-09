# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
# Use --only-binary to prefer prebuilt wheels (faster)
# Use --no-cache-dir to reduce image size
RUN pip install --upgrade pip && \
    pip wheel --only-binary :all: --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt || \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies (libpq for postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies from wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY src/ /app/src/
COPY alembic.ini /app/alembic.ini
COPY alembic/ /app/alembic/

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Add src to Python path so ai_career_advisor module is discoverable
ENV PYTHONPATH=/app/src

# Expose port 10000 (Render default)
ENV PORT=10000
EXPOSE 10000

# Run with Gunicorn + Uvicorn workers
# Change to src directory so ai_career_advisor is directly importable
WORKDIR /app/src
# Use shell form CMD to allow $PORT expansion
CMD gunicorn ai_career_advisor.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
