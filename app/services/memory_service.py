"""Core memory service for business logic."""

import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.memory_models import (
    MemoryEntry, 
    AddMemoryRequest, 
    SearchMemoryRequest, 
    MemorySearchResult
)
from ..utils.encryption import EncryptionService
from ..utils.logger import get_logger
from ..config import get_settings
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

logger = get_logger(__name__)


class MemoryService:
    """Core service for memory operations."""
    
    def __init__(self):
        """Initialize the memory service."""
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.encryption_service = EncryptionService(self.settings.encryption_key)
    
    async def initialize(self):
        """Initialize all dependent services."""
        await self.vector_store.initialize()
        logger.info("Memory service initialized successfully")
    
    async def add_memory(self, request: AddMemoryRequest) -> MemoryEntry:
        """Add a new memory."""
        start_time = time.time()
        
        try:
            # Generate unique ID
            memory_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Create memory entry
            memory_entry = MemoryEntry(
                id=memory_id,
                text=request.text,
                tags=request.tags,
                timestamp=timestamp,
                user_id=request.user_id,
                metadata=request.metadata
            )
            
            # Generate embedding for the text
            logger.debug(f"Generating embedding for memory {memory_id}")
            embedding = await self.embedding_service.encode_text(request.text)
            
            # Prepare metadata for storage
            storage_metadata = {
                "user_id": request.user_id,
                "tags": request.tags,
                "timestamp": timestamp.isoformat(),
                **request.metadata
            }
            
            # Encrypt the text content
            encrypted_text = self.encryption_service.encrypt(request.text)
            
            # Store in vector database
            await self.vector_store.add_memory(
                memory_id=memory_id,
                embedding=embedding,
                text=encrypted_text,  # Store encrypted text
                metadata=storage_metadata
            )
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Added memory {memory_id} in {processing_time:.2f}ms")
            
            return memory_entry
        
        except Exception as e:
            logger.error(f"Failed to add memory: {str(e)}")
            raise ValueError(f"Failed to add memory: {str(e)}")
    
    async def search_memories(self, request: SearchMemoryRequest) -> List[MemorySearchResult]:
        """Search for memories based on semantic similarity."""
        start_time = time.time()
        
        try:
            # Generate embedding for the search query
            logger.debug(f"Generating embedding for query: {request.query[:50]}...")
            query_embedding = await self.embedding_service.encode_text(request.query)
            
            # Search in vector store
            results = await self.vector_store.search_memories(
                query_embedding=query_embedding,
                limit=request.limit,
                min_similarity=request.min_similarity,
                user_filter=request.user_id,
                tag_filter=request.tags
            )
            
            # Process and decrypt results
            search_results = []
            for memory_id, similarity, encrypted_text, metadata in results:
                try:
                    # Decrypt the text content
                    decrypted_text = self.encryption_service.decrypt(encrypted_text)
                    
                    # Parse timestamp
                    timestamp = datetime.fromisoformat(metadata.get('timestamp', datetime.utcnow().isoformat()))
                    
                    # Extract tags
                    tags = metadata.get('tags', [])
                    if isinstance(tags, str):
                        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    
                    # Create search result
                    result = MemorySearchResult(
                        id=memory_id,
                        text=decrypted_text,
                        tags=tags,
                        timestamp=timestamp,
                        similarity_score=round(similarity, 4),
                        metadata={k: v for k, v in metadata.items() if k not in ['user_id', 'tags', 'timestamp']}
                    )
                    
                    search_results.append(result)
                
                except Exception as decrypt_error:
                    logger.error(f"Failed to decrypt memory {memory_id}: {str(decrypt_error)}")
                    # Skip this result rather than failing the entire search
                    continue
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Search completed in {processing_time:.2f}ms, found {len(search_results)} results")
            
            return search_results
        
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            raise ValueError(f"Failed to search memories: {str(e)}")
    
    async def get_memory(self, memory_id: str, user_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID."""
        try:
            result = await self.vector_store.get_memory(memory_id)
            
            if not result:
                return None
            
            encrypted_text, metadata = result
            
            # Check if user owns this memory
            if metadata.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to access memory {memory_id} owned by {metadata.get('user_id')}")
                return None
            
            # Decrypt the text content
            decrypted_text = self.encryption_service.decrypt(encrypted_text)
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(metadata.get('timestamp', datetime.utcnow().isoformat()))
            
            # Extract tags
            tags = metadata.get('tags', [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Create memory entry
            memory_entry = MemoryEntry(
                id=memory_id,
                text=decrypted_text,
                tags=tags,
                timestamp=timestamp,
                user_id=user_id,
                metadata={k: v for k, v in metadata.items() if k not in ['user_id', 'tags', 'timestamp']}
            )
            
            return memory_entry
        
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {str(e)}")
            return None
    
    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete a memory."""
        try:
            # First check if memory exists and user owns it
            memory = await self.get_memory(memory_id, user_id)
            if not memory:
                return False
            
            # Delete from vector store
            success = await self.vector_store.delete_memory(memory_id)
            
            if success:
                logger.info(f"Deleted memory {memory_id} for user {user_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {str(e)}")
            return False
    
    async def get_user_memories_count(self, user_id: str) -> int:
        """Get the count of memories for a user."""
        try:
            # This is a simplified implementation
            # In a production system, you might want a more efficient way to count
            search_request = SearchMemoryRequest(
                query="",  # Empty query to get all
                user_id=user_id,
                limit=1,
                min_similarity=0.0
            )
            
            stats = await self.vector_store.get_collection_stats()
            return stats.get('total_memories', 0)
        
        except Exception as e:
            logger.error(f"Failed to get memories count for user {user_id}: {str(e)}")
            return 0
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory service."""
        try:
            vector_stats = await self.vector_store.get_collection_stats()
            
            return {
                "service_name": "MemoryLink Memory Service",
                "version": self.settings.app_version,
                "embedding_model": self.settings.embedding_model,
                "embedding_dimension": self.settings.embedding_dimension,
                **vector_stats,
                "encryption_enabled": True
            }
        
        except Exception as e:
            logger.error(f"Failed to get service stats: {str(e)}")
            return {"error": str(e)}