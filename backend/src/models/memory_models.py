"""Pydantic models for MemoryLink API."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class MemoryEntry(BaseModel):
    """Core memory entry model."""
    
    id: str = Field(..., description="Unique identifier for the memory")
    text: str = Field(..., description="The memory content", max_length=10000)
    tags: List[str] = Field(default_factory=list, description="Tags associated with the memory")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the memory was created")
    user_id: str = Field(..., description="ID of the user who owns this memory")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags are non-empty strings."""
        if v:
            v = [tag.strip().lower() for tag in v if tag and tag.strip()]
        return v
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text is not empty."""
        if not v or not v.strip():
            raise ValueError("Memory text cannot be empty")
        return v.strip()


class AddMemoryRequest(BaseModel):
    """Request model for adding a new memory."""
    
    text: str = Field(..., description="The memory content to store", max_length=10000)
    tags: List[str] = Field(default_factory=list, description="Tags to associate with the memory")
    user_id: str = Field(..., description="ID of the user adding the memory")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Clean and validate tags."""
        if v:
            v = [tag.strip().lower() for tag in v if tag and tag.strip()]
        return v
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text is not empty."""
        if not v or not v.strip():
            raise ValueError("Memory text cannot be empty")
        return v.strip()


class AddMemoryResponse(BaseModel):
    """Response model for adding a memory."""
    
    id: str = Field(..., description="The generated ID for the stored memory")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(..., description="When the memory was stored")


class MemorySearchResult(BaseModel):
    """Individual search result model."""
    
    id: str = Field(..., description="Memory ID")
    text: str = Field(..., description="Memory content")
    tags: List[str] = Field(..., description="Associated tags")
    timestamp: datetime = Field(..., description="Creation timestamp")
    similarity_score: float = Field(..., description="Similarity score (0-1)", ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchMemoryRequest(BaseModel):
    """Request model for memory search."""
    
    query: str = Field(..., description="Search query", max_length=1000)
    user_id: str = Field(..., description="ID of the user performing the search")
    limit: int = Field(default=10, description="Maximum number of results", ge=1, le=100)
    min_similarity: float = Field(default=0.5, description="Minimum similarity threshold", ge=0, le=1)
    tags: Optional[List[str]] = Field(None, description="Filter by specific tags")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty."""
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        """Clean and validate tags filter."""
        if v:
            v = [tag.strip().lower() for tag in v if tag and tag.strip()]
        return v


class SearchMemoryResponse(BaseModel):
    """Response model for memory search."""
    
    query: str = Field(..., description="The original search query")
    results: List[MemorySearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the error occurred")