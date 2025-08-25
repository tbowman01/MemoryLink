# MemoryLink Component Interaction Diagrams
*SPARC Architecture Phase - Component Relationships and Interactions*

## Component Interaction Overview

This document provides detailed component interaction diagrams showing how different parts of the MemoryLink system communicate and coordinate during various operations.

## 1. System Component Map

### 1.1 Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MemoryLink System                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Presentation Layer                             │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │    CLI      │  │  REST API   │  │   Health    │  │  MCP Adapter│ │   │
│  │  │  Interface  │  │  Endpoints  │  │  Endpoints  │  │  Interface  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Service Layer                                 │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Memory    │  │  Embedding  │  │ Encryption  │  │    Auth     │ │   │
│  │  │   Service   │  │   Service   │  │   Service   │  │  Service    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Data Access Layer                              │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │  Vector     │  │  Metadata   │  │   Config    │  │   Cache     │ │   │
│  │  │   Store     │  │   Store     │  │   Store     │  │   Store     │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Infrastructure Layer                            │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Logging   │  │  Monitoring │  │    Docker   │  │    File     │ │   │
│  │  │   System    │  │   System    │  │  Container  │  │   System    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Memory Addition Operation Interaction

### 2.1 Component Interaction Flow

```
┌─────────────┐
│   Client    │
│  (CLI/API)  │
└──────┬──────┘
       │ 1. POST /add_memory
       │ {"content": "...", "tags": [...]}
       ▼
┌─────────────────┐
│   FastAPI       │
│   Router        │◄────────────────────────┐
└──────┬──────────┘                        │
       │ 2. Route to handler               │
       ▼                                   │
┌─────────────────┐                        │ 9. HTTP 201 Response
│  Memory Route   │                        │ {"id": "...", "status": "success"}
│   Handler       │                        │
└──────┬──────────┘                        │
       │ 3. Validate input                 │
       ▼                                   │
┌─────────────────┐     ┌─────────────────┐ │
│   Memory        │────▶│   Embedding     │ │
│   Service       │ 4.  │    Service      │ │
│                 │     │                 │ │
│   orchestrate() │◄────│ generate_embed()│ │
└──────┬──────────┘ 5.  └─────────────────┘ │
       │ 6. Content + embedding             │
       ▼                                    │
┌─────────────────┐                         │
│   Encryption    │                         │
│    Service      │                         │
│                 │                         │
│  encrypt(text)  │                         │
└──────┬──────────┘                         │
       │ 7. Encrypted content               │
       ▼                                    │
┌─────────────────┐                         │
│   Vector        │                         │
│    Store        │                         │
│  (ChromaDB)     │                         │
│                 │                         │
│  store_memory() │─────────────────────────┘
└─────────────────┘ 8. Confirm storage
```

### 2.2 Detailed Component Interactions

**Step 1-3: Request Processing**
```python
# FastAPI Router → Memory Route Handler
@app.post("/add_memory")
async def add_memory(request: MemoryRequest):
    # Component interaction: Router delegates to handler
    return await memory_handler.add_memory(request)

# Memory Route Handler → Input Validation
async def add_memory(request: MemoryRequest):
    # Component interaction: Handler validates with Pydantic
    validated_data = MemorySchema.validate(request)
    
    # Component interaction: Handler calls service layer
    return await memory_service.add_memory(validated_data)
```

**Step 4-5: Service Coordination**
```python
# Memory Service → Embedding Service Interaction
class MemoryService:
    async def add_memory(self, data: dict) -> str:
        # Component interaction: Service orchestrates other services
        embedding = await self.embedding_service.generate(data['content'])
        
        encrypted_content = await self.encryption_service.encrypt(data['content'])
        
        return await self.vector_store.store_memory(
            content=encrypted_content,
            embedding=embedding,
            metadata=data.get('metadata', {})
        )
```

