# Phase 4: API Enhancement & Integration

## Overview
This phase focuses on enhancing the MemoryLink API with advanced features, complete documentation, client SDKs, and integration capabilities. Building on the secure foundation from previous phases, this phase makes MemoryLink developer-friendly and ready for widespread adoption.

**Timeline:** 3-4 Days  
**Priority:** MEDIUM - Enhanced developer experience  
**Status:** Ready after Phase 2/3 completion  
**Dependencies:** Phase 2 (Authentication) and Phase 3 (Production Readiness)

## Objectives
- Complete OpenAPI documentation with examples
- Implement MCP (Model Context Protocol) compliance
- Create batch operations for efficiency
- Build client SDKs for multiple languages
- Add webhook and event streaming support
- Implement advanced search and filtering
- Create integration examples and templates
- Enable developer portal with interactive docs

## Current API State Analysis

### Existing API Features ✅
- **Core CRUD operations:** Memory add, search, delete implemented
- **FastAPI framework:** Auto-generated OpenAPI docs
- **Input validation:** Pydantic models with validation
- **Error handling:** Consistent error responses
- **Health endpoints:** Service status monitoring
- **Authentication:** JWT and API key support (Phase 2)

### API Enhancement Gaps 🚨
- **Incomplete OpenAPI schema:** Missing examples and detailed descriptions
- **No MCP compliance:** Not compatible with Model Context Protocol
- **No batch operations:** Inefficient for bulk operations
- **No webhook support:** No event notifications
- **Limited search features:** Basic semantic search only
- **No client SDKs:** Manual HTTP integration required

## Implementation Tasks

### Task 4.1: Complete OpenAPI Documentation (0.5 day)

#### 4.1.1: Enhanced API Schema
**File:** `/backend/src/api/openapi_config.py`
```python
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    """Generate enhanced OpenAPI schema with examples and documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MemoryLink API",
        version="1.0.0",
        description="""
# MemoryLink API

A local-first personal memory system that enables AI agents and developer tools to store, search, and retrieve contextual information with semantic understanding.

## Features

- **Semantic Search**: Find memories by meaning, not just keywords
- **Encryption**: All data encrypted at rest with user-controlled keys
- **Authentication**: JWT tokens and API keys for secure access
- **Real-time Events**: Webhooks and SSE for live updates
- **Batch Operations**: Efficient bulk memory operations
- **MCP Compatible**: Model Context Protocol compliance

## Getting Started

1. Register for an account at `/auth/register`
2. Get your API key from `/auth/api-keys`
3. Start storing memories with `/api/v1/memory`
4. Search with natural language at `/api/v1/memory/search`

## Rate Limits

- **Authenticated users**: 60 requests per minute
- **API key users**: 1000 requests per hour
- **Batch operations**: 10 operations per minute

## SDKs

- [Python SDK](https://github.com/memorylink/python-sdk)
- [JavaScript SDK](https://github.com/memorylink/js-sdk)
- [Go SDK](https://github.com/memorylink/go-sdk)
        """,
        routes=app.routes,
    )
    
    # Add examples to schemas
    openapi_schema["components"]["schemas"]["MemoryCreate"]["example"] = {
        "text": "Meeting notes from Q4 planning session. Discussed new product features and budget allocation.",
        "tags": ["meeting", "planning", "q4"],
        "metadata": {
            "source": "zoom_meeting",
            "participants": ["alice@company.com", "bob@company.com"],
            "duration_minutes": 60,
            "priority": "high"
        }
    }
    
    openapi_schema["components"]["schemas"]["SearchQuery"]["example"] = {
        "query": "product planning discussions from last quarter",
        "top_k": 10,
        "threshold": 0.7,
        "tags": ["meeting", "planning"],
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-03-31"
        }
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "https://api.memorylink.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.memorylink.com",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8080",
            "description": "Development server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

#### 4.1.2: Enhanced Route Documentation
**File:** `/backend/src/api/routes/memory.py` (Enhanced with documentation)
```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, date

router = APIRouter(prefix="/api/v1", tags=["Memory Operations"])

