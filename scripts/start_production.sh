#!/bin/bash

echo "=== Production startup ==="

echo "Starting backend API on port 5000..."
cd /home/runner/workspace/backend
exec python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 5000 \
    --log-level info \
    --no-access-log
