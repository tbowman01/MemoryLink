"""Embedding service for converting text to vectors."""

import asyncio
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from ..utils.logger import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.settings = get_settings()
        self._model = None
        self._lock = asyncio.Lock()
    
    async def _ensure_model_loaded(self):
        """Ensure the embedding model is loaded."""
        if self._model is None:
            async with self._lock:
                if self._model is None:
                    logger.info(f"Loading embedding model: {self.settings.embedding_model}")
                    # Run in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    self._model = await loop.run_in_executor(
                        None, 
                        SentenceTransformer, 
                        self.settings.embedding_model
                    )
                    logger.info("Embedding model loaded successfully")
    
    async def encode_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        await self._ensure_model_loaded()
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            # Run encoding in thread pool
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self._model.encode(text.strip()).tolist()
            )
            
            logger.debug(f"Generated embedding of dimension {len(embedding)} for text")
            return embedding
        
        except Exception as e:
            logger.error(f"Failed to encode text: {str(e)}")
            raise ValueError(f"Failed to generate embedding: {str(e)}")
    
    async def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        await self._ensure_model_loaded()
        
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not valid_texts:
            raise ValueError("No valid texts provided")
        
        try:
            # Run batch encoding in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self._model.encode(valid_texts).tolist()
            )
            
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
        
        except Exception as e:
            logger.error(f"Failed to encode texts: {str(e)}")
            raise ValueError(f"Failed to generate embeddings: {str(e)}")
    
    async def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts."""
        embeddings = await self.encode_texts([text1, text2])
        return self._cosine_similarity(embeddings[0], embeddings[1])
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math
        
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        return self.settings.embedding_dimension