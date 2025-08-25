# Multi-stage Docker build for MemoryLink
# Stage 1: Build dependencies and prepare environment
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_ENV=production
ARG APP_VERSION=latest

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /build

# Copy requirements files
COPY requirements/ requirements/

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install base requirements
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements/base.txt

# Install production dependencies if needed
RUN if [ "$BUILD_ENV" = "production" ]; then \
        pip install --no-cache-dir -r requirements/prod.txt || true; \
    fi

# Stage 2: Production runtime
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    MEMORYLINK_ENV=production \
    MEMORYLINK_HOST=0.0.0.0 \
    MEMORYLINK_PORT=8080

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r memorylink && \
    useradd -r -g memorylink -d /app -s /bin/bash memorylink

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application directories
RUN mkdir -p /app /data /logs && \
    chown -R memorylink:memorylink /app /data /logs

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=memorylink:memorylink app/ ./app/
COPY --chown=memorylink:memorylink scripts/ ./scripts/
COPY --chown=memorylink:memorylink config/ ./config/

# Copy startup script
COPY --chown=memorylink:memorylink docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Create requirements directory for health checks
RUN mkdir -p requirements/
COPY --chown=memorylink:memorylink requirements/base.txt requirements/

# Switch to non-root user
USER memorylink

# Create data subdirectories
RUN mkdir -p /data/{vector,metadata,logs,backups}

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]