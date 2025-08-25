# MemoryLink Architecture Specification
*SPARC Architecture Phase - Technical System Design*

## Executive Summary

MemoryLink is a local-first personal memory system that provides a unified memory layer for AI agents and developer tools. This architecture specification defines a scalable, secure, and maintainable system design using FastAPI, ChromaDB, and Docker containerization.

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────────────────────────┐    ┌──────────────────┐
│   Client Apps   │    │        MemoryLink Core API          │    │  Storage Layer   │
│                 │    │                                     │    │                  │
│ ┌─────────────┐ │    │ ┌─────────────┐ ┌─────────────────┐ │    │ ┌──────────────┐ │
│ │ IDE Plugins │ │    │ │   Routes    │ │   Services      │ │    │ │   ChromaDB   │ │
│ │             │◄────►│ │ /add_memory │ │ Memory Service  │◄────►│ │ (Vectors +   │ │
│ │ AI Agents   │ │    │ │ /search     │ │ Embedding Svc   │ │    │ │  Metadata)   │ │
│ │             │ │    │ │ /healthz    │ │ Encryption Svc  │ │    │ │              │ │
│ │ CLI Tools   │ │    │ └─────────────┘ └─────────────────┘ │    │ └──────────────┘ │
│ └─────────────┘ │    │                                     │    │                  │
└─────────────────┘    └─────────────────────────────────────┘    └──────────────────┘
```

### 1.2 Core Components

1. **MemoryLink API Server**: FastAPI-based REST service handling HTTP requests
2. **Vector Store**: ChromaDB for semantic search and embedding storage
3. **Encryption Layer**: Application-level AES-256 encryption for content security
4. **Service Layer**: Business logic for memory operations and data processing
5. **Client Interfaces**: REST API, CLI tools, and future SDK support

## 2. Technology Stack Selection

### 2.1 Primary Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **API Framework** | FastAPI + Uvicorn | Async support, auto-documentation, fast development |
| **Vector Database** | ChromaDB | Embedded solution, metadata support, SQLite backend |
| **Embedding Engine** | SentenceTransformers | Local inference, privacy-first, CPU optimized |
| **Encryption** | PyCryptodome | Battle-tested, AES-256-GCM support |
| **Containerization** | Docker + Compose | Consistent deployment, easy scaling |
| **Metadata Storage** | SQLite (via ChromaDB) | Embedded, no external dependencies |

### 2.2 Alternative Options Considered

| Component | Primary Choice | Alternative | Decision Factor |
|-----------|---------------|-------------|-----------------|
| **Vector DB** | ChromaDB | Qdrant, Weaviate | Embedded simplicity |
| **Embedding** | SentenceTransformers | OpenAI API | Privacy & local-first |
| **Web Framework** | FastAPI | Flask, Django | Performance & modern features |
| **Database** | SQLite | PostgreSQL | MVP simplicity, no setup |

## 3. Component Architecture

### 3.1 MemoryLink API Server

**Responsibilities:**
- HTTP request/response handling
- Input validation and sanitization
- Authentication (future: API keys)
- Error handling and logging
- Health check endpoints

**Technology:** FastAPI with Uvicorn ASGI server

**Key Features:**
- Automatic OpenAPI documentation
- Async request handling
- Pydantic model validation
- CORS support for future web clients

### 3.2 Vector Store & Embedding System

**ChromaDB Integration:**
```python
# Simplified architecture
class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./data/chroma")
        self.collection = self.client.get_or_create_collection("memories")
    
    def add_memory(self, id: str, text: str, embedding: List[float], metadata: dict):
        self.collection.add(
            ids=[id],
            embeddings=[embedding],
            documents=[text],  # Encrypted
            metadatas=[metadata]
        )
    
    def search_memories(self, query_embedding: List[float], top_k: int = 10):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
```

**Embedding Pipeline:**
1. Text input → SentenceTransformers model
2. Generate 384-dimensional vectors (all-MiniLM-L6-v2)
3. Store in ChromaDB with metadata
4. Support fallback to OpenAI embeddings (optional)

### 3.3 Encryption Layer

**Security Architecture:**
```python
class EncryptionService:
    def __init__(self, key: bytes):
        self.key = key
    
    def encrypt_content(self, plaintext: str) -> str:
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def decrypt_content(self, encrypted: str) -> str:
        data = base64.b64decode(encrypted)
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