**Step 6-8: Data Storage**
```python
# Encryption Service → Vector Store Interaction
class VectorStore:
    async def store_memory(self, content: str, embedding: list, metadata: dict):
        # Component interaction: Store coordinates with ChromaDB
        result = await self.collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding],
            documents=[content],  # Already encrypted
            metadatas=[metadata]
        )
        return result.ids[0]
```

## 3. Memory Search Operation Interaction

### 3.1 Search Component Flow

```
┌─────────────┐
│   Client    │
│             │
└──────┬──────┘
       │ 1. GET /search_memory?query=...
       ▼
┌─────────────────┐
│   FastAPI       │
│   Router        │
└──────┬──────────┘
       │ 2. Route to search handler
       ▼
┌─────────────────┐                    ┌─────────────────┐
│  Search Route   │───────────────────▶│   Memory        │
│   Handler       │ 3. Parse query     │   Service       │
└─────────────────┘                    └──────┬──────────┘
                                              │ 4. Orchestrate search
                                              ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Embedding     │◄───│                 │
                    │    Service      │ 5. │                 │
                    │                 │    │                 │
                    │ generate_query_ │    │                 │
                    │   embedding()   │    │                 │
                    └─────────────────┘    │                 │
                                          │                 │
                    ┌─────────────────┐    │                 │
                    │   Vector        │◄───│                 │
                    │    Store        │ 6. │                 │
                    │  (ChromaDB)     │    │                 │
                    │                 │    │                 │
                    │ similarity_     │    │                 │
                    │   search()      │    │                 │
                    └──────┬──────────┘    │                 │
                           │ 7. Raw results│                 │
                           ▼               │                 │
                    ┌─────────────────┐    │                 │
                    │   Encryption    │◄───┤                 │
                    │    Service      │ 8. │                 │
                    │                 │    │                 │
                    │   decrypt()     │    │                 │
                    └──────┬──────────┘    │                 │
                           │ 9. Decrypted  │                 │
                           │    results    ▼                 │
                    ┌─────────────────────────────────────────┐
                    │          Result Processor               │
                    │                                         │
                    │  • Filter by metadata                   │
                    │  • Rank by relevance                    │
                    │  • Format response                      │
                    └──────┬──────────────────────────────────┘
                           │ 10. Formatted results
                           ▼
┌─────────────┐    ┌─────────────────┐
│   Client    │◄───│   HTTP          │
│             │    │  Response       │
└─────────────┘    └─────────────────┘
```

## 4. System Initialization Component Interactions

### 4.1 Startup Sequence Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Docker    │    │    App      │    │  Services   │    │   Storage   │    │   Server    │
│ Container   │    │   Config    │    │   Layer     │    │   Layer     │    │   Layer     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │                  │
       │ 1. Start         │                  │                  │                  │
       ├─────────────────▶│                  │                  │                  │
       │                  │ 2. Load config   │                  │                  │
       │                  ├─────────────────▶│                  │                  │
       │                  │                  │ 3. Init services │                  │
       │                  │                  ├─────────────────▶│                  │
       │                  │                  │                  │ 4. Connect stores│
       │                  │                  │◄─────────────────┤                  │
       │                  │◄─────────────────┤ 5. Services ready│                  │
       │                  │ 6. Config ready  ├─────────────────▶│                  │
       │                  │                  │                  │ 7. Start server │
       │                  │                  │                  │◄─────────────────┤
       │◄─────────────────┤                  │                  │                  │ 8. Ready
       │ 9. Container     │                  │                  │                  │
       │    ready         │                  │                  │                  │
