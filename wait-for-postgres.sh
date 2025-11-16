#!/bin/bash

echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h postgres -p 5432 -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
  echo "PostgreSQL not ready - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is READY."
exec "$@"
