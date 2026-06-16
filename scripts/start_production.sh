#!/bin/bash

echo "=== Production startup — Dzeck AI Agent ==="

# Verify frontend was built
if [ ! -d "/home/runner/workspace/frontend/dist" ]; then
    echo "WARNING: frontend/dist not found — UI will not be served"
fi

echo "Starting backend on port 5000..."
cd /home/runner/workspace/backend

exec python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 5000 \
    --log-level info \
    --no-access-log \
    --timeout-keep-alive 75
