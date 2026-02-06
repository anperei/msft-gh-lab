#!/bin/bash
# Test runner with backend restart for clean state

echo "🔍 Stopping existing backend..."
pkill -f "uvicorn.*src.main:app" || true
sleep 2

echo "🚀 Starting fresh backend..."
cd backend
TEST_MODE=true uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to be ready..."
sleep 3

# Check if backend started
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend running!"
echo "🧪 Running E2E tests..."

source .venv/bin/activate
pytest tests/e2e/ -v "$@"
TEST_EXIT=$?

echo "🛑 Stopping backend..."
kill $BACKEND_PID 2>/dev/null

exit $TEST_EXIT
