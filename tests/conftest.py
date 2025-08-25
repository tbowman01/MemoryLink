"""
Test configuration and shared fixtures for MemoryLink test suite.
Implements London School TDD approach with comprehensive mocking.
"""

import asyncio
import os
import tempfile
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List
import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Mock external dependencies
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_path():
    """Provide temporary database path for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield os.path.join(temp_dir, "test_memory.db")


@pytest.fixture
def temp_vector_store_path():
    """Provide temporary vector store path for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield os.path.join(temp_dir, "test_vectors")


@pytest.fixture
def mock_encryption_service():
    """Mock encryption service with predictable behavior."""
    mock = Mock()
    mock.encrypt.return_value = b"encrypted_data_mock"
    mock.decrypt.return_value = "decrypted_data_mock"
    mock.generate_key.return_value = b"mock_encryption_key"
    return mock


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for vector operations."""
    mock = AsyncMock()
    mock.generate_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dim vector
    mock.calculate_similarity.return_value = 0.85
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock ChromaDB vector store operations."""
    mock = Mock()
    mock.add_vectors = AsyncMock()
    mock.search = AsyncMock(return_value=[
        {"id": "test_id_1", "score": 0.9, "metadata": {"content": "test content"}},
        {"id": "test_id_2", "score": 0.8, "metadata": {"content": "related content"}}
    ])
    mock.delete = AsyncMock()
    mock.get_collection = Mock()
    return mock


@pytest.fixture
def mock_memory_service():
    """Mock memory service for API testing."""
    mock = AsyncMock()
    mock.add_memory.return_value = {
        "id": "test_memory_id",
        "content": "test content",
        "timestamp": "2024-01-01T00:00:00",
        "embedding": [0.1] * 500
    }
    mock.search_memories.return_value = [
        {
            "id": "result_1",
            "content": "matching content",
            "similarity": 0.9,
            "timestamp": "2024-01-01T00:00:00"
        }
    ]
    mock.get_memory.return_value = {
        "id": "test_memory_id",
        "content": "retrieved content",
        "timestamp": "2024-01-01T00:00:00"
    }
    return mock


@pytest.fixture
async def async_client():
    """Create async HTTP client for API testing."""
    # This will be configured once the main app is created
    return AsyncClient()


@pytest.fixture
def test_client():
    """Create sync test client for FastAPI testing."""
    # This will be configured once the main app is created
    from fastapi.testclient import TestClient
    # Note: Will need to import actual app once created
    # return TestClient(app)
    return Mock(spec=TestClient)


@pytest.fixture
def sample_memory_data():
    """Provide sample memory data for testing."""
    return {
        "valid_memory": {
            "content": "This is a test memory about machine learning algorithms",
            "tags": ["ai", "ml", "algorithms"],
            "metadata": {"importance": "high", "category": "technical"}
        },
        "minimal_memory": {
            "content": "Simple memory"
        },
        "long_memory": {
            "content": "This is a very long memory " * 100,  # ~2500 chars
            "tags": ["long", "test"]
        },
        "unicode_memory": {
            "content": "Memory with unicode: 🤖 AI 中文 français",
            "tags": ["unicode", "international"]
        }
    }


@pytest.fixture
def sample_embeddings():
    """Provide sample embedding vectors for testing."""
    return {
        "dimension_384": [0.1] * 384,
        "dimension_512": [0.2] * 512,
        "dimension_768": [0.3] * 768,
        "zero_vector": [0.0] * 384,
        "unit_vector": [1.0] + [0.0] * 383,
        "similar_vectors": {
            "vector_a": [0.1, 0.2, 0.3] * 128,
            "vector_b": [0.11, 0.21, 0.31] * 128,  # Slightly different
            "vector_c": [0.9, 0.8, 0.7] * 128      # Very different
        }
    }


@pytest.fixture
def performance_test_data():
    """Generate performance test data sets."""
    return {
        "small_dataset": [f"Memory entry {i}" for i in range(100)],
        "medium_dataset": [f"Medium memory entry {i} with more content" for i in range(1000)],
        "large_dataset": [f"Large memory entry {i} with extensive content and details" for i in range(10000)],
        "concurrent_requests": 50,
        "latency_threshold_ms": 500,
        "throughput_target_rps": 100
    }


@pytest.fixture
def security_test_vectors():
    """Provide security test vectors and attack patterns."""
    return {
        "sql_injection": [
            "'; DROP TABLE memories; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--"
        ],
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;"
        ],
        "large_payloads": {
            "max_content_size": "x" * 100000,  # 100KB
            "max_tag_count": ["tag"] * 1000,
            "deeply_nested": {"level": {"nested": {"data": "value"}}}
        },
        "encryption_test_data": [
            b"sensitive information",
            b"",  # Empty data
            b"\x00\x01\x02\x03",  # Binary data
            "unicode data: 🔒".encode('utf-8')
        ]
    }


@pytest.fixture
def mock_docker_client():
    """Mock Docker client for container testing."""
    mock = Mock()
    mock.containers = Mock()
    mock.images = Mock()
    mock.networks = Mock()
    mock.volumes = Mock()
    
    # Mock container operations
    mock_container = Mock()
    mock_container.status = "running"
    mock_container.attrs = {"State": {"Health": {"Status": "healthy"}}}
    mock_container.logs.return_value = b"Container started successfully"
    mock_container.exec_run.return_value = Mock(exit_code=0, output=b"Service healthy")
    
    mock.containers.get.return_value = mock_container
    mock.containers.run.return_value = mock_container
    mock.containers.list.return_value = [mock_container]
    
    return mock


class SwarmTestCoordinator:
    """Coordinate tests across swarm agents using London School patterns."""
    
    def __init__(self):
        self.test_results = {}
        self.mock_contracts = {}
        self.interaction_logs = []
    
    def register_mock_contract(self, service_name: str, contract: Dict[str, Any]):
        """Register mock contract for swarm coordination."""
        self.mock_contracts[service_name] = contract
    
    def log_interaction(self, from_service: str, to_service: str, method: str, args: Any):
        """Log interaction between services for verification."""
        self.interaction_logs.append({
            "from": from_service,
            "to": to_service,
            "method": method,
            "args": args,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def verify_interaction_sequence(self, expected_sequence: List[Dict[str, Any]]) -> bool:
        """Verify that interactions occurred in expected sequence."""
        if len(self.interaction_logs) < len(expected_sequence):
            return False
        
        for i, expected in enumerate(expected_sequence):
            actual = self.interaction_logs[i]
            if (actual["from"] != expected["from"] or 
                actual["to"] != expected["to"] or 
                actual["method"] != expected["method"]):
                return False
        
        return True


@pytest.fixture
def swarm_coordinator():
    """Provide swarm test coordinator for distributed testing."""
    return SwarmTestCoordinator()


# Async fixtures for London School TDD patterns
@pytest_asyncio.fixture
async def memory_service_with_mocks(mock_encryption_service, mock_embedding_service, mock_vector_store):
    """Create memory service with all dependencies mocked."""
    # This will be implemented once MemoryService is created
    # For now, return a mock that satisfies the contract
    mock = AsyncMock()
    mock.encryption_service = mock_encryption_service
    mock.embedding_service = mock_embedding_service
    mock.vector_store = mock_vector_store
    return mock


# Test markers for categorization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.security = pytest.mark.security
pytest.mark.performance = pytest.mark.performance
pytest.mark.docker = pytest.mark.docker
pytest.mark.slow = pytest.mark.slow


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "docker: Docker tests")
    config.addinivalue_line("markers", "slow: Slow running tests")