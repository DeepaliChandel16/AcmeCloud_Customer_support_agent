#!/usr/bin/env bash
set -e

echo "Stopping AcmeCloud Support Agent..."

for port in 8501 8080; do
    PID=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo "Killing process on port $port (PID: $PID)..."
        kill -9 $PID 2>/dev/null || true
    else
        echo "No process on port $port."
    fi
done

echo "AcmeCloud Support Agent stopped."
