#!/bin/bash
# MemoryLink Docker Test Script
# Comprehensive testing of Docker deployment

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_TIMEOUT=60
API_BASE_URL="http://localhost:8080"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[TEST]${NC} $1"
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

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Function to record test result
record_test() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    if [[ "$result" == "PASS" ]]; then
        ((TESTS_PASSED++))
        success "✓ $test_name"
        TEST_RESULTS+=("PASS: $test_name")
    else
        ((TESTS_FAILED++))
        error "✗ $test_name: $message"
        TEST_RESULTS+=("FAIL: $test_name - $message")
    fi
}

# Wait for service to be ready
wait_for_service() {
    local url="$1"
    local timeout="$2"
    local start_time=$(date +%s)
    
    log "Waiting for service at $url (timeout: ${timeout}s)"
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [[ $elapsed -ge $timeout ]]; then
            return 1
        fi
        
        if curl -f -s "$url" > /dev/null 2>&1; then
            return 0
        fi
        
        sleep 2
    done
}

# Test Docker image build
test_image_build() {
    log "Testing Docker image build..."
    
    cd "$PROJECT_ROOT"
    
    if docker build -t memorylink:test . > /dev/null 2>&1; then
        record_test "Docker Image Build" "PASS"
    else
        record_test "Docker Image Build" "FAIL" "Build failed"
        return 1
    fi
}

# Test container startup
test_container_startup() {
    log "Testing container startup..."
    
    # Stop any existing test containers
    docker stop memorylink-test 2>/dev/null || true
    docker rm memorylink-test 2>/dev/null || true
    
    # Start test container
    if docker run -d --name memorylink-test -p 8080:8080 \
        -e MEMORYLINK_ENV=test \
        -e MEMORYLINK_LOG_LEVEL=DEBUG \
        memorylink:test > /dev/null 2>&1; then
        
        # Wait for container to be ready
        if wait_for_service "$API_BASE_URL/api/v1/health" $TEST_TIMEOUT; then
            record_test "Container Startup" "PASS"
        else
            record_test "Container Startup" "FAIL" "Service not ready within timeout"
            return 1
        fi
    else
        record_test "Container Startup" "FAIL" "Container failed to start"
        return 1
    fi
}

# Test health endpoint
test_health_endpoint() {
    log "Testing health endpoint..."
    
    local response=$(curl -s "$API_BASE_URL/api/v1/health" 2>/dev/null)
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]] && echo "$response" | grep -q '"status":"healthy"'; then
        record_test "Health Endpoint" "PASS"
    else
        record_test "Health Endpoint" "FAIL" "Health check failed"
    fi
}

# Test API documentation
test_api_docs() {
    log "Testing API documentation..."
    
    local response=$(curl -s "$API_BASE_URL/docs" 2>/dev/null)
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]] && echo "$response" | grep -q "swagger"; then
        record_test "API Documentation" "PASS"
    else
        record_test "API Documentation" "FAIL" "Documentation not accessible"
    fi
}

# Test memory API endpoints
test_memory_api() {
    log "Testing memory API endpoints..."
    
    # Test POST /api/v1/memory (create memory)
    local create_response=$(curl -s -X POST "$API_BASE_URL/api/v1/memory" \
        -H "Content-Type: application/json" \
        -d '{
            "text": "Test memory for Docker testing",
            "tags": ["test", "docker"],
            "metadata": {"source": "test"}
        }' 2>/dev/null)
    
    local create_exit_code=$?
    
    if [[ $create_exit_code -eq 0 ]] && echo "$create_response" | grep -q '"id"'; then
        record_test "Memory Creation API" "PASS"
        
        # Test POST /api/v1/memory/search (search memories)
        local search_response=$(curl -s -X POST "$API_BASE_URL/api/v1/memory/search" \
            -H "Content-Type: application/json" \
            -d '{
                "query": "test memory",
                "top_k": 10
            }' 2>/dev/null)
        
        local search_exit_code=$?
        
        if [[ $search_exit_code -eq 0 ]] && echo "$search_response" | grep -q '"memories"'; then
            record_test "Memory Search API" "PASS"
        else
            record_test "Memory Search API" "FAIL" "Search endpoint failed"
        fi
    else
        record_test "Memory Creation API" "FAIL" "Create endpoint failed"
    fi
}

