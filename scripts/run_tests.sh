#!/bin/bash

# MemoryLink Test Runner Script
# Comprehensive test execution with proper environment setup and reporting

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/.venv"
TEST_RESULTS_DIR="${PROJECT_ROOT}/test-results"
COVERAGE_DIR="${PROJECT_ROOT}/coverage"

# Default test categories
RUN_UNIT=true
RUN_INTEGRATION=false
RUN_SECURITY=false
RUN_PERFORMANCE=false
RUN_DOCKER=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            RUN_UNIT=true
            shift
            ;;
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --security)
            RUN_SECURITY=true
            shift
            ;;
        --performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        --docker)
            RUN_DOCKER=true
            shift
            ;;
        --all)
            RUN_UNIT=true
            RUN_INTEGRATION=true
            RUN_SECURITY=true
            RUN_PERFORMANCE=true
            RUN_DOCKER=true
            shift
            ;;
        --fast)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            RUN_SECURITY=false
            RUN_PERFORMANCE=false
            RUN_DOCKER=false
            shift
            ;;
        --ci)
            # CI mode - run essential tests
            RUN_UNIT=true
            RUN_INTEGRATION=true
            RUN_SECURITY=true
            RUN_PERFORMANCE=false
            RUN_DOCKER=true
            shift
            ;;
        --help)
            echo "MemoryLink Test Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --unit         Run unit tests (default)"
            echo "  --integration  Run integration tests"
            echo "  --security     Run security tests"
            echo "  --performance  Run performance tests"
            echo "  --docker       Run Docker tests"
            echo "  --all          Run all test categories"
            echo "  --fast         Run only unit tests (fast feedback)"
            echo "  --ci           Run CI test suite (unit + integration + security + docker)"
            echo "  --help         Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Setup test environment
setup_environment() {
    log_info "Setting up test environment..."
    
    # Create directories
    mkdir -p "$TEST_RESULTS_DIR"
    mkdir -p "$COVERAGE_DIR"
    
    # Set environment variables for testing
    export TESTING=true
    export LOG_LEVEL=DEBUG
    export DATABASE_URL="sqlite:///test.db"
    export ENCRYPTION_KEY="test-encryption-key-for-testing-only"
    export VECTOR_STORE_PATH="tests/tmp/vectors"
    export CACHE_SIZE=100
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "$VENV_PATH" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Install dependencies
    log_info "Installing test dependencies..."
    pip install --upgrade pip
    pip install -r tests/requirements.txt
    pip install -e .
    
    log_success "Test environment ready"
}

# Run unit tests
run_unit_tests() {
    if [[ "$RUN_UNIT" == true ]]; then
        log_info "Running unit tests..."
        
        pytest tests/unit/ \
            --marker=unit \
            --cov=src \
            --cov-report=html:"$COVERAGE_DIR/unit" \
            --cov-report=xml:"$COVERAGE_DIR/unit.xml" \
            --cov-report=term-missing \
            --junit-xml="$TEST_RESULTS_DIR/unit-tests.xml" \
            --verbose \
            --tb=short \
            || { log_error "Unit tests failed"; return 1; }
            
        log_success "Unit tests completed"
    fi
}

# Run integration tests
run_integration_tests() {
    if [[ "$RUN_INTEGRATION" == true ]]; then
        log_info "Running integration tests..."
        
        # Check for required services
        check_services() {
            log_info "Checking required services..."
            
            # Check if PostgreSQL is available
            if command -v pg_isready &> /dev/null; then
                if ! pg_isready -h localhost -p 5432 -U postgres &> /dev/null; then
                    log_warning "PostgreSQL not running, starting with Docker..."
                    docker run -d --name postgres-test \
                        -e POSTGRES_PASSWORD=test_password \
                        -e POSTGRES_DB=memorylink_test \
                        -p 5432:5432 \
                        postgres:15
                    sleep 5
                fi
            fi
            
            # Check if ChromaDB is available
            if ! curl -f http://localhost:8080/api/v1/heartbeat &> /dev/null; then
                log_warning "ChromaDB not running, starting with Docker..."
                docker run -d --name chroma-test \
                    -p 8080:8000 \
                    chromadb/chroma:latest
                sleep 5
            fi
        }
        
        check_services
        
        pytest tests/integration/ \
            --marker=integration \
            --cov=src \
            --cov-report=html:"$COVERAGE_DIR/integration" \
            --cov-report=xml:"$COVERAGE_DIR/integration.xml" \
            --junit-xml="$TEST_RESULTS_DIR/integration-tests.xml" \
            --verbose \
            || { log_error "Integration tests failed"; return 1; }
            
        log_success "Integration tests completed"
    fi
}

# Run security tests
run_security_tests() {
    if [[ "$RUN_SECURITY" == true ]]; then
        log_info "Running security tests..."
        
        # Run security-focused pytest tests
        pytest tests/security/ \
            --marker=security \
            --junit-xml="$TEST_RESULTS_DIR/security-tests.xml" \
            --verbose \
            || { log_error "Security tests failed"; return 1; }
        
        # Run Bandit security scan
        log_info "Running Bandit security scan..."
        bandit -r src/ -f json -o "$TEST_RESULTS_DIR/bandit-scan.json" || true
        
        # Run Safety dependency check
        log_info "Running Safety dependency check..."
        safety check --json --output "$TEST_RESULTS_DIR/safety-report.json" || true
        
        log_success "Security tests completed"
    fi
}

