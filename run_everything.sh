#!/usr/bin/env bash
# Starts the Trust Cart AI backend (FastAPI) and frontend (Vite/React) together.
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "============================================"
echo "  Trust Cart AI - starting backend + frontend"
echo "============================================"

if [ ! -x ".venv/bin/uvicorn" ]; then
    echo "[ERROR] .venv not found or incomplete at $(pwd)/.venv"
    echo "Run this first from this folder:"
    echo "    python3 -m venv .venv"
    echo "    .venv/bin/pip install -r requirements.txt fastapi \"uvicorn[standard]\" python-multipart"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "[frontend] node_modules not found - running npm install first..."
    (cd frontend && npm install)
fi

PIDS=()

cleanup() {
    echo ""
    echo "Stopping servers..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    exit 0
}
trap cleanup INT TERM

echo "Starting backend on http://localhost:8000 ..."
.venv/bin/uvicorn api_server:app --port 8000 &
PIDS+=($!)

echo "Starting frontend on http://localhost:5173 ..."
(cd frontend && npm run dev) &
PIDS+=($!)

echo ""
echo "Waiting for servers to warm up..."
sleep 5

# Try to open the browser automatically; fall back silently if no opener is available.
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5173" >/dev/null 2>&1 || true
fi

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."

wait
