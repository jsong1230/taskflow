# Stage 1: Builder - Install dependencies and prepare application
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# This layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install only runtime dependencies (PostgreSQL client for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN adduser --disabled-password --gecos "" --uid 1000 appuser

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Update PATH to include user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose application port
EXPOSE 8000

# Run the application with production settings
# --workers 1: Single worker by default (adjust based on CPU cores in production)
# --host 0.0.0.0: Accept connections from any interface
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