**Key Management:**
- Environment variable: `MEMORYLINK_ENCRYPTION_KEY`
- KDF from passphrase: PBKDF2 with salt
- Future: Hardware security modules, user-provided keys

### 3.4 Service Layer Architecture

**Memory Service:**
```python
class MemoryService:
    def __init__(self, vector_store, encryption_service, embedding_service):
        self.vector_store = vector_store
        self.encryption = encryption_service
        self.embeddings = embedding_service
    
    async def add_memory(self, content: str, metadata: dict) -> str:
        # 1. Generate embedding
        embedding = await self.embeddings.generate(content)
        
        # 2. Encrypt content
        encrypted_content = self.encryption.encrypt_content(content)
        
        # 3. Store in vector database
        memory_id = str(uuid.uuid4())
        await self.vector_store.add_memory(
            id=memory_id,
            text=encrypted_content,
            embedding=embedding,
            metadata=metadata
        )
        
        return memory_id
    
    async def search_memories(self, query: str, filters: dict = None) -> List[Memory]:
        # 1. Generate query embedding
        query_embedding = await self.embeddings.generate(query)
        
        # 2. Vector similarity search
        results = await self.vector_store.search_memories(query_embedding)
        
        # 3. Decrypt results
        memories = []
        for result in results:
            decrypted_content = self.encryption.decrypt_content(result['document'])
            memories.append(Memory(
                id=result['id'],
                content=decrypted_content,
                metadata=result['metadata'],
                score=result['distance']
            ))
        
        return memories
```

## 4. Data Flow Architecture

### 4.1 Add Memory Flow

```
Client Request → Input Validation → Generate Embedding → Encrypt Content → Store (Vector + Metadata) → Return ID
```

**Detailed Steps:**
1. **HTTP Request**: `POST /add_memory` with JSON payload
2. **Validation**: Pydantic models validate input structure
3. **Embedding Generation**: SentenceTransformers processes text
4. **Encryption**: AES-256-GCM encrypts content with user key
5. **Storage**: ChromaDB stores vector, encrypted text, and metadata
6. **Response**: Return memory ID and status

### 4.2 Search Memory Flow

```
Search Query → Generate Query Embedding → Vector Similarity Search → Decrypt Results → Return Ranked Results
```

**Detailed Steps:**
1. **HTTP Request**: `GET /search_memory` with query parameters
2. **Query Processing**: Generate embedding for search terms
3. **Vector Search**: ChromaDB performs cosine similarity search
4. **Result Filtering**: Apply metadata filters (tags, date ranges)
5. **Decryption**: Decrypt content for matching memories
6. **Ranking**: Return results sorted by relevance score

### 4.3 Authentication Flow (Future)

```
API Key → Validation → Rate Limiting → Request Processing
```

## 5. Project Structure Design

### 5.1 Directory Organization

```
memorylink/
├── app/                          # Main application code
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── routes/                   # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── memory.py             # Memory CRUD operations
│   │   └── health.py             # Health check endpoints
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── memory_service.py     # Core memory operations
│   │   ├── embedding_service.py  # Embedding generation
│   │   └── encryption_service.py # Encryption/decryption
│   ├── db/                       # Database and storage
│   │   ├── __init__.py
│   │   ├── vector_store.py       # ChromaDB wrapper
│   │   └── migrations.py         # Schema migrations
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── memory.py             # Memory data structures
│   │   └── requests.py           # API request/response models
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── logging.py            # Logging configuration
│       └── exceptions.py         # Custom exception classes
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data and fixtures
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── architecture/             # Architecture diagrams
│   └── user-guide/               # User documentation
├── scripts/                      # Utility scripts
│   ├── setup.py                  # Initial setup
│   └── populate_test_data.py     # Test data generation
├── config/                       # Configuration files
│   ├── development.yml
│   ├── production.yml
│   └── docker.yml
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Multi-container orchestration
├── Makefile                      # Build and development tasks
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Python project configuration
└── README.md                     # Project documentation
```

