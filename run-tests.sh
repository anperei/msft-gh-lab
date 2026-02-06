#!/bin/bash
# Quick test runner script

echo "🔍 Checking if servers are running..."

# Check backend
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running on port 8000"
    echo "   Start it with: cd backend && TEST_MODE=true uv run uvicorn src.main:app --reload"
    exit 1
fi

# Check frontend
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend not running on port 3000"
    echo "   Start it with: cd frontend && npm run dev"
    exit 1
fi

echo "✅ Both servers running!"
echo "🧪 Running E2E tests..."

pytest tests/e2e/ -v "$@"
