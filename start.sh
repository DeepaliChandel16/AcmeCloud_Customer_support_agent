#!/usr/bin/env bash
set -e

echo "Starting AcmeCloud Support Agent..."

if ! command -v ollama &>/dev/null; then
    echo "ERROR: Ollama is not installed or not in PATH."
    exit 1
fi

if ! pgrep -x ollama &>/dev/null; then
    echo "Starting Ollama..."
    ollama serve &>/dev/null &
    sleep 3
else
    echo "Ollama is already running."
fi

echo "Launching Streamlit app..."
cd "$(dirname "$0")"
python -m streamlit run src/ui/app.py --server.port 8501 &
sleep 5
if command -v open &>/dev/null; then
    open http://localhost:8501
elif command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:8501
fi
echo "App is running at http://localhost:8501"

if [ "$1" = "--devui" ]; then
    echo ""
    echo "Starting DevUI debug server on port 8080..."
    python devui_server.py &
    sleep 3
    if command -v open &>/dev/null; then
        open http://localhost:8080
    elif command -v xdg-open &>/dev/null; then
        xdg-open http://localhost:8080
    fi
    echo "DevUI is running at http://localhost:8080"
fi
