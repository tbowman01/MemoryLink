# Phase 3: Integration & APIs

## Overview
This phase focuses on making MemoryLink easily integratable with external tools, implementing MCP compliance, adding authentication, and creating client SDKs and examples.

## Objectives
- Implement MCP (Model Context Protocol) compliance
- Add API authentication and rate limiting
- Create batch operations for efficiency
- Build client SDKs and examples
- Implement webhooks and event streaming
- Add advanced search features

## Implementation Tasks

### 3.1 MCP Protocol Compliance (Day 15-16)

#### MCP-Compatible Endpoints
```python
# app/api/routes/mcp.py
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/mcp")

class MCPContext(BaseModel):
    """MCP Context format"""
    role: str
    content: str
    metadata: Optional[dict] = {}

class MCPMemoryRequest(BaseModel):
    """MCP-compliant memory request"""
    context: MCPContext
    operation: str  # "store" or "retrieve"
    parameters: dict

@router.post("/context/store")
async def mcp_store_context(
    request: MCPMemoryRequest,
    x_mcp_version: Optional[str] = Header(None)
):
    """MCP-compliant context storage"""
    # Convert MCP format to internal format
    memory_data = MemoryCreate(
        text=request.context.content,
        tags=[request.context.role],
        metadata={
            "mcp_version": x_mcp_version,
            **request.context.metadata
        }
    )
    # Store using existing service
    return {"status": "stored", "id": memory_id}

@router.post("/context/retrieve")
async def mcp_retrieve_context(
    request: MCPMemoryRequest,
    x_mcp_version: Optional[str] = Header(None)
):
    """MCP-compliant context retrieval"""
    # Convert to internal search format
    query = SearchQuery(
        query=request.parameters.get("query", ""),
        top_k=request.parameters.get("limit", 10)
    )
    # Search and format response
    return {"contexts": formatted_results}
```

### 3.2 Authentication & Authorization (Day 16-17)

#### API Key Authentication
```python
# app/core/auth.py
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Optional
import hashlib
import secrets

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

class AuthService:
    def __init__(self):
        self.api_keys = {}  # In production, use database
        
    def generate_api_key(self, user_id: str) -> str:
        """Generate new API key for user"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[key_hash] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "request_count": 0
        }
        
        return api_key
    
    def verify_api_key(
        self,
        api_key_header: Optional[str] = None,
        api_key_query: Optional[str] = None
    ) -> str:
        """Verify API key and return user_id"""
        api_key = api_key_header or api_key_query
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Update usage stats
        self.api_keys[key_hash]["last_used"] = datetime.utcnow()
        self.api_keys[key_hash]["request_count"] += 1
        
        return self.api_keys[key_hash]["user_id"]

# Dependency for protected routes
async def get_current_user(
    api_key_header: Optional[str] = Security(api_key_header),
    api_key_query: Optional[str] = Security(api_key_query)
) -> str:
    auth_service = AuthService()
    return auth_service.verify_api_key(api_key_header, api_key_query)
```

### 3.3 Rate Limiting (Day 17-18)

#### Rate Limiter Implementation
```python
# app/core/rate_limit.py
from fastapi import HTTPException, Request
from typing import Dict, Tuple
import time
import asyncio

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.requests: Dict[str, list] = {}
        
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < 3600  # Keep last hour
        ]
        
        # Check per-minute limit
        recent_minute = [
            req for req in self.requests[identifier]
            if current_time - req < 60
        ]
        
        if len(recent_minute) >= self.rpm:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.rpm} requests per minute"
            )
        
        # Check per-hour limit
        if len(self.requests[identifier]) >= self.rph:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.rph} requests per hour"
            )
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True

# Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Get identifier (IP or API key)
        identifier = request.client.host
        
        # Check rate limit
        await self.rate_limiter.check_rate_limit(identifier)
        
        response = await call_next(request)
        return response
```

### 3.4 Batch Operations (Day 18-19)

#### Batch Memory Operations
```python
# app/api/routes/batch.py
from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/batch")

class BatchMemoryRequest(BaseModel):
    memories: List[MemoryCreate]

class BatchSearchRequest(BaseModel):
    queries: List[SearchQuery]

@router.post("/memory/add")
async def batch_add_memories(
    request: BatchMemoryRequest,
    service: MemoryService = Depends(get_memory_service)
):
    """Add multiple memories in batch"""
    results = []
    errors = []
    
    # Generate embeddings in batch for efficiency
    texts = [m.text for m in request.memories]
    embeddings = service.embeddings.batch_generate(texts)
    
    for i, memory in enumerate(request.memories):
        try:
            # Use pre-computed embedding
            result = await service.add_memory_with_embedding(
                memory, 
                embeddings[i]
            )
            results.append(result)
        except Exception as e:
            errors.append({
                "index": i,
                "error": str(e)
            })
    
    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

@router.post("/memory/search")
async def batch_search_memories(
    request: BatchSearchRequest,
    service: MemoryService = Depends(get_memory_service)
):
    """Search multiple queries in batch"""
    results = []
    
    # Process searches in parallel
    tasks = [
        service.search_memories(query)
        for query in request.queries
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        "queries": len(request.queries),
        "results": results
    }
```

