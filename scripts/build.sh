#!/bin/bash
# MemoryLink Docker Build Script
# Handles building Docker images with proper tagging and optimization

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="memorylink"
REGISTRY="${DOCKER_REGISTRY:-}"
BUILD_ENV="${BUILD_ENV:-production}"
VERSION="${VERSION:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[BUILD]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
MemoryLink Docker Build Script

Usage: $0 [OPTIONS]

Options:
    -h, --help          Show this help message
    -e, --env ENV       Build environment (development|production) [default: production]
    -t, --tag TAG       Docker tag [default: latest]
    -r, --registry REG  Docker registry URL
    -p, --push          Push image to registry after build
    --no-cache          Build without Docker cache
    --multi-platform    Build for multiple platforms (linux/amd64,linux/arm64)
    --dry-run          Show commands without executing

Examples:
    $0                                  # Build production image with 'latest' tag
    $0 -e development -t dev            # Build development image with 'dev' tag  
    $0 -t v1.0.0 -p                    # Build and push version 1.0.0
    $0 --multi-platform -t v1.0.0      # Build multi-platform image

EOF
}

# Parse command line arguments
PUSH=false
NO_CACHE=""
MULTI_PLATFORM=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            BUILD_ENV="$2"
            shift 2
            ;;
        -t|--tag)
            VERSION="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --multi-platform)
            MULTI_PLATFORM=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate build environment
if [[ "$BUILD_ENV" != "development" && "$BUILD_ENV" != "production" ]]; then
    error "Invalid build environment: $BUILD_ENV (must be 'development' or 'production')"
    exit 1
fi

# Construct image tags
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="$REGISTRY/$IMAGE_NAME"
else
    FULL_IMAGE_NAME="$IMAGE_NAME"
fi

TAGS=(
    "$FULL_IMAGE_NAME:$VERSION"
    "$FULL_IMAGE_NAME:$BUILD_ENV"
)

# Add latest tag for production builds
if [[ "$BUILD_ENV" == "production" && "$VERSION" != "latest" ]]; then
    TAGS+=("$FULL_IMAGE_NAME:latest")
fi

# Build information
log "Building MemoryLink Docker image"
log "Project root: $PROJECT_ROOT"
log "Build environment: $BUILD_ENV"
log "Version: $VERSION"
log "Tags: ${TAGS[*]}"

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker daemon
if ! docker info &> /dev/null; then
    error "Docker daemon is not running"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Verify required files exist
REQUIRED_FILES=(
    "Dockerfile"
    "requirements/base.txt"
    "docker/entrypoint.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        error "Required file not found: $file"
        exit 1
    fi
done

# Create build command
BUILD_ARGS=(
    "--build-arg" "BUILD_ENV=$BUILD_ENV"
    "--build-arg" "APP_VERSION=$VERSION"
    "--build-arg" "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    "--build-arg" "VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
)

# Add tags to build command
TAG_ARGS=()
for tag in "${TAGS[@]}"; do
    TAG_ARGS+=("--tag" "$tag")
done

# Platform arguments for multi-platform builds
PLATFORM_ARGS=()
if [[ "$MULTI_PLATFORM" == "true" ]]; then
    PLATFORM_ARGS+=("--platform" "linux/amd64,linux/arm64")
fi

# Build command
BUILD_CMD=(
    "docker" "build"
    "${BUILD_ARGS[@]}"
    "${TAG_ARGS[@]}"
    "${PLATFORM_ARGS[@]}"
    $NO_CACHE
    "."
)

# Execute or show build command
if [[ "$DRY_RUN" == "true" ]]; then
    log "Would execute: ${BUILD_CMD[*]}"
else
    log "Executing build command..."
    "${BUILD_CMD[@]}"
    
    # Verify build success
    if [[ $? -eq 0 ]]; then
        success "Docker image built successfully"
        
        # Show image information
        log "Image details:"
        for tag in "${TAGS[@]}"; do
            if docker images "$tag" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -v REPOSITORY; then
                log "  $tag"
            fi
        done
    else
        error "Docker build failed"
        exit 1
    fi
fi

# Push to registry if requested
if [[ "$PUSH" == "true" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would push images to registry"
    else
        log "Pushing images to registry..."
        
        for tag in "${TAGS[@]}"; do
            log "Pushing $tag..."
            docker push "$tag"
            
            if [[ $? -eq 0 ]]; then
                success "Pushed $tag"
            else
                error "Failed to push $tag"
                exit 1
            fi
        done
        
        success "All images pushed successfully"
    fi
fi

# Security scan (if available)
if command -v docker-scout &> /dev/null; then
    if [[ "$DRY_RUN" != "true" ]]; then
        log "Running security scan with Docker Scout..."
        docker scout cves "${TAGS[0]}" || warn "Security scan completed with warnings"
    fi
fi

# Cleanup old images (optional)
if [[ "$BUILD_ENV" == "development" && "$DRY_RUN" != "true" ]]; then
    log "Cleaning up old development images..."
    docker image prune -f --filter "label=memorylink-dev" || true
fi

success "Build process completed successfully!"
log "Next steps:"
log "  - Test the image: docker run --rm -p 8080:8080 ${TAGS[0]}"
log "  - Run with compose: docker-compose up"
log "  - Deploy to production: Use docker-compose.prod.yml"