### 5.2 File Size Guidelines

**Adherence to 500-line limit:**
- Each module focused on single responsibility
- Service classes: ~200-300 lines with clear methods
- Route handlers: ~100-150 lines per endpoint group
- Model definitions: ~50-100 lines per file
- Utility functions: ~200-300 lines with related functions

## 6. Security Architecture

### 6.1 Data Protection Strategy

**Encryption at Rest:**
- All memory content encrypted with AES-256-GCM
- Metadata selectively encrypted (content-bearing fields)
- Embeddings stored unencrypted (required for vector search)
- Database files protected by filesystem permissions

**Key Management:**
- Development: Environment variable or config file
- Production: External key management service
- Future: Hardware security modules, user-controlled keys

**Local-First Security:**
- Default binding to localhost (127.0.0.1) only
- No external network dependencies
- Optional TLS for remote deployment
- API key authentication for network exposure

### 6.2 Privacy Architecture

**Data Sovereignty:**
- All data remains on user's machine by default
- No telemetry or analytics collection
- Optional cloud sync with end-to-end encryption
- User controls all aspects of data sharing

**Audit and Compliance:**
- Operation logging without sensitive content
- Clear data retention policies
- GDPR compliance through local storage
- Export functionality for data portability

## 7. Scalability Design

### 7.1 Horizontal Scaling Patterns

**Stateless API Design:**
- No session state stored in application memory
- All state persisted in databases
- Container-ready for orchestration
- Load balancer friendly

**Database Scaling:**
- ChromaDB: Single-node for MVP, distributed options available
- SQLite: Sufficient for single-user, PostgreSQL for multi-user
- Vector index partitioning for large datasets
- Read replica support for search-heavy workloads

### 7.2 Performance Optimization

**Caching Strategy:**
```python
# Embedding cache for frequently searched terms
class EmbeddingCache:
    def __init__(self, max_size: int = 1000):
        self.cache = LRUCache(max_size)
    
    async def get_embedding(self, text: str) -> List[float]:
        if text in self.cache:
            return self.cache[text]
        
        embedding = await self.model.encode(text)
        self.cache[text] = embedding
        return embedding
```

**Database Optimization:**
- Connection pooling for concurrent requests
- Index optimization for metadata queries
- Batch operations for bulk insertions
- Async I/O for non-blocking operations

### 7.3 Future Kubernetes Architecture

**Container Strategy:**
- Stateless application containers
- Persistent volumes for data storage
- ConfigMaps for configuration management
- Secrets for encryption keys

**Scaling Deployment:**
```yaml
# Future Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memorylink-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memorylink-api
  template:
    spec:
      containers:
      - name: api
        image: memorylink:latest
        env:
        - name: MEMORYLINK_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: memorylink-secrets
              key: encryption-key
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
```

## 8. API Architecture & Interface Design

### 8.1 REST API Specification

**Core Endpoints:**

```yaml
# OpenAPI 3.0 Specification (excerpt)
paths:
  /add_memory:
    post:
      summary: Add a new memory entry
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                content:
                  type: string
                  description: Memory content to store
                tags:
                  type: array
                  items:
                    type: string
                metadata:
                  type: object
                  additionalProperties: true
      responses:
        201:
          description: Memory successfully added
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                  status:
                    type: string
                    enum: [success]

  /search_memory:
    get:
      summary: Search memories by content or metadata
      parameters:
        - name: query
          in: query
          schema:
            type: string
          description: Search query text
        - name: tags
          in: query
          schema:
            type: array
            items:
              type: string
          description: Filter by tags
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
            maximum: 100
      responses:
        200:
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  memories:
                    type: array
                    items:
                      $ref: '#/components/schemas/Memory'
                  total:
                    type: integer
```

### 8.2 Model Context Protocol (MCP) Compliance

