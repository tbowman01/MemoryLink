# MemoryLink Data Models Specification

## Overview
This document defines the data models and database schema for MemoryLink MVP, ensuring consistency across API, storage, and vector search components.

## Core Data Models

### 1. MemoryEntry Model

#### Pydantic Schema
```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryEntry(BaseModel):
    id: str = Field(..., description="Unique memory identifier (UUID)")
    text: str = Field(..., min_length=1, max_length=10000, description="Memory content")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    timestamp: datetime = Field(..., description="Memory timestamp")
    user: str = Field(default="default", description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
```

#### Database Schema (SQLite)
```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    text_encrypted TEXT NOT NULL,
    tags JSON,
    timestamp DATETIME NOT NULL,
    user_id TEXT NOT NULL DEFAULT 'default',
    metadata JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_memories_timestamp ON memories(timestamp),
    INDEX idx_memories_user ON memories(user_id),
    INDEX idx_memories_created_at ON memories(created_at)
);

-- Tags table for normalized tag storage (optional optimization)
CREATE TABLE memory_tags (
    memory_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    
    PRIMARY KEY (memory_id, tag),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
    INDEX idx_tags_tag ON memory_tags(tag)
);

-- Metadata table for searchable metadata (optional optimization)
CREATE TABLE memory_metadata (
    memory_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    
    PRIMARY KEY (memory_id, key),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
    INDEX idx_metadata_key ON memory_metadata(key)
);
```

### 2. Vector Embedding Model

#### ChromaDB Collection Schema
```python
# ChromaDB collection configuration
collection_config = {
    "name": "memory_embeddings",
    "metadata": {
        "description": "Memory text embeddings for semantic search",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "dimensions": 384
    }
}

# Document structure in ChromaDB
class VectorDocument:
    id: str              # Same as MemoryEntry.id
    embedding: List[float]  # 384-dimensional vector
    metadata: Dict = {
        "memory_id": str,    # Reference to memories table
        "user_id": str,      # For user-scoped search
        "timestamp": str,    # ISO format for temporal search
        "tags": List[str],   # For tag filtering in vector search
    }
    document: str        # Original text for result display
```

### 3. Request/Response Models

#### Add Memory Request
```python
class AddMemoryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    tags: Optional[List[str]] = Field(default=None, max_items=20)
    user: Optional[str] = Field(default="default", max_length=100)
    timestamp: Optional[datetime] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag.strip()) == 0:
                    raise ValueError("Empty tags not allowed")
                if len(tag) > 50:
                    raise ValueError("Tag too long (max 50 characters)")
        return [tag.strip() for tag in v] if v else []
```

#### Search Memory Request
```python
class SearchMemoryRequest(BaseModel):
    query: Optional[str] = Field(default=None, max_length=1000)
    tags: Optional[List[str]] = Field(default=None)
    user: Optional[str] = Field(default=None)
    since: Optional[datetime] = Field(default=None)
    until: Optional[datetime] = Field(default=None)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    
    @validator('query')
    def validate_query(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v.strip() if v else None
```

#### Search Response Models
```python
class MemorySearchResult(BaseModel):
    id: str
    text: str
    tags: List[str]
    timestamp: datetime
    user: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class SearchMemoryResponse(BaseModel):
    results: List[MemorySearchResult]
    total_found: int
    query_processed: Optional[str]
    processing_time_ms: int
    has_more: bool
    pagination: Dict[str, int] = Field(default_factory=lambda: {"limit": 10, "offset": 0})
```

### 4. Configuration Models

#### Application Configuration
```python
class MemoryLinkConfig(BaseModel):
    # Database settings
    database_url: str = "sqlite:///data/memorylink.db"
    vector_store_type: str = "chromadb"  # or "qdrant"
    vector_store_path: str = "data/vectors"
    
    # Encryption settings
    encryption_enabled: bool = True
    encryption_key_source: str = "env"  # "env", "file", "prompt"
    encryption_key: Optional[str] = None
    
    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32
    
    # API settings
    host: str = "localhost"
    port: int = 8080
    api_key_required: bool = False
    api_key: Optional[str] = None
    
    # Performance settings
    max_content_length: int = 10000
    search_timeout_ms: int = 5000
    embedding_timeout_ms: int = 10000
    
    # Development settings
    debug: bool = False
    log_level: str = "INFO"
    enable_cors: bool = True
```

### 5. Error Models

