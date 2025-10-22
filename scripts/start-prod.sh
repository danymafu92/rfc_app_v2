#!/usr/bin/env bash
# Production startup script (Linux)
# Usage: ./scripts/start-prod.sh [--no-install]
#   --no-install : skip installing dependencies

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
cd "$REPO_ROOT"

INSTALL=true
for arg in "$@"; do
  if [ "$arg" = "--no-install" ]; then
    INSTALL=false
  fi
done

if [ "$INSTALL" = true ]; then
  echo "Installing Python dependencies..."
  python -m pip install --upgrade pip
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  fi

  echo "Installing frontend dependencies..."
  npm install
fi

# Build frontend
echo "Building frontend (Vite)..."
npm run build

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Apply migrations
echo "Applying Django migrations"
python manage.py migrate --noinput

# Launch Gunicorn with WhiteNoise for static serving
# Adjust WORKERS/ENV as needed
GUNICORN_CMD=(gunicorn --bind 0.0.0.0:8000 --workers 3 "weather_prediction.wsgi:application")

echo "Starting Gunicorn: ${GUNICORN_CMD[*]}"
exec "${GUNICORN_CMD[@]}"
