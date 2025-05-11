#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting database migration and container setup..."

# Run Alembic autogenerate
echo "📝 Generating database migrations..."
alembic revision --autogenerate -m "auto-generated migration"

# Run Alembic upgrade
echo "⬆️  Applying database migrations..."
alembic upgrade head

# Start containers
echo "🐳 Starting containers..."
docker-compose up --build

# Add a trap to handle script interruption
trap 'echo "🛑 Script interrupted. Stopping containers..."; docker-compose down' INT TERM 