```

### 4.2 Service Dependency Resolution

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dependency Graph                             │
│                                                                 │
│  ┌─────────────┐              ┌─────────────┐                   │
│  │   Config    │─────────────▶│   Logging   │                   │
│  │  Service    │              │   Service   │                   │
│  └─────────────┘              └─────────────┘                   │
│         │                             │                         │
│         │                             │                         │
│         ▼                             ▼                         │
│  ┌─────────────┐              ┌─────────────┐                   │
│  │ Encryption  │              │ Monitoring  │                   │
│  │  Service    │              │  Service    │                   │
│  └──────┬──────┘              └─────────────┘                   │
│         │                                                       │
│         │      ┌─────────────┐                                  │
│         ├─────▶│ Embedding   │                                  │
│         │      │  Service    │                                  │
│         │      └──────┬──────┘                                  │
│         │             │                                         │
│         │             │                                         │
│         ▼             ▼                                         │
│  ┌─────────────────────────────┐                                │
│  │      Vector Store           │                                │
│  │     (ChromaDB)             │                                │
│  └────────────┬────────────────┘                                │
│               │                                                 │
│               │                                                 │
│               ▼                                                 │
│  ┌─────────────────────────────┐                                │
│  │      Memory Service         │                                │
│  │    (Orchestrator)          │                                │
│  └────────────┬────────────────┘                                │
│               │                                                 │
│               │                                                 │
│               ▼                                                 │
│  ┌─────────────────────────────┐                                │
│  │      FastAPI Server         │                                │
│  │     (HTTP Interface)        │                                │
│  └─────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## 5. Error Handling Component Interactions

### 5.1 Error Flow Diagram

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐
│   Client    │    │  Presentation   │    │    Service      │    │    Data     │
│             │    │     Layer       │    │     Layer       │    │   Layer     │
└──────┬──────┘    └──────┬──────────┘    └──────┬──────────┘    └──────┬──────┘
       │                  │                      │                      │
       │ 1. Request       │                      │                      │
       ├─────────────────▶│                      │                      │
       │                  │ 2. Validate          │                      │
       │                  ├─────────────────────▶│                      │
       │                  │                      │ 3. Process           │
       │                  │                      ├─────────────────────▶│
       │                  │                      │                      │ 4. Error occurs
       │                  │                      │◄─────────────────────┤    (e.g., storage
       │                  │◄─────────────────────┤ 5. ServiceError      │     failure)
       │◄─────────────────┤ 6. HTTPException     │                      │
       │ 7. Error         │                      │                      │
       │    Response      │                      │                      │
```

### 5.2 Error Handling Components

```python
# Error handling component interactions

class ErrorHandler:
    """Centralizes error handling across all components"""
    
    def __init__(self, logger, monitoring):
        self.logger = logger
        self.monitoring = monitoring
    
    async def handle_service_error(self, error: ServiceError, context: dict):
        # Component interaction: ErrorHandler → Logger
        await self.logger.log_error(error, context)
        
        # Component interaction: ErrorHandler → Monitoring
        await self.monitoring.record_error_metric(error.type, context)
        
        # Component interaction: ErrorHandler → Response formatter
        return self.format_error_response(error)

class MemoryService:
    def __init__(self, error_handler):
        self.error_handler = error_handler
    
    async def add_memory(self, data):
        try:
            # Normal processing
            return await self._process_memory(data)
        except VectorStoreError as e:
            # Component interaction: Service → Error Handler
            return await self.error_handler.handle_service_error(
                e, {"operation": "add_memory", "data": data}
            )
```

## 6. Configuration Component Interactions

### 6.1 Configuration Loading Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Configuration Component Map                         │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │Environment  │    │   Config    │    │  Settings   │                  │
│  │ Variables   │───▶│   Loader    │───▶│ Validator   │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│                             │                   │                       │
│                             ▼                   │                       │
│                    ┌─────────────┐              │                       │
│                    │  .env File  │              │                       │
│                    │   Reader    │──────────────┘                       │
│                    └─────────────┘                                      │
│                             │                                           │
│                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 Configuration Object                            │   │
│  │                                                                 │   │
│  │  settings = Settings(                                           │   │
│  │    encryption_key="...",                                        │   │
│  │    data_path="./data",                                          │   │
│  │    host="127.0.0.1",                                            │   │
│  │    port=8080                                                    │   │
│  │  )                                                              │   │
│  └─────────────┬───────────────────────────────────────────────────┘   │
│                │                                                       │
│                ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                Service Configuration                            │   │
│  │                                                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │   Memory    │  │  Vector     │  │ Encryption  │              │   │
│  │  │   Service   │  │   Store     │  │  Service    │              │   │
│  │  │   Config    │  │   Config    │  │   Config    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 7. Health Check Component Interactions

