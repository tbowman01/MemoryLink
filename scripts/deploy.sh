#!/bin/bash
# MemoryLink Deployment Script
# Handles deployment to various environments (Docker, Kubernetes)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-development}"
DEPLOYMENT_TYPE="${DEPLOYMENT_TYPE:-docker-compose}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
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
MemoryLink Deployment Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    start           Start the application
    stop            Stop the application  
    restart         Restart the application
    status          Show deployment status
    logs            Show application logs
    update          Update to latest version
    backup          Create data backup
    restore         Restore from backup
    scale           Scale application replicas

Options:
    -h, --help              Show this help message
    -e, --env ENV           Environment (development|production) [default: development]
    -t, --type TYPE         Deployment type (docker-compose|kubernetes) [default: docker-compose]
    -f, --file FILE         Custom config file
    --replicas N            Number of replicas for scaling
    --dry-run              Show commands without executing
    --force                Force operation without confirmation

Examples:
    $0 start                           # Start development environment
    $0 -e production start             # Start production environment  
    $0 -t kubernetes start             # Deploy to Kubernetes
    $0 scale --replicas 3              # Scale to 3 replicas
    $0 backup                          # Create backup
    $0 logs                            # Show logs

EOF
}

# Parse command line arguments
REPLICAS=""
DRY_RUN=false
FORCE=false
CONFIG_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        -f|--file)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --replicas)
            REPLICAS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        start|stop|restart|status|logs|update|backup|restore|scale)
            COMMAND="$1"
            shift
            break
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    error "Invalid environment: $ENVIRONMENT (must be 'development' or 'production')"
    exit 1
fi

# Validate deployment type
if [[ "$DEPLOYMENT_TYPE" != "docker-compose" && "$DEPLOYMENT_TYPE" != "kubernetes" ]]; then
    error "Invalid deployment type: $DEPLOYMENT_TYPE (must be 'docker-compose' or 'kubernetes')"
    exit 1
fi

# Validate command
if [[ -z "$COMMAND" ]]; then
    error "No command specified"
    show_help
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Docker Compose functions
docker_compose_start() {
    log "Starting MemoryLink with Docker Compose ($ENVIRONMENT environment)"
    
    local compose_file="docker-compose.yml"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    if [[ -n "$CONFIG_FILE" ]]; then
        compose_file="$CONFIG_FILE"
    fi
    
    local cmd="docker-compose -f $compose_file up -d"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would execute: $cmd"
    else
        log "Executing: $cmd"
        $cmd
        
        # Wait for health check
        log "Waiting for application to be ready..."
        sleep 10
        
        if docker_compose_health_check "$compose_file"; then
            success "MemoryLink started successfully"
            docker_compose_show_info "$compose_file"
        else
            error "Health check failed"
            exit 1
        fi
    fi
}

docker_compose_stop() {
    log "Stopping MemoryLink"
    
    local compose_file="docker-compose.yml"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    local cmd="docker-compose -f $compose_file down"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would execute: $cmd"
    else
        $cmd
        success "MemoryLink stopped"
    fi
}

docker_compose_health_check() {
    local compose_file="$1"
    local container_name="memorylink-dev"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        container_name="memorylink-prod"
    fi
    
    # Check if container is running
    if ! docker ps | grep -q "$container_name"; then
        return 1
    fi
    
    # Check health endpoint
    local max_attempts=12
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 5
        ((attempt++))
    done
    
    return 1
}

docker_compose_show_info() {
    local compose_file="$1"
    
    log "Deployment Information:"
    log "  Environment: $ENVIRONMENT"
    log "  Config file: $compose_file"
    log "  API URL: http://localhost:8080"
    log "  API Docs: http://localhost:8080/docs"
    log "  Health: http://localhost:8080/api/v1/health"
    
    # Show container status
    log "Container status:"
    docker-compose -f "$compose_file" ps
}

# Kubernetes functions
kubernetes_start() {
    log "Deploying MemoryLink to Kubernetes ($ENVIRONMENT environment)"
    
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
        exit 1
    fi
    
    local overlay_dir="k8s/overlays/$ENVIRONMENT"
    if [[ ! -d "$overlay_dir" ]]; then
        error "Kubernetes overlay directory not found: $overlay_dir"
        exit 1
    fi
    
    local cmd="kubectl apply -k $overlay_dir"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would execute: $cmd"
    else
        log "Applying Kubernetes manifests..."
        $cmd
        
        # Wait for deployment
        log "Waiting for deployment to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/memorylink-deployment -n memorylink-$ENVIRONMENT
        
        success "MemoryLink deployed to Kubernetes successfully"
        kubernetes_show_info
    fi
}

kubernetes_stop() {
    log "Stopping MemoryLink in Kubernetes"
    
    local overlay_dir="k8s/overlays/$ENVIRONMENT"
    local cmd="kubectl delete -k $overlay_dir"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would execute: $cmd"
    else
        $cmd
        success "MemoryLink stopped in Kubernetes"
    fi
}

kubernetes_show_info() {
    local namespace="memorylink-$ENVIRONMENT"
    
    log "Kubernetes Deployment Information:"
    log "  Namespace: $namespace"
    log "  Environment: $ENVIRONMENT"
    
    # Show pod status
    log "Pod status:"
    kubectl get pods -n "$namespace"
    
    # Show service information
    log "Services:"
    kubectl get svc -n "$namespace"
}

# Backup functions
create_backup() {
    log "Creating MemoryLink data backup..."
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
        # Find Docker volume or mounted directory
        local data_source="./data"  # Default path
        
        if [[ -d "$data_source" ]]; then
            log "Backing up data from $data_source"
            cp -r "$data_source" "$backup_dir/"
            success "Backup created at $backup_dir"
        else
            error "Data directory not found: $data_source"
            exit 1
        fi
    else
        warn "Kubernetes backup not implemented yet"
    fi
}

# Main execution
main() {
    log "MemoryLink Deployment Manager"
    log "Environment: $ENVIRONMENT"
    log "Deployment Type: $DEPLOYMENT_TYPE"
    log "Command: $COMMAND"
    
    case "$COMMAND" in
        start)
            if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
                docker_compose_start
            else
                kubernetes_start
            fi
            ;;
        stop)
            if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
                docker_compose_stop
            else
                kubernetes_stop
            fi
            ;;
        restart)
            log "Restarting MemoryLink..."
            if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
                docker_compose_stop
                sleep 2
                docker_compose_start
            else
                kubernetes_stop
                sleep 5
                kubernetes_start
            fi
            ;;
        status)
            if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
                docker-compose ps
            else
                kubectl get all -n "memorylink-$ENVIRONMENT"
            fi
            ;;
        logs)
            if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
                docker-compose logs -f
            else
                kubectl logs -f deployment/memorylink-deployment -n "memorylink-$ENVIRONMENT"
            fi
            ;;
        backup)
            create_backup
            ;;
        scale)
            if [[ -z "$REPLICAS" ]]; then
                error "Number of replicas not specified. Use --replicas N"
                exit 1
            fi
            
            if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
                kubectl scale deployment/memorylink-deployment --replicas="$REPLICAS" -n "memorylink-$ENVIRONMENT"
                success "Scaled to $REPLICAS replicas"
            else
                warn "Scaling only supported in Kubernetes deployment"
            fi
            ;;
        *)
            error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main