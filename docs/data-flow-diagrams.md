# MemoryLink Data Flow Architecture
*SPARC Architecture Phase - Data Flow and Component Interactions*

## Data Flow Overview

This document details the data flow patterns and component interactions within the MemoryLink architecture, showing how information moves through the system during key operations.

## 1. Add Memory Data Flow

### 1.1 High-Level Flow
```
Client → API Gateway → Memory Service → Embedding Service → Encryption Service → Vector Store → Response
```

### 1.2 Detailed Data Flow Diagram

```
┌─────────────┐     ┌─────────────────────────────────────────────────────────────┐
│   Client    │     │                    MemoryLink API Server                    │
│             │     │                                                             │
│ POST        │────▶│ ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│ /add_memory │     │ │   Routes    │──▶│   Memory     │──▶│   Embedding     │ │
│             │     │ │ (FastAPI)   │   │   Service    │   │   Service       │ │
│ {           │     │ └─────────────┘   └──────────────┘   └─────────────────┘ │
│  "content": │     │        │                 │                    │          │
│   "...",    │     │        │                 ▼                    ▼          │
│  "tags":    │     │        │         ┌──────────────┐   ┌─────────────────┐ │
│   [...]     │     │        │         │ Encryption   │   │ SentenceTrans-  │ │
│ }           │     │        │         │ Service      │   │ formers Model   │ │
└─────────────┘     │        │         └──────────────┘   └─────────────────┘ │
                    │        │                 │                    │          │
                    │        ▼                 ▼                    ▼          │
                    │ ┌─────────────────────────────────────────────────────┐ │
                    │ │                ChromaDB Vector Store                │ │
                    │ │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
                    │ │  │  Vectors    │  │   Metadata   │  │ Encrypted   │ │ │
                    │ │  │  [0.1, 0.2, │  │   {tags,     │  │  Content    │ │ │
                    │ │  │   ..., 0.n] │  │    timestamp}│  │  (AES-256)  │ │ │
                    │ │  └─────────────┘  └──────────────┘  └─────────────┘ │ │
                    │ └─────────────────────────────────────────────────────┘ │
                    └─────────────────────────────────────────────────────────┘
                                                    │
                    ┌───────────────────────────────▼─────────────────────────────┐
                    │                       Response                             │
                    │  {                                                        │
                    │    "id": "uuid-1234-5678-9abc",                          │
                    │    "status": "success",                                   │
                    │    "timestamp": "2025-08-24T20:15:00Z"                   │
                    │  }                                                        │
                    └───────────────────────────────────────────────────────────┘
```

### 1.3 Step-by-Step Process

1. **Client Request Processing** (10-50ms)
   - HTTP request validation
   - JSON payload parsing
   - Pydantic model validation
   - Authentication check (future)

2. **Memory Service Orchestration** (5-10ms)
   - Generate unique memory ID (UUID4)
   - Extract content and metadata
   - Initialize processing pipeline

3. **Embedding Generation** (100-500ms)
   - Load SentenceTransformers model
   - Tokenize input text
   - Generate 384-dimensional vector
   - Cache model in memory for subsequent requests

4. **Content Encryption** (1-5ms)
   - Generate random nonce (96-bit)
   - AES-256-GCM encryption of content
   - Base64 encoding for storage
   - Preserve metadata for search

5. **Vector Storage** (10-50ms)
   - Store embedding vector in ChromaDB
   - Save encrypted content as document
   - Index metadata for filtering
   - Persist to SQLite backend

6. **Response Generation** (1-5ms)
   - Success status confirmation
   - Return memory ID to client
   - Log operation (non-sensitive data)

### 1.4 Error Handling Flow

```
Input Error ──┐
              │
Model Error ──┼──▶ Error Handler ──▶ Structured Response
              │
Storage Error ─┘
```

## 2. Search Memory Data Flow

### 2.1 High-Level Flow
```
Search Query → Embedding Generation → Vector Search → Result Ranking → Content Decryption → Filtered Response
```

### 2.2 Detailed Search Flow Diagram