### 7.1 Health Check Flow

```
┌─────────────┐    ┌─────────────────────────────────────────────────────┐
│   Client    │    │              MemoryLink System                     │
│             │    │                                                    │
│ GET /healthz│───▶│  ┌─────────────────┐                               │
└─────────────┘    │  │ Health Check    │                               │
                   │  │ Route Handler   │                               │
                   │  └──────┬──────────┘                               │
                   │         │                                          │
                   │         ▼                                          │
                   │  ┌─────────────────┐    ┌─────────────────┐        │
                   │  │ Health Check    │───▶│   API Status    │        │
                   │  │  Orchestrator   │    │   Component     │        │
                   │  └──────┬──────────┘    └─────────────────┘        │
                   │         │                                          │
                   │         ├──────────────▶┌─────────────────┐        │
                   │         │               │  Vector Store   │        │
                   │         │               │   Health Check  │        │
                   │         │               └─────────────────┘        │
                   │         │                                          │
                   │         ├──────────────▶┌─────────────────┐        │
                   │         │               │  Encryption     │        │
                   │         │               │   Service Check │        │
                   │         │               └─────────────────┘        │
                   │         │                                          │
                   │         ├──────────────▶┌─────────────────┐        │
                   │         │               │   Disk Space    │        │
                   │         │               │     Check       │        │
                   │         │               └─────────────────┘        │
                   │         │                                          │
                   │         ▼                                          │
                   │  ┌─────────────────┐                               │
                   │  │ Health Status   │                               │
                   │  │  Aggregator     │                               │
                   │  └──────┬──────────┘                               │
                   │         │                                          │
                   │         ▼                                          │
┌─────────────┐    │  ┌─────────────────┐                               │
│   Client    │◄───┼──│ JSON Response   │                               │
│ Response    │    │  │                 │                               │
│             │    │  │ {               │                               │
│ 200 or 503  │    │  │   "status":     │                               │
└─────────────┘    │  │     "healthy",  │                               │
                   │  │   "checks": {}  │                               │
                   │  │ }               │                               │
                   │  └─────────────────┘                               │
                   └─────────────────────────────────────────────────────┘
```

## 8. Caching Component Interactions

### 8.1 Cache Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Caching Components                               │
│                                                                         │
│  ┌─────────────────┐              ┌─────────────────┐                   │
│  │   Memory        │              │   Embedding     │                   │
│  │   Service       │              │   Service       │                   │
│  └──────┬──────────┘              └──────┬──────────┘                   │
│         │                                │                              │
│         │ 1. Check cache                 │ 2. Check embedding cache      │
│         ▼                                ▼                              │
│  ┌─────────────────┐              ┌─────────────────┐                   │
│  │  Query Result   │              │  Embedding      │                   │
│  │     Cache       │              │     Cache       │                   │
│  │                 │              │                 │                   │
│  │ LRU(1000)       │              │ LRU(500)        │                   │
│  │ TTL: 1 hour     │              │ TTL: 24 hours   │                   │
│  └──────┬──────────┘              └──────┬──────────┘                   │
│         │                                │                              │
│         │ Cache miss                     │ Cache miss                   │
│         ▼                                ▼                              │
│  ┌─────────────────┐              ┌─────────────────┐                   │
│  │   Vector        │              │ SentenceTrans-  │                   │
│  │    Store        │              │  formers Model  │                   │
│  │  (ChromaDB)     │              │                 │                   │
│  └──────┬──────────┘              └──────┬──────────┘                   │
│         │                                │                              │
│         │ 3. Fetch from storage          │ 4. Generate embedding         │
│         ▼                                ▼                              │
│  ┌─────────────────┐              ┌─────────────────┐                   │
│  │  Update Cache   │              │  Update Cache   │                   │
│  │   with Result   │              │  with Embedding │                   │
│  └─────────────────┘              └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 9. Monitoring and Observability Interactions