@router.post(
    "/memory",
    response_model=MemoryResponse,
    summary="Store a new memory",
    description="""
    Store a new memory with automatic semantic indexing and encryption.
    
    The memory will be encrypted and indexed for semantic search. Tags and metadata
    help with organization and filtering.
    
    **Rate Limit**: 60 requests per minute for authenticated users.
    """,
    responses={
        201: {
            "description": "Memory stored successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "mem_1234567890abcdef",
                        "text": "Meeting notes from Q4 planning session...",
                        "tags": ["meeting", "planning", "q4"],
                        "metadata": {"source": "zoom_meeting", "priority": "high"},
                        "timestamp": "2024-08-24T20:00:00Z",
                        "user_id": "user_abc123",
                        "embedding_id": "emb_1234567890abcdef"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "error": "VALIDATION_ERROR",
                        "message": "Memory text cannot be empty",
                        "details": {"field": "text", "reason": "required"}
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded. 60 requests per minute allowed.",
                        "retry_after": 45
                    }
                }
            }
        }
    }
)
async def add_memory(
    memory: MemoryCreate,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Store a new memory with semantic indexing"""
    memory.user_id = user.id
    result = await service.add_memory(memory)
    return result

@router.post(
    "/memory/search",
    response_model=SearchResult,
    summary="Search memories with natural language",
    description="""
    Search your memories using natural language queries. The system uses semantic
    similarity to find relevant memories even if exact words don't match.
    
    **Examples of queries:**
    - "meeting notes about the new product"
    - "technical discussions from last week"
    - "budget planning conversations"
    
    **Filtering options:**
    - Tags: Only search memories with specific tags
    - Date range: Limit search to specific time period
    - Threshold: Control similarity matching strictness (0.0-1.0)
    """,
    responses={
        200: {
            "description": "Search results",
            "content": {
                "application/json": {
                    "example": {
                        "memories": [
                            {
                                "id": "mem_1234567890abcdef",
                                "text": "Meeting notes from Q4 planning session...",
                                "tags": ["meeting", "planning", "q4"],
                                "similarity_score": 0.94,
                                "timestamp": "2024-08-24T20:00:00Z"
                            }
                        ],
                        "total": 1,
                        "query_time_ms": 45.2,
                        "query": "planning meeting notes"
                    }
                }
            }
        }
    }
)
async def search_memory(
    query: SearchQuery,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Search memories with semantic understanding"""
    query.user_id = user.id
    results = await service.search_memories(query)
    return results

@router.post(
    "/memory/batch",
    response_model=BatchOperationResult,
    summary="Bulk memory operations",
    description="""
    Perform bulk operations on memories for efficiency. Supports adding multiple
    memories in a single request with optimized embedding generation.
    
    **Rate Limit**: 10 batch operations per minute.
    """,
    responses={
        200: {
            "description": "Batch operation results",
            "content": {
                "application/json": {
                    "example": {
                        "successful": 8,
                        "failed": 2,
                        "results": [
                            {"id": "mem_001", "status": "success"},
                            {"id": "mem_002", "status": "error", "error": "Text too long"}
                        ],
                        "processing_time_ms": 1250
                    }
                }
            }
        }
    }
)
async def batch_add_memories(
    request: BatchMemoryRequest,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Add multiple memories in a single batch operation"""
    # Implementation for batch operations
    pass
```

### Task 4.2: MCP Protocol Implementation (1 day)

#### 4.2.1: MCP-Compatible Endpoints
**File:** `/backend/src/api/routes/mcp.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol"])

class MCPResource(BaseModel):
    """MCP Resource representation"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = "text/plain"
    metadata: Dict[str, Any] = {}

class MCPContext(BaseModel):
    """MCP Context representation"""
    role: str
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None

class MCPMemoryRequest(BaseModel):
    """MCP Memory operation request"""
    operation: str  # "store", "retrieve", "search", "delete"
    context: Optional[MCPContext] = None
    query: Optional[str] = None
    parameters: Dict[str, Any] = {}

class MCPMemoryResponse(BaseModel):
    """MCP Memory operation response"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

@router.get("/capabilities")
async def get_capabilities():
    """MCP Capabilities endpoint - describes what this server can do"""
    return {
        "capabilities": {
            "memory": {
                "store": True,
                "retrieve": True,
                "search": True,
                "delete": True,
                "batch": True
            },
            "resources": {
                "list": True,
                "read": True
            },
            "tools": {
                "semantic_search": {
                    "description": "Search memories using semantic similarity",
                    "parameters": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 10},
                        "threshold": {"type": "number", "default": 0.5}
                    }
                }
            }
        },
        "server": {
            "name": "MemoryLink",
            "version": "1.0.0",
            "description": "Local-first personal memory layer"
        }
    }

@router.post("/memory", response_model=MCPMemoryResponse)
async def mcp_memory_operation(
    request: MCPMemoryRequest,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """MCP-compliant memory operations"""
    
    try:
        if request.operation == "store":
            if not request.context:
                raise HTTPException(400, "Context required for store operation")
            
            # Convert MCP context to MemoryLink format
            memory_data = MemoryCreate(
                text=request.context.content,
                tags=[request.context.role] if request.context.role else [],
                metadata={
                    "mcp_source": True,
                    "role": request.context.role,
                    **request.context.metadata,
                    **request.parameters
                }
            )
            memory_data.user_id = user.id
            
            result = await service.add_memory(memory_data)
            
            return MCPMemoryResponse(
                success=True,
                data={
                    "id": result.id,
                    "uri": f"memorylink://memory/{result.id}"
                },
                metadata={"timestamp": result.timestamp.isoformat()}
            )
        
        elif request.operation == "search":
            if not request.query:
                raise HTTPException(400, "Query required for search operation")
            
            search_query = SearchQuery(
                query=request.query,
                user_id=user.id,
                top_k=request.parameters.get("limit", 10),
                threshold=request.parameters.get("threshold", 0.5)
            )
            
            results = await service.search_memories(search_query)
            
            # Convert to MCP format
            mcp_contexts = []
            for memory in results.memories:
                mcp_contexts.append({
                    "uri": f"memorylink://memory/{memory.id}",
                    "role": memory.metadata.get("role", "assistant"),
                    "content": memory.text,
                    "metadata": {
                        **memory.metadata,
                        "timestamp": memory.timestamp.isoformat(),
                        "tags": memory.tags
                    }
                })
            
            return MCPMemoryResponse(
                success=True,
                data={
                    "contexts": mcp_contexts,
                    "total": results.total,
                    "query_time_ms": results.query_time_ms
                }
            )
        
        elif request.operation == "retrieve":
            memory_id = request.parameters.get("id")
            if not memory_id:
                raise HTTPException(400, "Memory ID required for retrieve operation")
            
            # Get specific memory by ID
            memory = await service.get_memory(memory_id, user.id)
            if not memory:
                return MCPMemoryResponse(
                    success=False,
                    error="Memory not found"
                )
            
            return MCPMemoryResponse(
                success=True,
                data={
                    "context": {
                        "uri": f"memorylink://memory/{memory.id}",
                        "role": memory.metadata.get("role", "assistant"),
                        "content": memory.text,
                        "metadata": memory.metadata
                    }
                }
            )
        
        elif request.operation == "delete":
            memory_id = request.parameters.get("id")
            if not memory_id:
                raise HTTPException(400, "Memory ID required for delete operation")
            
            success = await service.delete_memory(memory_id, user.id)
            
            return MCPMemoryResponse(
                success=success,
                data={"deleted": memory_id} if success else None,
                error="Memory not found" if not success else None
            )
        
        else:
            raise HTTPException(400, f"Unknown operation: {request.operation}")
    
    except HTTPException:
        raise
    except Exception as e:
        return MCPMemoryResponse(
            success=False,
            error=str(e)
        )

@router.get("/resources", response_model=List[MCPResource])
async def list_resources(
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """List available memory resources in MCP format"""
    
    # Get user's memories
    recent_memories = await service.get_recent_memories(user.id, limit=100)
    
    resources = []
    for memory in recent_memories:
        resources.append(MCPResource(
            uri=f"memorylink://memory/{memory.id}",
            name=f"Memory: {memory.text[:50]}...",
            description=f"Memory from {memory.timestamp.strftime('%Y-%m-%d %H:%M')}",
            mimeType="text/plain",
            metadata={
                "tags": memory.tags,
                "timestamp": memory.timestamp.isoformat(),
                "size": len(memory.text)
            }
        ))
    
    return resources

@router.get("/resources/{resource_id}")
async def read_resource(
    resource_id: str,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Read a specific memory resource"""
    
    memory = await service.get_memory(resource_id, user.id)
    if not memory:
        raise HTTPException(404, "Resource not found")
    
    return {
        "contents": [{
            "uri": f"memorylink://memory/{memory.id}",
            "mimeType": "text/plain",
            "text": memory.text,
            "metadata": {
                "tags": memory.tags,
                "timestamp": memory.timestamp.isoformat(),
                **memory.metadata
            }
        }]
    }
```

### Task 4.3: Advanced Search Features (0.5 day)

#### 4.3.1: Enhanced Search Capabilities
**File:** `/backend/src/services/advanced_search_service.py`
```python
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy import and_, or_, func
from pydantic import BaseModel

class DateRange(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None

class AdvancedSearchQuery(BaseModel):
    query: str
    user_id: str = "default"
    top_k: int = 10
    threshold: float = 0.5
    tags: Optional[List[str]] = None
    date_range: Optional[DateRange] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    sort_by: str = "relevance"  # "relevance", "date", "similarity"
    include_content: bool = True
    include_similar: bool = False  # Include similar memories for each result

class AdvancedSearchService:
    def __init__(self, memory_service):
        self.memory_service = memory_service
    
    async def advanced_search(self, query: AdvancedSearchQuery) -> SearchResult:
        """Enhanced search with advanced filtering and sorting"""
        
        # Start with semantic search
        base_query = SearchQuery(
            query=query.query,
            user_id=query.user_id,
            top_k=query.top_k * 2,  # Get more results for filtering
            threshold=query.threshold
        )
        
        semantic_results = await self.memory_service.search_memories(base_query)
        
        # Apply advanced filters
        filtered_memories = []
        for memory in semantic_results.memories:
            if self._passes_filters(memory, query):
                if query.include_similar:
                    # Find similar memories to this one
                    similar = await self._find_similar_memories(memory, query.user_id)
                    memory.similar_memories = similar
                
                filtered_memories.append(memory)
        
        # Sort results
        sorted_memories = self._sort_memories(filtered_memories, query.sort_by)
        
        # Limit to requested count
        final_results = sorted_memories[:query.top_k]
        
        return SearchResult(
            memories=final_results,
            total=len(final_results),
            query_time_ms=semantic_results.query_time_ms,
            query=query.query,
            filters_applied={
                "tags": query.tags,
                "date_range": query.date_range.dict() if query.date_range else None,
                "metadata_filters": query.metadata_filters,
                "sort_by": query.sort_by
            }
        )
    
    def _passes_filters(self, memory, query: AdvancedSearchQuery) -> bool:
        """Check if memory passes all filters"""
        
        # Tag filtering
        if query.tags:
            if not any(tag in memory.tags for tag in query.tags):
                return False
        
        # Date range filtering
        if query.date_range:
            memory_date = memory.timestamp.date()
            if query.date_range.start and memory_date < query.date_range.start:
                return False
            if query.date_range.end and memory_date > query.date_range.end:
                return False
        
        # Metadata filtering
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                if key not in memory.metadata:
                    return False
                if memory.metadata[key] != value:
                    return False
        
        return True
    
    def _sort_memories(self, memories: List[MemoryResponse], sort_by: str) -> List[MemoryResponse]:
        """Sort memories by specified criteria"""
        
        if sort_by == "date":
            return sorted(memories, key=lambda m: m.timestamp, reverse=True)
        elif sort_by == "similarity":
            return sorted(memories, key=lambda m: getattr(m, 'similarity_score', 0), reverse=True)
        else:  # relevance (default)
            # Relevance combines recency and similarity
            def relevance_score(memory):
                similarity = getattr(memory, 'similarity_score', 0.5)
                days_old = (datetime.utcnow() - memory.timestamp).days
                recency_factor = max(0, 1 - days_old / 365)  # Decay over a year
                return similarity * 0.7 + recency_factor * 0.3
            
            return sorted(memories, key=relevance_score, reverse=True)
    
    async def _find_similar_memories(self, memory: MemoryResponse, user_id: str, limit: int = 3) -> List[MemoryResponse]:
        """Find memories similar to the given memory"""
        
        # Use the memory's text to find similar ones
        similar_query = SearchQuery(
            query=memory.text,
            user_id=user_id,
            top_k=limit + 1,  # +1 to exclude self
            threshold=0.6
        )
        
        results = await self.memory_service.search_memories(similar_query)
        
        # Remove the original memory and limit results
        similar_memories = [m for m in results.memories if m.id != memory.id][:limit]
        return similar_memories

    async def search_by_conversation_thread(self, user_id: str, thread_id: str) -> List[MemoryResponse]:
        """Search memories by conversation thread"""
        
        with self.memory_service.db.get_session() as session:
            memories = session.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.metadata.contains({"thread_id": thread_id})
            ).order_by(Memory.timestamp).all()
            
            return [self._convert_to_response(memory) for memory in memories]
    
    async def get_memory_timeline(self, user_id: str, start_date: date, end_date: date) -> Dict[str, List[MemoryResponse]]:
        """Get memories organized by date"""
        
        with self.memory_service.db.get_session() as session:
            memories = session.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.timestamp >= datetime.combine(start_date, datetime.min.time()),
                Memory.timestamp <= datetime.combine(end_date, datetime.max.time())
            ).order_by(Memory.timestamp.desc()).all()
            
            # Group by date
            timeline = {}
            for memory in memories:
                date_key = memory.timestamp.date().isoformat()
                if date_key not in timeline:
                    timeline[date_key] = []
                timeline[date_key].append(self._convert_to_response(memory))
            
            return timeline
```

### Task 4.4: Webhook and Event Streaming (1 day)

#### 4.4.1: Event System
**File:** `/backend/src/services/event_service.py`
```python
import asyncio
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import httpx
from pydantic import BaseModel, HttpUrl

class EventType(str, Enum):
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    SEARCH_PERFORMED = "search.performed"
    USER_LOGIN = "user.login"
    API_KEY_USED = "api_key.used"

class Event(BaseModel):
    id: str
    type: EventType
    timestamp: datetime
    user_id: str
    data: Dict
    metadata: Dict = {}

class WebhookEndpoint(BaseModel):
    id: str
    user_id: str
    url: HttpUrl
    events: List[EventType]
    is_active: bool = True
    secret: Optional[str] = None
    retry_attempts: int = 3
    timeout_seconds: int = 10

class EventService:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.webhooks: Dict[str, WebhookEndpoint] = {}
        self.event_queue = asyncio.Queue()
        self.sse_clients: Dict[str, List[asyncio.Queue]] = {}
        
        # Start background event processor
        asyncio.create_task(self._process_events())
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to events with callback"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def emit_event(self, event_type: EventType, user_id: str, data: Dict, metadata: Dict = None):
        """Emit an event to all subscribers"""
        event = Event(
            id=f"evt_{int(datetime.utcnow().timestamp() * 1000)}",
            type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            data=data,
            metadata=metadata or {}
        )
        
        await self.event_queue.put(event)
    
    async def _process_events(self):
        """Background task to process events"""
        while True:
            try:
                event = await self.event_queue.get()
                
                # Notify subscribers
                if event.type in self.subscribers:
                    for callback in self.subscribers[event.type]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            print(f"Error in event subscriber: {e}")
                
                # Send to webhooks
                await self._send_to_webhooks(event)
                
                # Send to SSE clients
                await self._send_to_sse_clients(event)
                
            except Exception as e:
                print(f"Error processing event: {e}")
                await asyncio.sleep(1)
    
    async def _send_to_webhooks(self, event: Event):
        """Send event to registered webhooks"""
        user_webhooks = [
            webhook for webhook in self.webhooks.values()
            if webhook.user_id == event.user_id and 
               webhook.is_active and 
               event.type in webhook.events
        ]
        
        tasks = []
        for webhook in user_webhooks:
            tasks.append(self._deliver_webhook(webhook, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _deliver_webhook(self, webhook: WebhookEndpoint, event: Event):
        """Deliver single webhook with retries"""
        payload = {
            "id": event.id,
            "type": event.type,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "metadata": event.metadata
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-MemoryLink-Event": event.type,
            "X-MemoryLink-Timestamp": event.timestamp.isoformat(),
        }
        
        if webhook.secret:
            # Add HMAC signature for security
            import hmac
            import hashlib
            signature = hmac.new(
                webhook.secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-MemoryLink-Signature"] = f"sha256={signature}"
        
        for attempt in range(webhook.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=webhook.timeout_seconds) as client:
                    response = await client.post(
                        str(webhook.url),
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code < 400:
                        return  # Success
                    
                    print(f"Webhook delivery failed (attempt {attempt + 1}): {response.status_code}")
                    
            except Exception as e:
                print(f"Webhook delivery error (attempt {attempt + 1}): {e}")
            
            if attempt < webhook.retry_attempts - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _send_to_sse_clients(self, event: Event):
        """Send event to Server-Sent Event clients"""
        if event.user_id in self.sse_clients:
            event_data = {
                "type": event.type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }
            
            # Send to all clients for this user
            for client_queue in self.sse_clients[event.user_id]:
                try:
                    await client_queue.put(event_data)
                except Exception as e:
                    print(f"Error sending to SSE client: {e}")
    
    def register_webhook(self, webhook: WebhookEndpoint):
        """Register a new webhook endpoint"""
        self.webhooks[webhook.id] = webhook
    
    def unregister_webhook(self, webhook_id: str):
        """Unregister a webhook endpoint"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
    
    async def add_sse_client(self, user_id: str) -> asyncio.Queue:
        """Add SSE client and return queue for events"""
        if user_id not in self.sse_clients:
            self.sse_clients[user_id] = []
        
        client_queue = asyncio.Queue()
        self.sse_clients[user_id].append(client_queue)
        return client_queue
    
    def remove_sse_client(self, user_id: str, client_queue: asyncio.Queue):
        """Remove SSE client"""
        if user_id in self.sse_clients:
            try:
                self.sse_clients[user_id].remove(client_queue)
                if not self.sse_clients[user_id]:
                    del self.sse_clients[user_id]
            except ValueError:
                pass  # Client queue not found
```

#### 4.4.2: Webhook Management API
**File:** `/backend/src/api/routes/webhooks.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[EventType]
    secret: Optional[str] = None

class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[EventType]
    is_active: bool
    created_at: datetime

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    user: DBUser = Depends(get_authenticated_user),
    event_service: EventService = Depends(get_event_service)
):
    """Register a new webhook endpoint"""
    
    webhook = WebhookEndpoint(
        id=str(uuid.uuid4()),
        user_id=user.id,
        url=webhook_data.url,
        events=webhook_data.events,
        secret=webhook_data.secret
    )
    
    event_service.register_webhook(webhook)
    
    return WebhookResponse(
        id=webhook.id,
        url=str(webhook.url),
        events=webhook.events,
        is_active=webhook.is_active,
        created_at=datetime.utcnow()
    )

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    user: DBUser = Depends(get_authenticated_user),
    event_service: EventService = Depends(get_event_service)
):
    """List user's webhook endpoints"""
    
    user_webhooks = [
        webhook for webhook in event_service.webhooks.values()
        if webhook.user_id == user.id
    ]
    
    return [
        WebhookResponse(
            id=webhook.id,
            url=str(webhook.url),
            events=webhook.events,
            is_active=webhook.is_active,
            created_at=datetime.utcnow()  # Would be stored in DB in real implementation
        )
        for webhook in user_webhooks
    ]

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    user: DBUser = Depends(get_authenticated_user),
    event_service: EventService = Depends(get_event_service)
):
    """Delete a webhook endpoint"""
    
    webhook = event_service.webhooks.get(webhook_id)
    if not webhook or webhook.user_id != user.id:
        raise HTTPException(404, "Webhook not found")
    
    event_service.unregister_webhook(webhook_id)
    return {"status": "deleted", "webhook_id": webhook_id}
```

### Task 4.5: Client SDKs (1 day)

#### 4.5.1: Python SDK
**File:** `/sdks/python/memorylink/client.py`
```python
import httpx
from typing import List, Dict, Optional, Union, AsyncContextManager
from datetime import datetime, date
import asyncio
from pydantic import BaseModel

class MemoryLinkError(Exception):
    """Base exception for MemoryLink client"""
    pass

class AuthenticationError(MemoryLinkError):
    """Authentication failed"""
    pass

class RateLimitError(MemoryLinkError):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after

class Memory(BaseModel):
    id: str
    text: str
    tags: List[str]
    metadata: Dict
    timestamp: datetime
    similarity_score: Optional[float] = None

class SearchResult(BaseModel):
    memories: List[Memory]
    total: int
    query_time_ms: float
    query: str

class AsyncMemoryLinkClient:
    """Async Python client for MemoryLink API"""
    
    def __init__(
        self,
        base_url: str = "https://api.memorylink.com",
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.jwt_token = jwt_token
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        elif jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers=headers
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _handle_response(self, response: httpx.Response):
        """Handle HTTP response and raise appropriate exceptions"""
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 60)
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after)
            )
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", "Unknown error")
            except:
                message = f"HTTP {response.status_code}"
            raise MemoryLinkError(message)
        
        response.raise_for_status()
        return response.json()
    
    async def add_memory(
        self,
        text: str,
        tags: List[str] = None,
        metadata: Dict = None
    ) -> Memory:
        """Add a new memory"""
        payload = {
            "text": text,
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/memory",
            json=payload
        )
        
        data = self._handle_response(response)
        return Memory(**data)
    
    async def search_memories(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.5,
        tags: List[str] = None,
        date_range: Dict[str, Union[str, date]] = None,
        metadata_filters: Dict = None
    ) -> SearchResult:
        """Search memories with advanced filtering"""
        payload = {
            "query": query,
            "top_k": top_k,
            "threshold": threshold
        }
        
        if tags:
            payload["tags"] = tags
        if date_range:
            payload["date_range"] = {
                k: v.isoformat() if isinstance(v, date) else v
                for k, v in date_range.items()
            }
        if metadata_filters:
            payload["metadata_filters"] = metadata_filters
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/memory/search",
            json=payload
        )
        
        data = self._handle_response(response)
        return SearchResult(**data)
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/memory/{memory_id}"
        )
        
        if response.status_code == 404:
            return None
        
        data = self._handle_response(response)
        return Memory(**data)
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        response = await self.client.delete(
            f"{self.base_url}/api/v1/memory/{memory_id}"
        )
        
        if response.status_code == 404:
            return False
        
        self._handle_response(response)
        return True
    
    async def batch_add_memories(self, memories: List[Dict]) -> Dict:
        """Add multiple memories in a batch"""
        payload = {"memories": memories}
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/memory/batch",
            json=payload
        )
        
        return self._handle_response(response)
    
    async def create_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict:
        """Create a webhook endpoint"""
        payload = {
            "url": url,
            "events": events
        }
        if secret:
            payload["secret"] = secret
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/webhooks",
            json=payload
        )
        
        return self._handle_response(response)
    
    async def stream_events(self) -> AsyncContextManager:
        """Stream events via Server-Sent Events"""
        async with self.client.stream(
            "GET",
            f"{self.base_url}/api/v1/stream/events"
        ) as response:
            if response.status_code != 200:
                self._handle_response(response)
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