### 3.5 Advanced Search Features (Day 19-20)

#### Enhanced Search Capabilities
```python
# app/services/advanced_search.py
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

class AdvancedSearchService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
    
    async def search_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        query: Optional[str] = None
    ) -> SearchResult:
        """Search memories within date range"""
        with self.memory_service.db.get_session() as session:
            memories = session.query(Memory).filter(
                and_(
                    Memory.user_id == user_id,
                    Memory.timestamp >= start_date,
                    Memory.timestamp <= end_date
                )
            ).all()
            
            if query:
                # Filter by semantic similarity
                return await self._filter_by_similarity(memories, query)
            
            return self._format_results(memories)
    
    async def search_by_tags(
        self,
        user_id: str,
        tags: List[str],
        mode: str = "any"  # "any" or "all"
    ) -> SearchResult:
        """Search memories by tags"""
        with self.memory_service.db.get_session() as session:
            if mode == "all":
                # Must have all tags
                memories = session.query(Memory).filter(
                    Memory.user_id == user_id
                ).all()
                
                filtered = [
                    m for m in memories
                    if all(tag in m.tags for tag in tags)
                ]
            else:
                # Any tag matches
                memories = session.query(Memory).filter(
                    Memory.user_id == user_id
                ).all()
                
                filtered = [
                    m for m in memories
                    if any(tag in m.tags for tag in tags)
                ]
            
            return self._format_results(filtered)
    
    async def search_related(
        self,
        memory_id: str,
        user_id: str,
        top_k: int = 5
    ) -> SearchResult:
        """Find memories related to a specific memory"""
        # Get original memory
        with self.memory_service.db.get_session() as session:
            memory = session.query(Memory).filter(
                Memory.id == memory_id,
                Memory.user_id == user_id
            ).first()
            
            if not memory:
                return SearchResult(memories=[], total=0, query_time_ms=0)
            
            # Decrypt and search for similar
            text = self.memory_service.encryption.decrypt(
                memory.content_encrypted
            )
            
            query = SearchQuery(
                query=text,
                user_id=user_id,
                top_k=top_k + 1  # +1 to exclude self
            )
            
            results = await self.memory_service.search_memories(query)
            
            # Remove self from results
            results.memories = [
                m for m in results.memories
                if m.id != memory_id
            ][:top_k]
            
            return results
```

### 3.6 Event Streaming & Webhooks (Day 20-21)

#### Server-Sent Events for Real-time Updates
```python
# app/api/routes/stream.py
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

router = APIRouter(prefix="/stream")

class EventBroadcaster:
    def __init__(self):
        self.subscribers = []
    
    async def subscribe(self):
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self.subscribers.remove(queue)
    
    async def broadcast(self, event_type: str, data: dict):
        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        for queue in self.subscribers:
            await queue.put(message)

broadcaster = EventBroadcaster()

@router.get("/events")
async def stream_events(user_id: str = "default"):
    """Stream memory events to client"""
    async def event_generator():
        async for event in broadcaster.subscribe():
            yield {
                "event": "memory_update",
                "data": event
            }
    
    return EventSourceResponse(event_generator())

# Webhook support
class WebhookService:
    def __init__(self):
        self.webhooks = {}  # user_id -> webhook_url
    
    async def register_webhook(self, user_id: str, url: str):
        """Register webhook for user"""
        self.webhooks[user_id] = url
    
    async def trigger_webhook(self, user_id: str, event: dict):
        """Send event to webhook"""
        if user_id in self.webhooks:
            async with httpx.AsyncClient() as client:
                await client.post(
                    self.webhooks[user_id],
                    json=event,
                    timeout=5.0
                )
```

### 3.7 Client SDKs (Day 21)

#### Python SDK
```python
# sdk/python/memorylink.py
import httpx
from typing import List, Dict, Optional

class MemoryLinkClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={"X-API-Key": api_key} if api_key else {}
        )
    
    async def add_memory(
        self,
        text: str,
        tags: List[str] = None,
        metadata: Dict = None
    ) -> Dict:
        """Add a memory"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/memory",
            json={
                "text": text,
                "tags": tags or [],
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        tags: List[str] = None
    ) -> List[Dict]:
        """Search memories"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/memory/search",
            json={
                "query": query,
                "top_k": top_k,
                "tags": tags
            }
        )
        response.raise_for_status()
        return response.json()["memories"]
    
    async def close(self):
        await self.client.aclose()

# Usage example
async def example():
    client = MemoryLinkClient("http://localhost:8080", api_key="your-key")
    
    # Add memory
    memory = await client.add_memory(
        "Important meeting notes",
        tags=["meeting", "project-x"]
    )
    
    # Search
    results = await client.search("meeting notes")
    
    await client.close()
```