```
┌─────────────┐     ┌─────────────────────────────────────────────────────────────┐
│   Client    │     │                    MemoryLink API Server                    │
│             │     │                                                             │
│ GET         │────▶│ ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│ /search     │     │ │   Routes    │──▶│   Memory     │──▶│   Embedding     │ │
│ ?query=     │     │ │ (FastAPI)   │   │   Service    │   │   Service       │ │
│ "meeting"   │     │ └─────────────┘   └──────────────┘   └─────────────────┘ │
│ &tags=work  │     │                           │                    │          │
└─────────────┘     │                           ▼                    ▼          │
                    │                  ┌──────────────┐   ┌─────────────────┐ │
                    │                  │  Query       │   │ Generate Query  │ │
                    │                  │  Processing  │   │ Embedding       │ │
                    │                  └──────────────┘   └─────────────────┘ │
                    │                           │                    │          │
                    │                           ▼                    ▼          │
                    │ ┌─────────────────────────────────────────────────────┐ │
                    │ │                ChromaDB Vector Search               │ │
                    │ │                                                     │ │
                    │ │  Query Vector [0.1, 0.2, ..., 0.n]                 │ │
                    │ │           │                                         │ │
                    │ │           ▼                                         │ │
                    │ │  ┌─────────────────────────────────────────────┐   │ │
                    │ │  │          Cosine Similarity Search          │   │ │
                    │ │  │                                             │   │ │
                    │ │  │  Memory 1: 0.92 similarity                 │   │ │
                    │ │  │  Memory 2: 0.87 similarity                 │   │ │
                    │ │  │  Memory 3: 0.81 similarity                 │   │ │
                    │ │  └─────────────────────────────────────────────┘   │ │
                    │ └─────────────────────────────────────────────────────┘ │
                    │                           │                              │
                    │                           ▼                              │
                    │ ┌─────────────────────────────────────────────────────┐ │
                    │ │                Result Processing                    │ │
                    │ │                                                     │ │
                    │ │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │ │
                    │ │  │   Decrypt   │  │   Filter     │  │    Rank    │ │ │
                    │ │  │   Content   │  │  Metadata    │  │  Results   │ │ │
                    │ │  └─────────────┘  └──────────────┘  └────────────┘ │ │
                    │ └─────────────────────────────────────────────────────┘ │
                    └─────────────────────────────────────────────────────────┘
                                                    │
                    ┌───────────────────────────────▼─────────────────────────────┐
                    │                      Response                              │
                    │  {                                                        │
                    │    "memories": [                                          │
                    │      {                                                    │
                    │        "id": "uuid-1234...",                             │
                    │        "content": "Meeting notes about...",              │
                    │        "score": 0.92,                                    │
                    │        "metadata": {"tags": ["work", "meeting"]}         │
                    │      }                                                    │
                    │    ],                                                     │
                    │    "total": 3,                                           │
                    │    "query_time_ms": 156                                  │
                    │  }                                                        │
                    └───────────────────────────────────────────────────────────┘
```

### 2.3 Search Processing Steps

1. **Query Processing** (5-15ms)
   - Parse search parameters
   - Extract query text and filters
   - Validate input constraints

2. **Query Embedding Generation** (100-500ms)
   - Generate embedding for search query
   - Use same model as indexing
   - Cache frequent query embeddings

3. **Vector Similarity Search** (20-100ms)
   - Perform cosine similarity in ChromaDB
   - Apply metadata filters
   - Retrieve top-k similar vectors

4. **Result Processing** (10-50ms)
   - Decrypt content for matching memories
   - Apply additional filters
   - Rank by combined relevance score

5. **Response Formatting** (5-10ms)
   - Format results for API response
   - Include relevance scores
   - Add query performance metadata

## 3. System Initialization Flow

### 3.1 Application Startup Sequence

```
Container Start ──▶ Environment Load ──▶ Service Init ──▶ Health Check ──▶ Ready
```

### 3.2 Detailed Initialization Flow

```
┌─────────────────┐
│ Docker Container│
│ Startup         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Environment     │
│ Configuration   │
│ • Load .env     │
│ • Validate keys │
│ • Set defaults  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Service Layer   │
│ Initialization  │
│                 │
│ ┌─────────────┐ │
│ │ Embedding   │ │
│ │ Service     │ │
│ │ • Load model│ │
│ │ • Test gen  │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ Encryption  │ │
│ │ Service     │ │
│ │ • Load key  │ │
│ │ • Test ops  │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ Vector Store│ │
│ │ • Connect   │ │
│ │ • Create DB │ │
│ │ • Test ops  │ │
│ └─────────────┘ │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ FastAPI Server  │
│ Startup         │
│ • Mount routes  │
│ • Start uvicorn │
│ • Health check  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Service Ready   │
│ • Listen on 8080│
│ • Accept reqs   │
│ • Metrics on    │
└─────────────────┘
```

## 4. Data Persistence Patterns

### 4.1 ChromaDB Data Organization

