#!/bin/bash
# MemoryLink Docker Entrypoint Script
# Handles initialization, health checks, and graceful startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] MemoryLink:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

# Environment variables with defaults
MEMORYLINK_ENV=${MEMORYLINK_ENV:-production}
MEMORYLINK_HOST=${MEMORYLINK_HOST:-0.0.0.0}
MEMORYLINK_PORT=${MEMORYLINK_PORT:-8080}
MEMORYLINK_DATA_PATH=${MEMORYLINK_DATA_PATH:-/data}
MEMORYLINK_LOG_LEVEL=${MEMORYLINK_LOG_LEVEL:-INFO}
MEMORYLINK_WORKERS=${MEMORYLINK_WORKERS:-1}

log "Starting MemoryLink container..."
log "Environment: $MEMORYLINK_ENV"
log "Host: $MEMORYLINK_HOST"
log "Port: $MEMORYLINK_PORT"
log "Workers: $MEMORYLINK_WORKERS"

# Check if running as root (security check)
if [ "$(id -u)" = "0" ]; then
    warn "Running as root user. This is not recommended for production."
fi

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    local dirs=(
        "$MEMORYLINK_DATA_PATH"
        "$MEMORYLINK_DATA_PATH/vector"
        "$MEMORYLINK_DATA_PATH/metadata"
        "$MEMORYLINK_DATA_PATH/logs"
        "$MEMORYLINK_DATA_PATH/backups"
        "/logs"
        "/tmp"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "Created directory: $dir"
        fi
    done
    
    # Set proper permissions
    if [ -w "$MEMORYLINK_DATA_PATH" ]; then
        chmod 755 "$MEMORYLINK_DATA_PATH"
        find "$MEMORYLINK_DATA_PATH" -type d -exec chmod 755 {} \;
        success "Directory permissions set correctly"
    else
        error "Cannot write to data directory: $MEMORYLINK_DATA_PATH"
        exit 1
    fi
}

# Validate environment
validate_environment() {
    log "Validating environment..."
    
    # Check Python version
    python_version=$(python --version 2>&1)
    log "Python version: $python_version"
    
    # Check if required packages are installed
    if ! python -c "import fastapi, chromadb, sentence_transformers" 2>/dev/null; then
        error "Required Python packages are not installed"
        exit 1
    fi
    
    # Check encryption key if encryption is enabled
    if [ "${MEMORYLINK_ENCRYPTION_ENABLED:-true}" = "true" ]; then
        if [ -z "${MEMORYLINK_ENCRYPTION_KEY}" ]; then
            warn "Encryption is enabled but no encryption key provided"
            warn "Data will be stored unencrypted"
        else
            success "Encryption key configured"
        fi
    fi
    
    # Check disk space
    available_space=$(df -h "$MEMORYLINK_DATA_PATH" | awk 'NR==2{print $4}')
    log "Available disk space: $available_space"
    
    success "Environment validation completed"
}

# Initialize database and vector store
initialize_storage() {
    log "Initializing storage systems..."
    
    # Test vector database initialization
    python -c "
import os
os.environ.setdefault('MEMORYLINK_DATA_PATH', '$MEMORYLINK_DATA_PATH')
try:
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(
        path='$MEMORYLINK_DATA_PATH/vector',
        settings=Settings(anonymized_telemetry=False, allow_reset=False)
    )
    collection = client.get_or_create_collection(name='memories')
    print('Vector database initialized successfully')
except Exception as e:
    print(f'Error initializing vector database: {e}')
    exit(1)
" || {
        error "Failed to initialize vector database"
        exit 1
    }
    
    success "Storage systems initialized"
}

# Health check function
health_check() {
    log "Performing initial health check..."
    
    # Check if the application can start
    timeout 30 python -c "
import sys
sys.path.insert(0, '/app')
try:
    from app.main import app
    print('Application imports successfully')
except Exception as e:
    print(f'Application import failed: {e}')
    sys.exit(1)
" || {
        error "Application failed to import correctly"
        exit 1
    }
    
    success "Health check passed"
}

# Signal handlers for graceful shutdown
cleanup() {
    log "Received shutdown signal, cleaning up..."
    
    # Kill any background processes
    if [ ! -z "$UVICORN_PID" ]; then
        log "Stopping uvicorn server..."
        kill -TERM "$UVICORN_PID" 2>/dev/null || true
        wait "$UVICORN_PID" 2>/dev/null || true
    fi
    
    log "Cleanup completed"
    exit 0
}

# Set up signal traps
trap cleanup SIGTERM SIGINT SIGQUIT

# Main execution
main() {
    log "MemoryLink container starting..."
    
    # Run initialization steps
    create_directories
    validate_environment
    initialize_storage
    health_check
    
    success "Initialization completed successfully"
    
    # Start the application
    log "Starting MemoryLink application..."
    
    # Build uvicorn command
    UVICORN_CMD="uvicorn app.main:app"
    UVICORN_CMD="$UVICORN_CMD --host $MEMORYLINK_HOST"
    UVICORN_CMD="$UVICORN_CMD --port $MEMORYLINK_PORT"
    UVICORN_CMD="$UVICORN_CMD --workers $MEMORYLINK_WORKERS"
    
    if [ "$MEMORYLINK_ENV" = "development" ]; then
        UVICORN_CMD="$UVICORN_CMD --reload"
        log "Development mode: auto-reload enabled"
    fi
    
    if [ "$MEMORYLINK_LOG_LEVEL" = "DEBUG" ]; then
        UVICORN_CMD="$UVICORN_CMD --log-level debug"
    else
        UVICORN_CMD="$UVICORN_CMD --log-level info"
    fi
    
    log "Executing: $UVICORN_CMD"
    
    # Start uvicorn in background so we can trap signals
    $UVICORN_CMD &
    UVICORN_PID=$!
    
    success "MemoryLink is running (PID: $UVICORN_PID)"
    success "API available at http://$MEMORYLINK_HOST:$MEMORYLINK_PORT"
    success "API documentation at http://$MEMORYLINK_HOST:$MEMORYLINK_PORT/docs"
    
    # Wait for the process
    wait $UVICORN_PID
}

# Handle direct command execution
if [ $# -eq 0 ]; then
    main
else
    # If arguments provided, execute them instead
    log "Executing command: $@"
    exec "$@"
fi