# Test data persistence
test_data_persistence() {
    log "Testing data persistence..."
    
    # Create a test volume
    docker volume create memorylink-test-data > /dev/null 2>&1
    
    # Stop current container
    docker stop memorylink-test > /dev/null 2>&1
    docker rm memorylink-test > /dev/null 2>&1
    
    # Start container with volume
    docker run -d --name memorylink-test -p 8080:8080 \
        -v memorylink-test-data:/data \
        -e MEMORYLINK_ENV=test \
        memorylink:test > /dev/null 2>&1
    
    # Wait for service
    if wait_for_service "$API_BASE_URL/api/v1/health" 30; then
        # Add a memory
        local memory_id=$(curl -s -X POST "$API_BASE_URL/api/v1/memory" \
            -H "Content-Type: application/json" \
            -d '{
                "text": "Persistence test memory",
                "tags": ["persistence", "test"]
            }' | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        
        if [[ -n "$memory_id" ]]; then
            # Restart container
            docker stop memorylink-test > /dev/null 2>&1
            docker rm memorylink-test > /dev/null 2>&1
            
            docker run -d --name memorylink-test -p 8080:8080 \
                -v memorylink-test-data:/data \
                -e MEMORYLINK_ENV=test \
                memorylink:test > /dev/null 2>&1
            
            if wait_for_service "$API_BASE_URL/api/v1/health" 30; then
                # Search for the memory
                local search_result=$(curl -s -X POST "$API_BASE_URL/api/v1/memory/search" \
                    -H "Content-Type: application/json" \
                    -d '{"query": "persistence test", "top_k": 5}')
                
                if echo "$search_result" | grep -q "Persistence test memory"; then
                    record_test "Data Persistence" "PASS"
                else
                    record_test "Data Persistence" "FAIL" "Memory not found after restart"
                fi
            else
                record_test "Data Persistence" "FAIL" "Service failed to restart"
            fi
        else
            record_test "Data Persistence" "FAIL" "Failed to create test memory"
        fi
    else
        record_test "Data Persistence" "FAIL" "Service not ready for persistence test"
    fi
    
    # Clean up volume
    docker volume rm memorylink-test-data > /dev/null 2>&1 || true
}

# Test resource limits
test_resource_limits() {
    log "Testing resource limits..."
    
    # Stop current container
    docker stop memorylink-test > /dev/null 2>&1
    docker rm memorylink-test > /dev/null 2>&1
    
    # Start container with resource limits
    if docker run -d --name memorylink-test -p 8080:8080 \
        --memory=512m \
        --cpus=0.5 \
        -e MEMORYLINK_ENV=test \
        memorylink:test > /dev/null 2>&1; then
        
        if wait_for_service "$API_BASE_URL/api/v1/health" 30; then
            record_test "Resource Limits" "PASS"
        else
            record_test "Resource Limits" "FAIL" "Service failed with resource limits"
        fi
    else
        record_test "Resource Limits" "FAIL" "Container failed to start with limits"
    fi
}

# Test security (non-root user)
test_security() {
    log "Testing security configuration..."
    
    # Check if container runs as non-root
    local user_info=$(docker exec memorylink-test id 2>/dev/null)
    
    if echo "$user_info" | grep -v -q "uid=0(root)"; then
        record_test "Non-root User" "PASS"
    else
        record_test "Non-root User" "FAIL" "Container running as root"
    fi
    
    # Check read-only filesystem (excluding writable mounts)
    local writable_dirs=$(docker exec memorylink-test find / -type d -writable 2>/dev/null | grep -v -E "^/(data|logs|tmp|proc|sys|dev)" | wc -l)
    
    if [[ $writable_dirs -lt 10 ]]; then
        record_test "Filesystem Security" "PASS"
    else
        record_test "Filesystem Security" "WARN" "Many writable directories found"
    fi
}

# Test Docker Compose
test_docker_compose() {
    log "Testing Docker Compose setup..."
    
    # Stop any running containers
    docker stop memorylink-test 2>/dev/null || true
    docker rm memorylink-test 2>/dev/null || true
    
    cd "$PROJECT_ROOT"
    
    # Test development compose
    if docker-compose -f docker-compose.yml config > /dev/null 2>&1; then
        record_test "Docker Compose Config (Dev)" "PASS"
    else
        record_test "Docker Compose Config (Dev)" "FAIL" "Invalid development compose file"
    fi
    
    # Test production compose
    if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
        record_test "Docker Compose Config (Prod)" "PASS"
    else
        record_test "Docker Compose Config (Prod)" "FAIL" "Invalid production compose file"
    fi
}

# Clean up test resources
cleanup() {
    log "Cleaning up test resources..."
    
    # Stop and remove test containers
    docker stop memorylink-test 2>/dev/null || true
    docker rm memorylink-test 2>/dev/null || true
    
    # Remove test image
    docker rmi memorylink:test 2>/dev/null || true
    
    # Remove test volumes
    docker volume rm memorylink-test-data 2>/dev/null || true
    
    success "Cleanup completed"
}

# Show test summary
show_summary() {
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    
    log "Test Summary"
    log "============"
    log "Total Tests: $total_tests"
    log "Passed: $TESTS_PASSED"
    log "Failed: $TESTS_FAILED"
    log "Success Rate: $(( TESTS_PASSED * 100 / total_tests ))%"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        success "All tests passed! 🎉"
        return 0
    else
        error "Some tests failed:"
        for result in "${TEST_RESULTS[@]}"; do
            if [[ "$result" == FAIL:* ]]; then
                echo "  - ${result#FAIL: }"
            fi
        done
        return 1
    fi
}

# Main execution
main() {
    log "Starting MemoryLink Docker Test Suite"
    log "====================================="
    
    # Ensure we're in the right directory
    cd "$PROJECT_ROOT"
    
    # Run tests
    test_image_build
    test_container_startup
    test_health_endpoint
    test_api_docs
    test_memory_api
    test_data_persistence
    test_resource_limits
    test_security
    test_docker_compose
    
    # Show results
    show_summary
    local exit_code=$?
    
    # Cleanup
    cleanup
    
    exit $exit_code
}

# Handle script termination
trap cleanup EXIT

# Execute main function
main