#### JavaScript/TypeScript SDK
```typescript
// sdk/js/memorylink.ts
interface Memory {
  id: string;
  text: string;
  tags: string[];
  metadata: Record<string, any>;
  timestamp: string;
}

class MemoryLinkClient {
  private baseUrl: string;
  private apiKey?: string;
  
  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }
  
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    };
    
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    
    return headers;
  }
  
  async addMemory(
    text: string,
    tags: string[] = [],
    metadata: Record<string, any> = {}
  ): Promise<Memory> {
    const response = await fetch(`${this.baseUrl}/api/v1/memory`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ text, tags, metadata })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to add memory: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async search(
    query: string,
    topK: number = 10,
    tags?: string[]
  ): Promise<Memory[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/memory/search`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, top_k: topK, tags })
    });
    
    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result.memories;
  }
}

export default MemoryLinkClient;
```

### 3.8 Integration Examples (Day 21)

#### VSCode Extension Example
```javascript
// examples/vscode-extension/extension.js
const vscode = require('vscode');
const MemoryLinkClient = require('memorylink-sdk');

function activate(context) {
    const client = new MemoryLinkClient(
        'http://localhost:8080',
        vscode.workspace.getConfiguration('memorylink').get('apiKey')
    );
    
    // Command to save selection as memory
    let saveCommand = vscode.commands.registerCommand(
        'memorylink.saveSelection',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;
            
            const selection = editor.document.getText(editor.selection);
            if (!selection) return;
            
            const tags = await vscode.window.showInputBox({
                prompt: 'Enter tags (comma-separated)',
                placeHolder: 'code, javascript, function'
            });
            
            try {
                await client.addMemory(
                    selection,
                    tags ? tags.split(',').map(t => t.trim()) : [],
                    {
                        file: editor.document.fileName,
                        language: editor.document.languageId
                    }
                );
                
                vscode.window.showInformationMessage('Memory saved!');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed: ${error.message}`);
            }
        }
    );
    
    context.subscriptions.push(saveCommand);
}

module.exports = { activate };
```

## OpenAPI Specification

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: MemoryLink API
  version: 1.0.0
  description: Local-first personal memory layer for AI agents

servers:
  - url: http://localhost:8080/api/v1

paths:
  /memory:
    post:
      summary: Add a memory
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MemoryCreate'
      responses:
        200:
          description: Memory created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MemoryResponse'
  
  /memory/search:
    post:
      summary: Search memories
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchQuery'
      responses:
        200:
          description: Search results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResult'

components:
  schemas:
    MemoryCreate:
      type: object
      required:
        - text
      properties:
        text:
          type: string
        tags:
          type: array
          items:
            type: string
        metadata:
          type: object

    MemoryResponse:
      type: object
      properties:
        id:
          type: string
        text:
          type: string
        tags:
          type: array
          items:
            type: string
        timestamp:
          type: string
          format: date-time

    SearchQuery:
      type: object
      required:
        - query
      properties:
        query:
          type: string
        top_k:
          type: integer
          default: 10
        tags:
          type: array
          items:
            type: string

    SearchResult:
      type: object
      properties:
        memories:
          type: array
          items:
            $ref: '#/components/schemas/MemoryResponse'
        total:
          type: integer
        query_time_ms:
          type: number

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - ApiKeyAuth: []
```

## Validation Checklist

### API Features
- [ ] MCP protocol support
- [ ] Authentication working
- [ ] Rate limiting active
- [ ] Batch operations functional
- [ ] Advanced search implemented

### Integration
- [ ] Python SDK tested
- [ ] JavaScript SDK tested
- [ ] OpenAPI spec accurate
- [ ] Webhook delivery working
- [ ] SSE streaming functional

### Documentation
- [ ] API documentation complete
- [ ] SDK examples provided
- [ ] Integration guides written
- [ ] Authentication documented

## Deliverables

1. **Enhanced API**
   - MCP-compliant endpoints
   - Authentication & rate limiting
   - Batch operations
   - Advanced search

2. **Client SDKs**
   - Python SDK package
   - JavaScript/TypeScript SDK
   - Usage examples

3. **Integration Support**
   - OpenAPI specification
   - Webhook system
   - Event streaming
   - Sample integrations

## Success Metrics

- API authentication working
- Rate limiting prevents abuse
- Batch operations improve efficiency
- SDKs simplify integration
- MCP compliance verified

## Next Phase

Phase 4 will focus on testing, optimization, and gamification:
- Comprehensive test suite
- Performance optimization
- Gamified onboarding
- Load testing
- Security audit