"""Application settings and configuration."""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Configuration
    app_name: str = "MemoryLink Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Security Configuration
    encryption_key: Optional[str] = None
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database Configuration
    chroma_db_path: str = "./data/chromadb"
    chroma_collection_name: str = "memory_embeddings"
    
    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Search Configuration
    default_search_limit: int = 10
    max_search_limit: int = 100
    min_similarity_threshold: float = 0.3
    
    # Performance Configuration
    max_content_length: int = 10000
    request_timeout: int = 30
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('encryption_key')
    def validate_encryption_key(cls, v):
        """Validate or generate encryption key."""
        if not v:
            # Generate a default key for development (NOT for production)
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    @validator('chroma_db_path')
    def validate_db_path(cls, v):
        """Ensure database directory exists."""
        os.makedirs(v, exist_ok=True)
        return v
    
    @validator('allowed_origins')
    def validate_origins(cls, v):
        """Ensure origins are valid."""
        return [origin.rstrip('/') for origin in v]


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()