**Standardized Memory Interface:**
```python
# MCP-inspired memory interface
class MCPMemoryInterface:
    async def add_resource(self, resource: MCPResource) -> str:
        """Add memory as MCP resource"""
        return await self.memory_service.add_memory(
            content=resource.content,
            metadata={
                "uri": resource.uri,
                "mime_type": resource.mimeType,
                "description": resource.description
            }
        )
    
    async def list_resources(self, cursor: Optional[str] = None) -> MCPResourceList:
        """List memories as MCP resources"""
        memories = await self.memory_service.list_memories(cursor=cursor)
        return MCPResourceList(
            resources=[
                MCPResource(
                    uri=f"memory://{m.id}",
                    name=m.title or m.id,
                    description=m.summary,
                    mimeType="text/plain"
                )
                for m in memories
            ]
        )
```

## 9. Development & Operations Architecture

### 9.1 Container Architecture

**Dockerfile Strategy:**
```dockerfile
# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Application setup
WORKDIR /app
COPY app/ ./app/
COPY config/ ./config/

# Security and performance
RUN groupadd -r memorylink && useradd -r -g memorylink memorylink
USER memorylink

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Docker Compose Configuration:**
```yaml
version: '3.8'
services:
  memorylink-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MEMORYLINK_ENCRYPTION_KEY=${MEMORYLINK_ENCRYPTION_KEY}
      - MEMORYLINK_DATA_PATH=/app/data
      - MEMORYLINK_LOG_LEVEL=INFO
    volumes:
      - memorylink_data:/app/data
      - memorylink_logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  memorylink_data:
    driver: local
  memorylink_logs:
    driver: local

networks:
  default:
    driver: bridge
```

### 9.2 Configuration Management

**Environment-Based Configuration:**
```python
# config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    
    # Security settings
    encryption_key: str
    api_key: Optional[str] = None
    
    # Data settings
    data_path: str = "./data"
    max_memory_size: int = 10_000_000  # 10MB
    max_memories: int = 100_000
    
    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    
    # ChromaDB settings
    chroma_path: str = "./data/chroma"
    
    class Config:
        env_prefix = "MEMORYLINK_"
        env_file = ".env"

settings = Settings()
```

### 9.3 Monitoring & Observability

**Health Check System:**
```python
@router.get("/healthz")
async def health_check():
    """System health check endpoint"""
    checks = {
        "api": "healthy",
        "vector_store": await vector_store.health_check(),
        "encryption": await encryption_service.health_check(),
        "disk_space": await check_disk_space()
    }
    
    status = "healthy" if all(v == "healthy" for v in checks.values()) else "unhealthy"
    
    return {
        "status": status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "version": __version__
    }
```

**Logging Architecture:**
```python
# utils/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging(level: str = "INFO"):
    """Configure structured logging"""
    logger = logging.getLogger("memorylink")
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))
    
    return logger
```

## 10. Architecture Decision Records (ADRs)

### ADR-001: Vector Database Selection

**Status:** Accepted  
**Date:** 2025-08-24

**Decision:** Use ChromaDB as the primary vector database for the MVP.

**Context:** Need embedded vector storage with metadata support for local-first architecture.

**Options Considered:**
1. ChromaDB (embedded SQLite backend)
2. Qdrant (external service)
3. Weaviate (external service)
4. Faiss + SQLite (custom implementation)

**Decision Factors:**
- **Simplicity:** ChromaDB requires no external services
- **Integration:** Native Python integration with metadata support
- **Performance:** Sufficient for MVP scale (< 100k memories)
- **Persistence:** Built-in SQLite persistence
- **Migration Path:** Can migrate to distributed solutions later

**Consequences:**
- ✅ Simple deployment and development
- ✅ No external service dependencies
- ✅ Automatic metadata management
- ❌ Single-node scaling limitations
- ❌ Limited advanced vector operations

### ADR-002: Encryption Strategy

**Status:** Accepted  
**Date:** 2025-08-24

**Decision:** Implement application-level encryption using AES-256-GCM for memory content.

**Context:** Privacy-first architecture requires encryption at rest for sensitive memory data.

**Options Considered:**
1. Application-level encryption (chosen)
2. Database-level encryption (SQLCipher)
3. Filesystem encryption (OS-level)
4. No encryption (rejected for privacy reasons)

**Decision Factors:**
- **Granular Control:** Application-level allows selective encryption
- **Portability:** Works across different deployment environments
- **Key Management:** Full control over key lifecycle
- **Performance:** Minimal overhead with modern AES implementations

**Consequences:**
- ✅ Maximum privacy control
- ✅ Portable across environments
- ✅ Selective encryption (metadata vs content)
- ❌ Additional complexity in application layer
- ❌ Key management responsibility

### ADR-003: Local-First Architecture

**Status:** Accepted  
**Date:** 2025-08-24

**Decision:** Design system with local-first principles, no cloud dependencies by default.

**Context:** User privacy and data sovereignty are core requirements.

**Architectural Implications:**
- Default deployment binds to localhost only
- All data stored locally by default
- Cloud sync designed as optional extension
- No external API dependencies for core functionality
- Embedding models run locally (CPU-optimized)

**Trade-offs:**
- ✅ Complete user data control
- ✅ Works offline
- ✅ No vendor lock-in
- ❌ Limited collaboration features
- ❌ Higher local resource requirements

## 11. Future Architecture Considerations

### 11.1 Multi-User Extensions

**User Namespace Design:**
```python
class MultiUserMemoryService:
    async def add_memory(self, user_id: str, content: str, metadata: dict):
        # Add user_id to all operations
        memory_metadata = {**metadata, "user_id": user_id}
        return await self.single_user_service.add_memory(content, memory_metadata)
    
    async def search_memories(self, user_id: str, query: str):
        # Filter by user_id in metadata
        filters = {"user_id": user_id}
        return await self.single_user_service.search_memories(query, filters)
