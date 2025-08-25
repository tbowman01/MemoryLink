# MemoryLink Testing Guide

## Overview

This document provides a comprehensive guide to the MemoryLink test suite, which follows the London School Test-Driven Development (TDD) approach with comprehensive coverage across all system components.

## Test Architecture

### Testing Philosophy

The MemoryLink test suite is built on the **London School TDD approach**, which emphasizes:

- **Outside-In Development**: Starting from user behavior down to implementation details
- **Mock-Driven Development**: Using mocks to isolate units and define contracts
- **Behavior Verification**: Focusing on interactions and collaborations between objects
- **Swarm Coordination**: Collaborative testing across agent swarms for comprehensive coverage

### Test Categories

#### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Approach**: Heavy use of mocks to isolate dependencies
- **Focus**: Behavior verification and interaction patterns
- **Speed**: Fast (< 100ms per test)
- **Coverage Target**: > 95%

#### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and workflows
- **Approach**: End-to-end workflow testing with real dependencies
- **Focus**: Complete user journeys and data flow
- **Speed**: Medium (< 5s per test)
- **Coverage Target**: > 85%

#### 3. Security Tests (`tests/security/`)
- **Purpose**: Validate security measures and attack resistance
- **Approach**: Penetration testing and vulnerability assessment
- **Focus**: Input validation, encryption, authentication, authorization
- **Speed**: Medium (< 10s per test)
- **Coverage Target**: 100% of security-critical paths

#### 4. Performance Tests (`tests/performance/`)
- **Purpose**: Validate performance requirements and scalability
- **Approach**: Load testing and benchmark analysis
- **Focus**: Latency (< 500ms), throughput, resource utilization
- **Speed**: Slow (< 30s per test)
- **Coverage Target**: All performance-critical operations

#### 5. Docker Tests (`tests/docker/`)
- **Purpose**: Validate containerization and deployment
- **Approach**: Container lifecycle testing and orchestration
- **Focus**: Build, deployment, networking, persistence
- **Speed**: Slow (< 60s per test)
- **Coverage Target**: All deployment scenarios

## Test Structure

### Directory Organization

```
tests/
├── conftest.py              # Global test configuration and fixtures
├── fixtures/
│   └── test_data.py         # Test data generation utilities
├── unit/                    # Unit tests
│   ├── test_memory_service.py
│   ├── test_encryption.py
│   ├── test_embeddings.py
│   └── test_api_endpoints.py
├── integration/             # Integration tests
│   ├── test_workflows.py
│   ├── test_vector_store.py
│   └── test_persistence.py
├── security/                # Security tests
│   └── test_security_validation.py
├── performance/             # Performance tests
│   └── test_performance_benchmarks.py
└── docker/                  # Docker tests
    └── test_container_deployment.py
```

### Key Testing Components

#### Test Fixtures (`conftest.py`)
- **SwarmTestCoordinator**: Coordinates tests across swarm agents
- **Mock Services**: Comprehensive mocks for all external dependencies
- **Test Data Generators**: Realistic test data for various scenarios
- **Performance Utilities**: Benchmarking and profiling tools

#### Test Data (`fixtures/test_data.py`)
- **TestDataGenerator**: Creates realistic memory content and metadata
- **EmbeddingTestData**: Generates and manages embedding vectors
- **SecurityTestData**: Malicious input patterns and attack vectors
- **PerformanceTestData**: Load testing scenarios and datasets

## Running Tests

### Quick Start

```bash
# Run all unit tests (fast feedback)
./scripts/run_tests.sh --unit

# Run full test suite
./scripts/run_tests.sh --all

# Run specific categories
./scripts/run_tests.sh --integration --security
```

### Test Runner Options

```bash
./scripts/run_tests.sh [options]

Options:
  --unit         Run unit tests (default)
  --integration  Run integration tests  
  --security     Run security tests
  --performance  Run performance tests
  --docker       Run Docker tests
  --all          Run all test categories
  --fast         Run only unit tests (fast feedback)
  --ci           Run CI test suite (unit + integration + security + docker)
```

### Manual Pytest Execution

