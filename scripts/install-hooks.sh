#!/bin/bash

# Install git hooks for TaskFlow project
# Run this script once to set up pre-commit hooks

echo "🪝 Installing git hooks..."

# Copy pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook for TaskFlow
# Runs linting and tests before allowing commit

set -e  # Exit on first error

echo "🔍 Running pre-commit checks..."
echo ""

# Backend checks
echo "📦 Backend checks..."
cd backend

echo "  - Running ruff check..."
python -m ruff check app/ || {
  echo "❌ Ruff linting failed! Fix errors and try again."
  exit 1
}

echo "  - Running ruff format check..."
python -m ruff format --check app/ || {
  echo "❌ Code formatting check failed! Run 'ruff format app/' to fix."
  exit 1
}

echo "  - Checking database connection..."
# Check if PostgreSQL is running (Docker Compose or local)
if nc -z localhost 5433 2>/dev/null || nc -z localhost 5432 2>/dev/null; then
  echo "  - Running pytest..."
  pytest -v --tb=short || {
    echo "❌ Tests failed! Fix failing tests and try again."
    exit 1
  }
else
  echo "  ⚠️  Database not available, skipping pytest"
  echo "  ℹ️  Run 'docker compose up -d' to enable full tests"
  echo "  ℹ️  Tests will still run in CI/CD pipeline"
fi

cd ..

# Frontend checks
echo ""
echo "🎨 Frontend checks..."
cd frontend

echo "  - Running ESLint..."
npm run lint || {
  echo "❌ ESLint failed! Fix linting errors and try again."
  exit 1
}

echo "  - Running TypeScript check..."
npx tsc --noEmit || {
  echo "❌ TypeScript check failed! Fix type errors and try again."
  exit 1
}

cd ..

echo ""
echo "✅ All pre-commit checks passed!"
echo "🚀 Proceeding with commit..."
EOF

# Make it executable
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "ℹ️  The hook will run automatically before each commit."
echo "ℹ️  To skip the hook temporarily, use: git commit --no-verify"