# Run performance tests
run_performance_tests() {
    if [[ "$RUN_PERFORMANCE" == true ]]; then
        log_info "Running performance tests..."
        
        pytest tests/performance/ \
            --marker=performance \
            --benchmark-json="$TEST_RESULTS_DIR/benchmark-results.json" \
            --benchmark-histogram="$TEST_RESULTS_DIR/benchmark-histogram.svg" \
            --junit-xml="$TEST_RESULTS_DIR/performance-tests.xml" \
            --verbose \
            || { log_error "Performance tests failed"; return 1; }
            
        log_success "Performance tests completed"
    fi
}

# Run Docker tests
run_docker_tests() {
    if [[ "$RUN_DOCKER" == true ]]; then
        log_info "Running Docker tests..."
        
        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            log_error "Docker is not available"
            return 1
        fi
        
        # Build test image
        log_info "Building Docker test image..."
        docker build -t memorylink:test . || { log_error "Docker build failed"; return 1; }
        
        pytest tests/docker/ \
            --marker=docker \
            --junit-xml="$TEST_RESULTS_DIR/docker-tests.xml" \
            --verbose \
            || { log_error "Docker tests failed"; return 1; }
            
        log_success "Docker tests completed"
    fi
}

# Generate test report
generate_report() {
    log_info "Generating test report..."
    
    REPORT_FILE="$TEST_RESULTS_DIR/test-summary.html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>MemoryLink Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #2196F3; background-color: #f5f5f5; }
        .success { border-left-color: #4CAF50; }
        .warning { border-left-color: #FF9800; }
        .error { border-left-color: #F44336; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-weight: bold; font-size: 1.2em; }
    </style>
</head>
<body>
    <h1 class="header">MemoryLink Test Report</h1>
    <p>Generated on: $(date)</p>
    
    <div class="section success">
        <h2>Test Execution Summary</h2>
EOF

    # Add test results to report
    if [[ -f "$TEST_RESULTS_DIR/unit-tests.xml" ]]; then
        echo "        <div class=\"metric\">Unit Tests: <span class=\"metric-value\">✓ PASSED</span></div>" >> "$REPORT_FILE"
    fi
    
    if [[ -f "$TEST_RESULTS_DIR/integration-tests.xml" ]]; then
        echo "        <div class=\"metric\">Integration Tests: <span class=\"metric-value\">✓ PASSED</span></div>" >> "$REPORT_FILE"
    fi
    
    if [[ -f "$TEST_RESULTS_DIR/security-tests.xml" ]]; then
        echo "        <div class=\"metric\">Security Tests: <span class=\"metric-value\">✓ PASSED</span></div>" >> "$REPORT_FILE"
    fi
    
    if [[ -f "$TEST_RESULTS_DIR/performance-tests.xml" ]]; then
        echo "        <div class=\"metric\">Performance Tests: <span class=\"metric-value\">✓ PASSED</span></div>" >> "$REPORT_FILE"
    fi
    
    if [[ -f "$TEST_RESULTS_DIR/docker-tests.xml" ]]; then
        echo "        <div class=\"metric\">Docker Tests: <span class=\"metric-value\">✓ PASSED</span></div>" >> "$REPORT_FILE"
    fi
    
    cat >> "$REPORT_FILE" << EOF
    </div>
    
    <div class="section">
        <h2>Coverage Information</h2>
        <p>Coverage reports are available in the <code>coverage/</code> directory.</p>
    </div>
    
    <div class="section">
        <h2>Test Artifacts</h2>
        <ul>
            <li>JUnit XML reports: <code>test-results/</code></li>
            <li>Coverage reports: <code>coverage/</code></li>
            <li>Security scans: <code>test-results/bandit-scan.json</code></li>
            <li>Performance benchmarks: <code>test-results/benchmark-results.json</code></li>
        </ul>
    </div>
</body>
</html>
EOF

    log_success "Test report generated: $REPORT_FILE"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    
    # Stop test containers
    docker stop postgres-test chroma-test 2>/dev/null || true
    docker rm postgres-test chroma-test 2>/dev/null || true
    
    # Clean up temporary test files
    rm -rf tests/tmp/ 2>/dev/null || true
    rm -f test.db 2>/dev/null || true
}

# Main execution
main() {
    log_info "Starting MemoryLink test suite..."
    
    # Setup
    setup_environment
    
    # Run tests
    run_unit_tests
    run_integration_tests
    run_security_tests
    run_performance_tests
    run_docker_tests
    
    # Generate report
    generate_report
    
    # Cleanup
    cleanup
    
    log_success "All tests completed successfully!"
    echo ""
    echo "Test results available in: $TEST_RESULTS_DIR"
    echo "Coverage reports available in: $COVERAGE_DIR"
    echo ""
}

# Trap cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"