# Synchronous client
class MemoryLinkClient:
    """Synchronous Python client for MemoryLink API"""
    
    def __init__(self, *args, **kwargs):
        self._async_client = AsyncMemoryLinkClient(*args, **kwargs)
    
    def add_memory(self, *args, **kwargs) -> Memory:
        return asyncio.run(self._async_client.add_memory(*args, **kwargs))
    
    def search_memories(self, *args, **kwargs) -> SearchResult:
        return asyncio.run(self._async_client.search_memories(*args, **kwargs))
    
    def get_memory(self, *args, **kwargs) -> Optional[Memory]:
        return asyncio.run(self._async_client.get_memory(*args, **kwargs))
    
    def delete_memory(self, *args, **kwargs) -> bool:
        return asyncio.run(self._async_client.delete_memory(*args, **kwargs))
    
    def close(self):
        asyncio.run(self._async_client.close())
```

## Success Criteria

### API Documentation:
- [ ] OpenAPI schema complete with examples
- [ ] Interactive API documentation accessible
- [ ] All endpoints documented with request/response examples
- [ ] Error responses documented with status codes
- [ ] Authentication methods clearly explained

### MCP Compliance:
- [ ] MCP endpoints responding correctly
- [ ] Resource listing and reading functional
- [ ] Context storage and retrieval working
- [ ] Tool definitions properly exposed
- [ ] Capability advertisement accurate

### Advanced Features:
- [ ] Batch operations improving efficiency
- [ ] Advanced search with filtering working
- [ ] Webhook system delivering events
- [ ] SSE streaming functional
- [ ] Rate limiting protecting endpoints

### Client SDKs:
- [ ] Python SDK functional with async support
- [ ] JavaScript SDK working in browsers/Node.js
- [ ] Error handling consistent across SDKs
- [ ] Documentation and examples provided
- [ ] Package publishing configured

This phase transforms MemoryLink into a developer-friendly platform with comprehensive API features, multiple integration options, and production-ready client libraries.