#!/bin/bash

# Manual check script
# Run this to check your code before committing

set -e

echo "🔍 Running all checks..."
echo ""

# Backend
echo "📦 Backend checks..."
cd backend
echo "  - Ruff lint..."
python -m ruff check app/
echo "  - Ruff format..."
python -m ruff format --check app/
echo "  - Checking database connection..."
# Check if PostgreSQL is running (Docker Compose or local)
if nc -z localhost 5433 2>/dev/null || nc -z localhost 5432 2>/dev/null; then
  echo "  - Pytest..."
  pytest -v
else
  echo "  ⚠️  Database not available, skipping pytest"
  echo "  ℹ️  Run 'docker compose up -d' to enable full tests"
fi
cd ..

# Frontend
echo ""
echo "🎨 Frontend checks..."
cd frontend
echo "  - ESLint..."
npm run lint
echo "  - TypeScript..."
npx tsc --noEmit
echo "  - Build..."
npm run build
cd ..

echo ""
echo "✅ All checks passed!"