```bash
# Unit tests with coverage
pytest tests/unit/ --cov=src --cov-report=html

# Integration tests with services
pytest tests/integration/ --marker=integration

# Security tests
pytest tests/security/ --marker=security

# Performance benchmarks
pytest tests/performance/ --marker=performance --benchmark-json=results.json

# Docker tests
pytest tests/docker/ --marker=docker
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

Key configuration options:
- **Coverage**: Minimum 90% coverage requirement
- **Markers**: Test categorization and filtering
- **Async Support**: Full asyncio test support
- **Reporting**: HTML, XML, and terminal coverage reports
- **Timeouts**: Prevent hanging tests
- **Logging**: Comprehensive test logging

### Environment Variables

Tests use these environment variables:
```bash
TESTING=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///test.db
ENCRYPTION_KEY=test-encryption-key-for-testing-only
VECTOR_STORE_PATH=tests/tmp/vectors
CACHE_SIZE=100
```

## Continuous Integration

### GitHub Actions Workflow

The CI pipeline includes:

1. **Unit Tests**: Run on Python 3.9, 3.10, 3.11
2. **Integration Tests**: With PostgreSQL and ChromaDB services
3. **Security Tests**: Including Bandit and Safety scans
4. **Performance Tests**: Benchmark validation on main branch
5. **Docker Tests**: Container build and deployment validation
6. **Coverage Reporting**: Combined coverage reports and PR comments

### CI Triggers

- **Push to main/develop**: Full test suite
- **Pull Requests**: Unit + Integration + Security + Docker tests
- **Nightly Schedule**: Complete test suite with performance tests
- **Manual Dispatch**: On-demand test execution

## Test Development Guidelines

### London School TDD Principles

1. **Start with Acceptance Tests**: Define behavior from the outside
2. **Mock External Dependencies**: Isolate units under test
3. **Verify Interactions**: Test how objects collaborate
4. **Define Contracts**: Use mocks to establish clear interfaces

### Example Test Structure

```python
@pytest.mark.unit
class TestServiceInteractions:
    """Test how Service collaborates with its dependencies."""
    
    @pytest.fixture
    def service_with_mocks(self, mock_dependency):
        """Create service with mocked dependencies."""
        return Service(mock_dependency)
    
    async def test_operation_coordinates_with_dependency(self, service_with_mocks, mock_dependency):
        """Test that operation follows proper collaboration sequence."""
        # Arrange
        expected_data = {"key": "value"}
        mock_dependency.process.return_value = expected_data
        
        # Act
        result = await service_with_mocks.perform_operation(input_data)
        
        # Assert - Focus on behavior and interactions
        mock_dependency.process.assert_called_once_with(input_data)
        assert result == expected_data
```

### Swarm Coordination Testing

```python
async def test_swarm_coordination(self, service, swarm_coordinator):
    """Test service coordination with swarm agents."""
    # Act
    result = await service.coordinate_with_swarm(task)
    
    # Log swarm interaction
    swarm_coordinator.log_interaction(
        "ServiceA", "ServiceB", "coordinate", task
    )
    
    # Verify coordination
    assert swarm_coordinator.verify_interaction_sequence(expected_sequence)
```

## Performance Requirements

### Latency Targets
- **Memory Addition**: < 500ms average
- **Search Operations**: < 500ms average  
- **API Endpoints**: < 500ms p95
- **Database Operations**: < 100ms average

### Throughput Targets
- **Concurrent Users**: 100 concurrent users
- **Operations per Second**: 100+ ops/sec
- **Search Queries**: 75+ queries/sec

### Resource Limits
- **Memory Usage**: < 2GB peak
- **CPU Usage**: < 80% under load
- **Disk I/O**: < 90% utilization
- **Network**: < 90% bandwidth utilization

## Security Test Coverage

### Input Validation
- SQL Injection prevention
- Cross-Site Scripting (XSS) prevention
- Command Injection prevention
- Buffer overflow protection
- Unicode normalization attacks

### Encryption Validation
- Key strength verification (256-bit minimum)
- Randomness quality testing
- Timing attack resistance
- Key derivation security (PBKDF2/Argon2)
- Secure key storage validation

### API Security
- Rate limiting enforcement
- Authentication bypass prevention
- Authorization escalation prevention
- CORS policy validation
- CSRF protection verification

### Data Protection
- Data-at-rest encryption (AES-256)
- Data-in-transit protection (TLS 1.2+)
- PII handling compliance
- Secure deletion verification
- Audit logging validation

## Troubleshooting

### Common Test Issues

1. **Service Connection Failures**
   ```bash
   # Start required services
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=test postgres:15
   docker run -d -p 8080:8000 chromadb/chroma:latest
   ```

2. **Coverage Below Threshold**
   ```bash
   # Run with detailed coverage report
   pytest --cov=src --cov-report=term-missing --cov-fail-under=90
   ```

3. **Slow Performance Tests**
   ```bash
   # Run performance tests with profiling
   pytest tests/performance/ --profile --profile-svg
   ```

4. **Docker Test Failures**
   ```bash
   # Rebuild test image
   docker build -t memorylink:test .
   # Clean up test containers
   docker system prune -f
   ```

### Debug Mode

Enable debug mode for detailed test output:
```bash
pytest -v --tb=long --capture=no --log-cli-level=DEBUG
```

## Test Metrics and Reporting

### Coverage Reporting
- **HTML Report**: `coverage/index.html`
- **XML Report**: `coverage.xml` (for CI)
- **Terminal Report**: Real-time coverage display

### Performance Reporting
- **Benchmark JSON**: Detailed performance metrics
- **Histograms**: Performance distribution graphs
- **Regression Detection**: Automatic performance regression alerts

### Security Reporting
- **Bandit Report**: Security vulnerability scan results
- **Safety Report**: Dependency vulnerability assessment
- **Custom Security Tests**: Application-specific security validation

This comprehensive test suite ensures MemoryLink maintains high quality, security, and performance standards while supporting collaborative development through swarm coordination patterns.