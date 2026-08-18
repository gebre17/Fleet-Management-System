#!/bin/sh
set -e

echo "Waiting for database and applying migrations..."
alembic upgrade head

exec "$@"