### 9.1 Monitoring Component Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Monitoring Architecture                              │
│                                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   Request   │───▶│   Middleware    │───▶│    Metrics      │              │
│  │ Processing  │    │   Interceptor   │    │   Collector     │              │
│  └─────────────┘    └─────────────────┘    └──────┬──────────┘              │
│                                                    │                        │
│                                                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Metrics Storage                                  │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │  Request    │  │  Response   │  │   Error     │  │ Performance │ │   │
│  │  │  Metrics    │  │   Times     │  │   Counts    │  │   Metrics   │ │   │
│  │  │             │  │             │  │             │  │             │ │   │
│  │  │ • Count     │  │ • Duration  │  │ • By type   │  │ • Memory    │ │   │
│  │  │ • Rate      │  │ • P95/P99   │  │ • By route  │  │ • CPU       │ │   │
│  │  │ • By route  │  │ • Avg       │  │ • Frequency │  │ • Disk I/O  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Monitoring Endpoints                             │   │
│  │                                                                     │   │
│  │  GET /metrics     - Prometheus format metrics                      │   │
│  │  GET /health      - System health status                           │   │
│  │  GET /stats       - Usage statistics                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 10. Security Component Interactions

### 10.1 Security Layer Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Security Architecture                               │
│                                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   Client    │───▶│   API Gateway   │───▶│  Authentication │              │
│  │   Request   │    │   (FastAPI)     │    │   Middleware    │              │
│  └─────────────┘    └─────────────────┘    └──────┬──────────┘              │
│                                                    │                        │
│                     Future: API Key Auth           ▼                        │
│                                          ┌─────────────────┐                │
│                                          │  Authorization  │                │
│                                          │   Component     │                │
│                                          └──────┬──────────┘                │
│                                                 │                           │
│                                                 ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Data Security Layer                              │   │
│  │                                                                     │   │
│  │  ┌─────────────┐                              ┌─────────────┐       │   │
│  │  │    Input    │                              │   Output    │       │   │
│  │  │ Validation  │                              │ Sanitization│       │   │
│  │  │             │                              │             │       │   │
│  │  │ • Schema    │                              │ • Remove    │       │   │
│  │  │   checks    │                              │   keys      │       │   │
│  │  │ • Size      │                              │ • Mask      │       │   │
│  │  │   limits    │                              │   content   │       │   │
│  │  └─────────────┘                              └─────────────┘       │   │
│  │         │                                              ▲             │   │
│  │         ▼                                              │             │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                Encryption Service                           │   │   │
│  │  │                                                             │   │   │
│  │  │  encrypt_content() ────▶ AES-256-GCM ────▶ decrypt_content()│   │   │
│  │  │                                                             │   │   │
│  │  │  Key Management:                                            │   │   │
│  │  │  • Environment variable loading                             │   │   │
│  │  │  • Key rotation (future)                                    │   │   │
│  │  │  • HSM integration (future)                                 │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Summary

The MemoryLink component interaction diagrams demonstrate:

1. **Clear Separation of Concerns**: Each layer has distinct responsibilities
2. **Loose Coupling**: Components interact through well-defined interfaces
3. **Error Handling**: Centralized error processing across all components
4. **Configuration Management**: Hierarchical config loading and validation
5. **Health Monitoring**: Comprehensive health checks across all components
6. **Caching Strategy**: Multi-layer caching for performance optimization
7. **Security Integration**: Security concerns addressed at every layer
8. **Observability**: Monitoring and logging integrated throughout

These interactions support the local-first, privacy-focused architecture while maintaining scalability and maintainability for the MemoryLink system.

---

*Component Interaction Design - SPARC Phase  
System Architect: Claude (Sonnet 4)  
Integration Status: Ready for Implementation*