```
┌─────────────────────────────────────────────────────────────┐
│                     ChromaDB Collection                     │
│                                                             │
│  Collection Name: "memories"                                │
│                                                             │
│  ┌─────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │     IDs     │  │    Embeddings    │  │    Documents    │ │
│  │             │  │                  │  │                 │ │
│  │ memory-001  │  │ [0.1, 0.2, ...] │  │ {encrypted_text}│ │
│  │ memory-002  │  │ [0.3, 0.1, ...] │  │ {encrypted_text}│ │
│  │ memory-003  │  │ [0.2, 0.4, ...] │  │ {encrypted_text}│ │
│  └─────────────┘  └──────────────────┘  └─────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Metadata                             │ │
│  │                                                         │ │
│  │  memory-001: {                                          │ │
│  │    "timestamp": "2025-08-24T20:15:00Z",                 │ │
│  │    "tags": ["work", "meeting"],                         │ │
│  │    "user_id": "default",                                │ │
│  │    "content_length": 256,                               │ │
│  │    "content_hash": "sha256:abc123..."                   │ │
│  │  }                                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Data Consistency Patterns

**ACID Properties in ChromaDB:**
- **Atomicity**: Individual operations are atomic
- **Consistency**: Schema validation ensures data integrity
- **Isolation**: Read-write isolation through SQLite WAL mode
- **Durability**: Automatic persistence to disk

**Backup and Recovery:**
```
Data Directory Structure:
/app/data/
├── chroma/
│   ├── chroma.sqlite3        # Metadata and configuration
│   ├── chroma.sqlite3-wal    # Write-ahead log
│   └── collections/
│       └── memories/
│           ├── data_level0.bin
│           ├── header.bin
│           └── length.bin
├── logs/
│   └── memorylink.log
└── backup/
    ├── daily/
    └── weekly/
```

## 5. Security Data Flow

### 5.1 Encryption Key Management Flow

```
┌─────────────────┐
│ Environment Var │
│ ENCRYPTION_KEY  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Key Validation  │
│ • Check length  │
│ • Test decrypt  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Memory Storage  │
│ • Secure buffer │
│ • No disk write │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Runtime Usage   │
│ • Encrypt ops   │
│ • Decrypt ops   │
└─────────────────┘
```

### 5.2 Content Encryption Flow

**Encryption Process:**
```python
# Simplified encryption data flow
plaintext = "Meeting notes about project X..."
    │
    ▼
nonce = os.urandom(16)  # 128-bit random nonce
    │
    ▼
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    │
    ▼
ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    │
    ▼
encrypted_data = base64.b64encode(nonce + tag + ciphertext)
    │
    ▼
stored_in_chromadb = encrypted_data.decode()
```

**Decryption Process:**
```python
# Simplified decryption data flow
encrypted_data = base64.b64decode(stored_data)
    │
    ▼
nonce = encrypted_data[:16]
tag = encrypted_data[16:32] 
ciphertext = encrypted_data[32:]
    │
    ▼
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    │
    ▼
plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    │
    ▼
return plaintext.decode()
```

## 6. Performance and Monitoring Data Flows

### 6.1 Request Monitoring Flow

```
┌─────────────┐    ┌─────────────────────────────────────┐    ┌─────────────┐
│   Client    │    │           API Middleware            │    │   Service   │
│   Request   │    │                                     │    │   Layer     │
└──────┬──────┘    │  ┌─────────────────────────────┐   │    └─────────────┘
       │           │  │     Request Timing         │   │
       │           │  │                             │   │
       ▼           │  │  start_time = now()         │   │
┌─────────────┐    │  │  request_id = uuid()        │   │    ┌─────────────┐
│ HTTP Request│────┼──┼─▶process_request()          │───┼───▶│   Process   │
│             │    │  │  end_time = now()           │   │    │   Request   │
└─────────────┘    │  │  duration = end - start     │   │    └─────────────┘
                   │  │                             │   │           │
                   │  └─────────────────────────────┘   │           │
                   │                                     │           ▼
                   │  ┌─────────────────────────────┐   │    ┌─────────────┐
                   │  │     Metrics Collection      │   │    │   Response  │
                   │  │                             │   │    │             │
                   │  │  log_request_metrics(       │◄──┼────┤             │
                   │  │    duration=duration,       │   │    │             │
                   │  │    status=200,             │   │    │             │
                   │  │    endpoint="/search"      │   │    │             │
                   │  │  )                         │   │    │             │
                   │  └─────────────────────────────┘   │    └─────────────┘
                   └─────────────────────────────────────┘
```

### 6.2 Health Check Data Flow

```
Health Check Request (/healthz)
    │
    ▼
┌─────────────────────────────────┐
│        Health Checks            │
│                                 │
│  ┌─────────────┐               │
│  │ API Status  │ ──────┐       │
│  └─────────────┘       │       │
│                        │       │
│  ┌─────────────┐       │       │
│  │Vector Store │ ──────┼──────▶│ ┌─────────────────┐
│  │ Connection  │       │       │ │ Aggregate Status│
│  └─────────────┘       │       │ │                 │
│                        │       │ │ All Healthy: 200│
│  ┌─────────────┐       │       │ │ Any Failed: 503 │
│  │ Encryption  │ ──────┘       │ └─────────────────┘
│  │ Service     │               │
│  └─────────────┘               │
│                                 │
│  ┌─────────────┐               │
│  │ Disk Space  │               │
│  └─────────────┘               │
└─────────────────────────────────┘
    │
    ▼
