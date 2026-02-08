# Stage 1: Builder
# Use Python 3.10 slim for smaller image size
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies (for psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# Note: Copying backend/requirements.txt directly
COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

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
# IMPORTANT: Adjusting paths since context is root
COPY backend/src/ /app/src/
COPY backend/alembic.ini /app/alembic.ini
COPY backend/alembic/ /app/alembic/

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (HF Spaces expects 7860)
ENV PORT=7860
EXPOSE 7860

# Run with Gunicorn + Uvicorn workers
# Adjust --workers based on CPU cores (HF Spaces = 2 vCPU)
CMD gunicorn src.ai_career_advisor.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
