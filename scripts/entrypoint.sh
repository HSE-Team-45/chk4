#!/bin/sh
set -e

attempts=10
until alembic upgrade head; do
  attempts=$((attempts - 1))
  if [ "$attempts" -le 0 ]; then
    echo "alembic upgrade failed"
    exit 1
  fi
  sleep 1
done

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