Response: {"status": "healthy", "checks": {...}}
```

## 7. Scalability Data Flow Patterns

### 7.1 Horizontal Scaling Data Flow

```
┌─────────────────┐    ┌─────────────────────────────────────┐
│  Load Balancer  │    │            API Instances            │
│                 │    │                                     │
│     Nginx       │    │  ┌─────────────┐  ┌─────────────┐   │
│       or        │    │  │MemoryLink   │  │MemoryLink   │   │
│   K8s Service   │    │  │API Pod 1    │  │API Pod 2    │   │
└─────────┬───────┘    │  └─────────┬───┘  └─────────┬───┘   │
          │            │            │                │       │
          │            └────────────┼────────────────┼───────┘
          │                         │                │
          ▼                         ▼                ▼
┌─────────────────┐    ┌─────────────────────────────────────┐
│ Request Router  │    │         Shared Storage              │
│                 │    │                                     │
│ Route by:       │    │  ┌─────────────────────────────┐   │
│ • Round Robin   │    │  │      ChromaDB Cluster        │   │
│ • Least Conn    │    │  │   (Future Distributed)       │   │
│ • Health        │    │  └─────────────────────────────┘   │
└─────────────────┘    │                                     │
                       │  ┌─────────────────────────────┐   │
                       │  │    Persistent Volume        │   │
                       │  │     /app/data shared        │   │
                       │  └─────────────────────────────┘   │
                       └─────────────────────────────────────┘
```

## 8. Integration Data Flow Patterns

### 8.1 MCP (Model Context Protocol) Integration Flow

```
┌─────────────────┐    ┌─────────────────────────────────────┐    ┌─────────────────┐
│   MCP Client    │    │          MemoryLink Server          │    │   Data Layer    │
│                 │    │                                     │    │                 │
│ IDE Extension   │    │  ┌─────────────────────────────┐   │    │                 │
│      or         │    │  │     MCP Adapter Layer       │   │    │                 │
│  AI Agent       │    │  │                             │   │    │                 │
└─────────┬───────┘    │  │  mcp_add_resource()         │   │    │                 │
          │            │  │  mcp_list_resources()       │   │    │                 │
          │            │  │  mcp_read_resource()        │   │    │                 │
          ▼            │  └─────────────┬───────────────┘   │    │                 │
┌─────────────────┐    │                │                   │    │                 │
│ MCP Protocol    │    │                ▼                   │    │                 │
│ JSON-RPC        │────┼──┐  ┌─────────────────────────────┐   │    │                 │
│ over HTTP       │    │  │  │    Memory Service Layer     │   │    │ ┌─────────────┐ │
└─────────────────┘    │  └─▶│                             │───┼───▶│ │ ChromaDB    │ │
                       │     │  add_memory()               │   │    │ │ Collections │ │
                       │     │  search_memories()          │   │    │ └─────────────┘ │
                       │     │  list_memories()            │   │    │                 │
                       │     └─────────────────────────────┘   │    └─────────────────┘
                       └─────────────────────────────────────────┘
```

### 8.2 CLI Integration Data Flow

```
┌─────────────────┐    ┌─────────────────────────────────────┐
│  Command Line   │    │        Local HTTP Client            │
│                 │    │                                     │
│  make start     │    │  curl -X POST localhost:8080/      │
│  make add_mem   │────┼─▶add_memory -d '{"content":"..."}'  │
│  make search    │    │                                     │
└─────────────────┘    │  curl -X GET localhost:8080/       │
                       │  search_memory?query=...            │
                       └─────────────┬───────────────────────┘
                                     │
                                     ▼
                       ┌─────────────────────────────────────┐
                       │         MemoryLink API              │
                       │                                     │
                       │  Same data flow as normal HTTP      │
                       │  requests, but from local CLI       │
                       └─────────────────────────────────────┘
```

## Summary

This data flow architecture demonstrates how MemoryLink processes information through its various components:

1. **Add Memory**: Client → Validation → Embedding → Encryption → Storage → Response
2. **Search Memory**: Query → Embedding → Vector Search → Decryption → Filtering → Response
3. **System Flow**: Startup → Configuration → Service Init → Health Check → Ready
4. **Security Flow**: Key Management → Content Encryption → Secure Storage
5. **Monitoring**: Request Tracking → Metrics Collection → Health Monitoring
6. **Integration**: MCP Protocol → Service Layer → Data Layer

The architecture ensures efficient data processing while maintaining security and scalability requirements for the MemoryLink local-first memory system.

---

*Data Flow Architecture - SPARC Phase  
System Architect: Claude (Sonnet 4)  
Coordination Status: Stored in Memory*