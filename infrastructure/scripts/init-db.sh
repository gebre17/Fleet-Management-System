#!/bin/bash
set -e

echo "Initializing TrackFleet database..."

# Wait for postgres to be ready
until PGPASSWORD=$DB_PASSWORD psql -h postgres -U trackfleet -d trackfleet -c "\q"; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is ready!"

# Run Alembic migrations
cd /app
alembic upgrade head

echo "Database initialized successfully!"
