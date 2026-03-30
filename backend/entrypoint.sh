#!/usr/bin/env bash
set -e

echo "entrypoint: waiting for Postgres to become available..."

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${POSTGRES_USER:-smartcart}

MAX_WAIT=${MAX_WAIT:-60}
i=0
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
  i=$((i+1))
  echo "Postgres not ready yet (attempt $i/$MAX_WAIT)..."
  if [ "$i" -ge "$MAX_WAIT" ]; then
    echo "Timed out waiting for Postgres after $MAX_WAIT seconds"
    break
  fi
  sleep 1
done

echo "Postgres wait complete — starting uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