#### Standard Error Response
```python
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    constraint: Optional[str] = None
    value: Optional[Any] = None

class ErrorResponse(BaseModel):
    error: Dict[str, Any] = Field(..., description="Error information")
    
    @classmethod
    def create(cls, code: str, message: str, details: Optional[Dict] = None):
        return cls(error={
            "code": code,
            "message": message,
            "details": details or {}
        })

# Common error codes
class ErrorCodes:
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    ENCRYPTION_ERROR = "ENCRYPTION_ERROR"
    VECTOR_SEARCH_ERROR = "VECTOR_SEARCH_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED = "UNAUTHORIZED"
```

## Database Relationships

### Entity Relationship Diagram
```
memories (1) ←→ (N) memory_tags
memories (1) ←→ (N) memory_metadata
memories (1) ←→ (1) vector_embeddings [via ChromaDB]

User Scope:
  user_id → [memories] → [embeddings with user metadata]
```

### Indexes and Performance

#### Required Indexes
```sql
-- Primary lookup indexes
CREATE INDEX idx_memories_id ON memories(id);
CREATE INDEX idx_memories_user_timestamp ON memories(user_id, timestamp DESC);
CREATE INDEX idx_memories_created_at ON memories(created_at DESC);

-- Search optimization indexes  
CREATE INDEX idx_memory_tags_tag ON memory_tags(tag);
CREATE INDEX idx_memory_tags_memory_tag ON memory_tags(memory_id, tag);
CREATE INDEX idx_memory_metadata_key_value ON memory_metadata(key, value);
```

#### Vector Index Configuration
```python
# ChromaDB index settings
chroma_settings = {
    "anonymized_telemetry": False,
    "allow_reset": True,
    "is_persistent": True,
    "persist_directory": "data/vectors"
}

# Vector search parameters
vector_search_config = {
    "n_results": 20,  # Internal limit before filtering
    "include": ["documents", "metadatas", "distances"],
    "where": {},      # Metadata filtering
    "where_document": {}  # Document content filtering
}
```

## Data Validation Rules

### Text Content Validation
- **Length**: 1-10,000 characters
- **Encoding**: UTF-8 required
- **Sanitization**: HTML/script tag removal
- **Whitespace**: Leading/trailing whitespace trimmed

### Tag Validation
- **Format**: Alphanumeric plus hyphens, underscores
- **Length**: 1-50 characters per tag
- **Count**: Maximum 20 tags per memory
- **Normalization**: Lowercase, trimmed

### Timestamp Validation
- **Format**: ISO 8601 with timezone
- **Range**: Not more than 1 year in future
- **Default**: Current UTC time if not provided

### User ID Validation
- **Format**: Alphanumeric plus hyphens, underscores, dots
- **Length**: 1-100 characters
- **Default**: "default" for MVP single-user mode

### Metadata Validation
- **Size**: Maximum 1KB JSON serialized
- **Depth**: Maximum 3 levels nested
- **Keys**: String keys only, no special characters
- **Values**: Strings, numbers, booleans, arrays (no objects)

## Data Migration Strategy

### Version 1.0 Schema
Current MVP schema as defined above.

### Future Migration Considerations
```python
class SchemaMigration:
    def __init__(self, from_version: str, to_version: str):
        self.from_version = from_version
        self.to_version = to_version
    
    def migrate_memories_v1_to_v2(self):
        """Example: Add new fields or change existing ones"""
        pass
    
    def migrate_vectors_v1_to_v2(self):
        """Example: Re-embed with new model"""
        pass
```

### Backup Strategy
- **SQLite**: File-based backup before migrations
- **ChromaDB**: Export collections before schema changes
- **Rollback**: Keep previous version data until migration verified

## Performance Considerations

### Expected Data Volumes (MVP)
- **Memory Entries**: 1-10,000 per user
- **Average Text Length**: 100-1,000 characters
- **Tags per Memory**: 1-5 average
- **Metadata Size**: 50-200 bytes average

### Query Performance Targets
- **Memory Insert**: < 2 seconds (including embedding)
- **Vector Search**: < 500ms for 10,000 entries
- **Metadata Filter**: < 100ms
- **Combined Search**: < 500ms total

### Storage Estimates
- **Text Storage**: ~1MB per 1,000 memories (encrypted)
- **Vector Storage**: ~1.5MB per 1,000 memories (384-dim floats)
- **Metadata/Tags**: ~100KB per 1,000 memories
- **Total**: ~2.6MB per 1,000 memories

This data model specification provides the foundation for consistent implementation across all MemoryLink components, ensuring data integrity, performance, and extensibility for future enhancements.