```

### 11.2 Cloud Sync Architecture

**Hybrid Local/Cloud Design:**
```python
class CloudSyncService:
    async def sync_to_cloud(self, user_key: bytes):
        # Encrypt with user-controlled key before cloud storage
        local_memories = await self.local_service.get_all_memories()
        
        for memory in local_memories:
            encrypted_memory = await self.encrypt_for_cloud(memory, user_key)
            await self.cloud_storage.upload(encrypted_memory)
    
    async def sync_from_cloud(self, user_key: bytes):
        # Download and decrypt with user key
        cloud_memories = await self.cloud_storage.download_all()
        
        for encrypted_memory in cloud_memories:
            memory = await self.decrypt_from_cloud(encrypted_memory, user_key)
            await self.local_service.merge_memory(memory)
```

### 11.3 Advanced Search Features

**Planned Extensions:**
- Temporal search (memories from specific time periods)
- Concept clustering (group related memories)
- Memory summarization (AI-generated summaries of memory sets)
- Cross-memory relationship detection
- Automated tagging and categorization

## 12. Implementation Roadmap

### Phase 1: Core MVP (Weeks 1-4)
- [x] Project structure and scaffolding
- [ ] FastAPI server with basic endpoints
- [ ] ChromaDB integration
- [ ] Encryption service implementation
- [ ] Basic CLI interface
- [ ] Docker containerization
- [ ] Unit and integration tests

### Phase 2: Production Readiness (Weeks 5-8)
- [ ] Performance optimization
- [ ] Advanced error handling
- [ ] Comprehensive logging
- [ ] Security hardening
- [ ] API documentation
- [ ] User documentation with gamification
- [ ] Load testing and optimization

### Phase 3: Advanced Features (Weeks 9-12)
- [ ] Multi-user support
- [ ] Advanced search features
- [ ] SDK development (Python, JavaScript)
- [ ] IDE integrations (VS Code, etc.)
- [ ] Kubernetes deployment templates
- [ ] Cloud sync preparation

## Conclusion

This architecture specification provides a comprehensive foundation for building MemoryLink as a scalable, secure, and maintainable local-first memory system. The design emphasizes:

1. **Privacy First**: Local storage with application-level encryption
2. **Developer Experience**: Modern FastAPI with auto-documentation
3. **Scalability**: Stateless design ready for container orchestration
4. **Simplicity**: Embedded databases and minimal external dependencies
5. **Extensibility**: Clean architecture supporting future enhancements

The architecture balances immediate MVP needs with long-term scalability requirements, ensuring MemoryLink can evolve from a single-user tool to an enterprise-ready memory platform while maintaining its core privacy and local-first principles.

---

*Architecture designed using SPARC methodology  
System Architect: Claude (Sonnet 4)  
Review Status: Ready for Implementation Phase*