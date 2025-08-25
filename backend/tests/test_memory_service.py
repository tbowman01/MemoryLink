"""Tests for memory service."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.services.memory_service import MemoryService
from src.models.memory_models import AddMemoryRequest, SearchMemoryRequest, MemoryEntry
from src.utils.encryption import EncryptionService


@pytest.fixture
def memory_service():
    """Create a memory service instance for testing."""
    with patch('src.services.memory_service.get_settings') as mock_settings:
        mock_settings.return_value.encryption_key = "test-key-for-encryption"
        mock_settings.return_value.embedding_model = "all-MiniLM-L6-v2"
        mock_settings.return_value.embedding_dimension = 384
        mock_settings.return_value.app_version = "1.0.0"
        
        service = MemoryService()
        service.embedding_service = AsyncMock()
        service.vector_store = AsyncMock()
        
        return service


@pytest.mark.asyncio
async def test_add_memory_success(memory_service):
    """Test successful memory addition."""
    # Mock dependencies
    memory_service.embedding_service.encode_text.return_value = [0.1] * 384
    memory_service.vector_store.add_memory.return_value = True
    
    # Create request
    request = AddMemoryRequest(
        text="Test memory content",
        tags=["test", "memory"],
        user_id="user123"
    )
    
    # Add memory
    result = await memory_service.add_memory(request)
    
    # Assertions
    assert isinstance(result, MemoryEntry)
    assert result.text == "Test memory content"
    assert result.tags == ["test", "memory"]
    assert result.user_id == "user123"
    assert result.id is not None
    
    # Verify service calls
    memory_service.embedding_service.encode_text.assert_called_once_with("Test memory content")
    memory_service.vector_store.add_memory.assert_called_once()


@pytest.mark.asyncio
async def test_search_memories_success(memory_service):
    """Test successful memory search."""
    # Mock dependencies
    memory_service.embedding_service.encode_text.return_value = [0.1] * 384
    memory_service.vector_store.search_memories.return_value = [
        ("mem1", 0.95, "encrypted_text1", {
            "user_id": "user123",
            "tags": ["test"],
            "timestamp": datetime.utcnow().isoformat()
        }),
        ("mem2", 0.85, "encrypted_text2", {
            "user_id": "user123", 
            "tags": ["memory"],
            "timestamp": datetime.utcnow().isoformat()
        })
    ]
    
    # Mock decryption
    with patch.object(memory_service.encryption_service, 'decrypt') as mock_decrypt:
        mock_decrypt.side_effect = ["Decrypted text 1", "Decrypted text 2"]
        
        # Create request
        request = SearchMemoryRequest(
            query="test query",
            user_id="user123",
            limit=10
        )
        
        # Search memories
        results = await memory_service.search_memories(request)
        
        # Assertions
        assert len(results) == 2
        assert results[0].id == "mem1"
        assert results[0].text == "Decrypted text 1"
        assert results[0].similarity_score == 0.95
        assert results[1].id == "mem2"
        assert results[1].text == "Decrypted text 2"
        assert results[1].similarity_score == 0.85


@pytest.mark.asyncio
async def test_add_memory_embedding_failure(memory_service):
    """Test memory addition with embedding failure."""
    # Mock embedding failure
    memory_service.embedding_service.encode_text.side_effect = ValueError("Embedding failed")
    
    # Create request
    request = AddMemoryRequest(
        text="Test memory content",
        tags=["test"],
        user_id="user123"
    )
    
    # Test that exception is raised
    with pytest.raises(ValueError, match="Failed to add memory"):
        await memory_service.add_memory(request)


@pytest.mark.asyncio
async def test_search_memories_empty_query(memory_service):
    """Test search with empty query."""
    # Mock dependencies
    memory_service.embedding_service.encode_text.side_effect = ValueError("Text cannot be empty")
    
    # Create request with empty query
    request = SearchMemoryRequest(
        query="",
        user_id="user123"
    )
    
    # Test that exception is raised
    with pytest.raises(ValueError):
        await memory_service.search_memories(request)