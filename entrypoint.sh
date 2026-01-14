#!/bin/sh
set -e
echo "Running migrations.."

alembic upgrade head

echo "Starting Flask dev server"

exec python -m flask run --host=0.0.0.0 --port=5000
