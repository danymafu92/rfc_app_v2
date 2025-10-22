#!/usr/bin/env bash
# Start both backend (Django) and frontend (Vite) for local development.
# Usage: ./scripts/start-dev.sh [--no-install] [--build]
#   --no-install : skip installing dependencies
#   --build      : build frontend before starting servers

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
cd "$REPO_ROOT"

INSTALL=true
BUILD=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-install) INSTALL=false; shift ;;
    --build) BUILD=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [ "$INSTALL" = true ]; then
  echo "Installing Python dependencies..."
  python -m pip install --upgrade pip
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  fi

  echo "Installing frontend dependencies (root package.json)..."
  npm install
fi

if [ "$BUILD" = true ]; then
  echo "Building frontend..."
  npm run build
fi

# Start Django and Vite in background; forward logs and ensure cleanup
LOG_DIR="$REPO_ROOT/.dev_logs"
mkdir -p "$LOG_DIR"

# Start Django dev server
echo "Starting Django dev server (http://localhost:8000)"
python manage.py runserver > "$LOG_DIR/django.log" 2>&1 &
DJANGO_PID=$!

# Start Vite dev server (serves frontend at http://localhost:5173)
echo "Starting Vite dev server (http://localhost:5173)"
npm run dev > "$LOG_DIR/vite.log" 2>&1 &
VITE_PID=$!

# Trap cleanup
cleanup() {
  echo "Stopping servers..."
  kill $DJANGO_PID 2>/dev/null || true
  kill $VITE_PID 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM EXIT

# Tail logs so the script stays alive and you can see output
echo "Tailing logs (press Ctrl-C to stop)"

# Use tail -f if available, otherwise sleep loop
if command -v tail >/dev/null 2>&1; then
  tail -f "$LOG_DIR/django.log" -n +1 &
  TAIL1=$!
  tail -f "$LOG_DIR/vite.log" -n +1 &
  TAIL2=$!
  wait $TAIL1 $TAIL2
else
  while true; do sleep 1; done
fi
