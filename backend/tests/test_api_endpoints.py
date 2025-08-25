"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.models.memory_models import MemoryEntry, MemorySearchResult
from datetime import datetime


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_memory_service():
    """Create a mock memory service."""
    return AsyncMock()


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "status" in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data


@patch('src.api.memory_routes.get_memory_service')
def test_add_memory_success(mock_get_service, client):
    """Test successful memory addition."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    
    # Mock memory entry response
    mock_memory = MemoryEntry(
        id="test-id-123",
        text="Test memory content",
        tags=["test"],
        timestamp=datetime.utcnow(),
        user_id="user123"
    )
    mock_service.add_memory.return_value = mock_memory
    
    # Make request
    response = client.post("/memory/add", json={
        "text": "Test memory content",
        "tags": ["test"],
        "user_id": "user123"
    })
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id-123"
    assert data["message"] == "Memory added successfully"


@patch('src.api.memory_routes.get_memory_service')
def test_add_memory_validation_error(mock_get_service, client):
    """Test memory addition with validation error."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    mock_service.add_memory.side_effect = ValueError("Text cannot be empty")
    
    # Make request with empty text
    response = client.post("/memory/add", json={
        "text": "",
        "user_id": "user123"
    })
    
    # Should fail at pydantic validation level
    assert response.status_code == 422


@patch('src.api.memory_routes.get_memory_service')
def test_search_memories_success(mock_get_service, client):
    """Test successful memory search."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    
    # Mock search results
    mock_results = [
        MemorySearchResult(
            id="mem1",
            text="Found memory 1",
            tags=["test"],
            timestamp=datetime.utcnow(),
            similarity_score=0.95
        ),
        MemorySearchResult(
            id="mem2", 
            text="Found memory 2",
            tags=["memory"],
            timestamp=datetime.utcnow(),
            similarity_score=0.85
        )
    ]
    mock_service.search_memories.return_value = mock_results
    
    # Make request
    response = client.post("/memory/search", json={
        "query": "test search",
        "user_id": "user123",
        "limit": 10
    })
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test search"
    assert len(data["results"]) == 2
    assert data["total_found"] == 2
    assert data["results"][0]["id"] == "mem1"
    assert data["results"][0]["similarity_score"] == 0.95


@patch('src.api.memory_routes.get_memory_service')
def test_search_memories_empty_query(mock_get_service, client):
    """Test search with empty query."""
    # Make request with empty query
    response = client.post("/memory/search", json={
        "query": "",
        "user_id": "user123"
    })
    
    # Should fail at pydantic validation level
    assert response.status_code == 422


@patch('src.api.memory_routes.get_memory_service')
def test_get_memory_success(mock_get_service, client):
    """Test successful memory retrieval."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    
    # Mock memory response
    mock_memory = MemoryEntry(
        id="mem123",
        text="Retrieved memory",
        tags=["test"],
        timestamp=datetime.utcnow(),
        user_id="user123"
    )
    mock_service.get_memory.return_value = mock_memory
    
    # Make request
    response = client.get("/memory/mem123?user_id=user123")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mem123"
    assert data["text"] == "Retrieved memory"


@patch('src.api.memory_routes.get_memory_service')
def test_get_memory_not_found(mock_get_service, client):
    """Test memory retrieval when not found."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    mock_service.get_memory.return_value = None
    
    # Make request
    response = client.get("/memory/nonexistent?user_id=user123")
    
    # Assertions
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "Memory not found or access denied"


@patch('src.api.memory_routes.get_memory_service') 
def test_delete_memory_success(mock_get_service, client):
    """Test successful memory deletion."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    mock_service.delete_memory.return_value = True
    
    # Make request
    response = client.delete("/memory/mem123?user_id=user123")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Memory deleted successfully"
    assert data["memory_id"] == "mem123"


@patch('src.api.memory_routes.get_memory_service')
def test_get_user_memory_count(mock_get_service, client):
    """Test getting user memory count."""
    # Mock service
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    mock_service.get_user_memories_count.return_value = 42
    
    # Make request
    response = client.get("/memory/user/user123/count")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user123"
    assert data["memory_count"] == 42