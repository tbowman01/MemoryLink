"""Vector storage service using ChromaDB."""

import uuid
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from ..utils.logger import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class VectorStore:
    """Service for storing and searching vector embeddings."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.settings = get_settings()
        self._client = None
        self._collection = None
    
    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        if self._client is None:
            logger.info(f"Initializing ChromaDB at {self.settings.chroma_db_path}")
            
            # Configure ChromaDB settings
            chroma_settings = ChromaSettings(
                persist_directory=self.settings.chroma_db_path,
                is_persistent=True,
                allow_reset=True
            )
            
            self._client = chromadb.Client(chroma_settings)
            
            # Get or create collection
            try:
                self._collection = self._client.get_collection(
                    name=self.settings.chroma_collection_name
                )
                logger.info(f"Using existing collection: {self.settings.chroma_collection_name}")
            except ValueError:
                # Collection doesn't exist, create it
                self._collection = self._client.create_collection(
                    name=self.settings.chroma_collection_name,
                    metadata={"description": "MemoryLink embeddings"}
                )
                logger.info(f"Created new collection: {self.settings.chroma_collection_name}")
    
    async def add_memory(
        self, 
        memory_id: str, 
        embedding: List[float], 
        text: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Add a memory with its embedding to the vector store."""
        await self.initialize()
        
        try:
            # Prepare metadata (ChromaDB requires string values)
            chroma_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    chroma_metadata[key] = str(value)
                elif isinstance(value, list):
                    chroma_metadata[key] = ','.join(str(v) for v in value)
                else:
                    chroma_metadata[key] = str(value)
            
            self._collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[chroma_metadata]
            )
            
            logger.debug(f"Added memory {memory_id} to vector store")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add memory to vector store: {str(e)}")
            raise ValueError(f"Failed to store memory: {str(e)}")
    
    async def search_memories(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.5,
        user_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None
    ) -> List[Tuple[str, float, str, Dict[str, Any]]]:
        """Search for similar memories."""
        await self.initialize()
        
        try:
            # Build where clause for filtering
            where_clause = {}
            if user_filter:
                where_clause["user_id"] = user_filter
            
            if tag_filter:
                # For tag filtering, we'll need to check if any of the tags match
                # ChromaDB doesn't support array operations directly, so we'll filter post-query
                pass
            
            # Perform the search
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # Get more to allow for filtering
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            memories = []
            if results['ids'] and results['ids'][0]:
                for i, memory_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0
                    # Convert distance to similarity score (closer to 0 = more similar)
                    similarity = 1.0 - min(distance, 1.0)
                    
                    if similarity < min_similarity:
                        continue
                    
                    document = results['documents'][0][i] if results['documents'] else ""
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    # Convert metadata back from strings
                    processed_metadata = self._process_metadata(metadata)
                    
                    # Filter by tags if specified
                    if tag_filter:
                        memory_tags = processed_metadata.get('tags', [])
                        if isinstance(memory_tags, str):
                            memory_tags = memory_tags.split(',')
                        
                        if not any(tag in memory_tags for tag in tag_filter):
                            continue
                    
                    memories.append((memory_id, similarity, document, processed_metadata))
            
            # Sort by similarity and limit results
            memories.sort(key=lambda x: x[1], reverse=True)
            memories = memories[:limit]
            
            logger.debug(f"Found {len(memories)} similar memories")
            return memories
        
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            raise ValueError(f"Failed to search memories: {str(e)}")
    
    async def get_memory(self, memory_id: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get a specific memory by ID."""
        await self.initialize()
        
        try:
            results = self._collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )
            
            if results['ids'] and results['ids'][0]:
                document = results['documents'][0] if results['documents'] else ""
                metadata = results['metadatas'][0] if results['metadatas'] else {}
                processed_metadata = self._process_metadata(metadata)
                return document, processed_metadata
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {str(e)}")
            return None
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from the vector store."""
        await self.initialize()
        
        try:
            self._collection.delete(ids=[memory_id])
            logger.debug(f"Deleted memory {memory_id} from vector store")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        await self.initialize()
        
        try:
            count = self._collection.count()
            return {
                "total_memories": count,
                "collection_name": self.settings.chroma_collection_name,
                "embedding_dimension": self.settings.embedding_dimension
            }
        
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}
    
    def _process_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process metadata from ChromaDB format back to original format."""
        processed = {}
        
        for key, value in metadata.items():
            if key == 'tags' and isinstance(value, str):
                processed[key] = [tag.strip() for tag in value.split(',') if tag.strip()]
            elif key == 'timestamp':
                processed[key] = value  # Keep as string for now
            else:
                processed[key] = value
        
        return processed