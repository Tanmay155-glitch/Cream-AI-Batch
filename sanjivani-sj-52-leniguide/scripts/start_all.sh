#!/bin/bash
# start_all.sh — Start LeniGuide API and UI for development or Docker.
# Usage: bash scripts/start_all.sh

set -e

echo "============================================"
echo "LeniGuide — Starting Services"
echo "============================================"

# Build Chroma index if not present
if [ ! -d ".chroma" ] || [ -z "$(ls -A .chroma 2>/dev/null)" ]; then
    echo "Building ChromaDB index..."
    python -c "from app.vectorstore import index_chunks; index_chunks()" 2>/dev/null || echo "Index build skipped (Chroma unavailable)"
fi

# Start API server
PORT="${PORT:-8000}"
echo "Starting API on port $PORT..."
uvicorn app.main:app --host 0.0.0.0 --port "$PORT" &
API_PID=$!

echo "API started (PID: $API_PID)"
echo "============================================"

# Wait for API to be ready
sleep 3

# If streamlit is available, start UI too
if command -v streamlit &>/dev/null; then
    echo "Starting Streamlit UI on port 8501..."
    streamlit run ui/app.py --server.port 8501 --server.headless true &
    UI_PID=$!
    echo "UI started (PID: $UI_PID)"
fi

echo "============================================"
echo "LeniGuide is running!"
echo "  API: http://localhost:$PORT/docs"
echo "  UI:  http://localhost:8501"
echo "============================================"

# Wait for background processes
wait
