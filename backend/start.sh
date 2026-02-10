#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment script..."

# Run database migrations
echo "📦 Running database migrations..."
cd /app
alembic upgrade head

# Start the application
echo "🔥 Starting application server..."
cd /app/src
exec gunicorn ai_career_advisor.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
