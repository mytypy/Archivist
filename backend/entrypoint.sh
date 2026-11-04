#!/bin/sh
set -e

echo "Waiting for Postgres..."
until pg_isready -h $POSTGRES_HOST -d $POSTGRES_DB; do
  sleep 5
done

echo "Running migrations..."
alembic upgrade head

echo "Starting API..."

exec uvicorn --port 8000 main:app --host 0.0.0.0