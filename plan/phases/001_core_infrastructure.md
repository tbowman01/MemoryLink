# Phase 1: Core Infrastructure Setup

## Overview
This phase establishes the foundational infrastructure for MemoryLink, including project scaffolding, development environment setup, basic API server, and containerization groundwork.

## Objectives
- Create modular project structure
- Set up FastAPI server with basic endpoints
- Configure Docker development environment
- Establish data models and schemas
- Implement configuration management
- Set up logging and monitoring basics

## Implementation Tasks

### 1.1 Project Scaffolding (Day 1-2)

#### Directory Structure
```
MemoryLink/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration management
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── routes/              # Route handlers
│   │   │   ├── __init__.py
│   │   │   ├── memory.py       # Memory endpoints
│   │   │   └── health.py       # Health check endpoints
│   │   └── dependencies.py     # Shared dependencies
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   ├── security.py         # Security utilities
│   │   └── constants.py        # Application constants
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── memory.py           # Memory data models
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/                # Business services
│   │   ├── __init__.py
│   │   └── memory_service.py   # Memory operations
│   └── db/                      # Database layer
│       ├── __init__.py
│       ├── base.py             # Database base classes
│       └── session.py          # Database sessions
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py            # Test configuration
├── scripts/                     # Utility scripts
│   ├── setup.py
│   └── seed_data.py
├── docker/                      # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements/                # Python dependencies
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/                      # Configuration files
│   ├── .env.example
│   └── settings.yaml
├── docs/                        # Documentation
│   ├── api/                    # API documentation
│   └── setup/                  # Setup guides
├── Makefile                     # Development commands
├── README.md                    # Project documentation
└── .gitignore
```

#### Key Files to Create

**app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import memory, health
from app.config import settings

app = FastAPI(
    title="MemoryLink",
    description="Local-first personal memory layer for AI agents",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(memory.router, prefix="/api/v1", tags=["memory"])

@app.on_event("startup")
async def startup_event():
    # Initialize services
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup
    pass
```

### 1.2 Configuration Management (Day 2-3)

#### Environment Variables
```env
# .env.example
MEMORYLINK_ENV=development
MEMORYLINK_HOST=0.0.0.0
MEMORYLINK_PORT=8080
MEMORYLINK_DATA_PATH=/data
MEMORYLINK_LOG_LEVEL=INFO
MEMORYLINK_ENCRYPTION_ENABLED=true
MEMORYLINK_ENCRYPTION_KEY=
MEMORYLINK_VECTOR_DB_PATH=/data/vector
MEMORYLINK_METADATA_DB_PATH=/data/metadata.db
```

#### Configuration Class
```python
# app/config.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "MemoryLink"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Security
    encryption_enabled: bool = True
    encryption_key: str = ""
    api_key_enabled: bool = False
    
    # Database
    data_path: str = "/data"
    vector_db_path: str = "/data/vector"
    metadata_db_path: str = "/data/metadata.db"
    
    # Performance
    max_memory_size: int = 10000
    embedding_batch_size: int = 32
    search_top_k: int = 10
    
    class Config:
        env_prefix = "MEMORYLINK_"
        env_file = ".env"

settings = Settings()
```

### 1.3 Data Models (Day 3-4)

#### Pydantic Schemas
```python
# app/models/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict

class MemoryBase(BaseModel):
    text: str = Field(..., description="Memory content")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, any] = Field(default_factory=dict)

class MemoryCreate(MemoryBase):
    user_id: Optional[str] = "default"
    session_id: Optional[str] = None

class MemoryResponse(MemoryBase):
    id: str
    timestamp: datetime
    user_id: str
    embedding_id: Optional[str]
    
class SearchQuery(BaseModel):
    query: str
    tags: Optional[List[str]] = None
    user_id: Optional[str] = "default"
    top_k: int = Field(10, ge=1, le=100)
    threshold: float = Field(0.5, ge=0, le=1)

class SearchResult(BaseModel):
    memories: List[MemoryResponse]
    total: int
    query_time_ms: float
```

### 1.4 Basic API Implementation (Day 4-5)

#### Health Check Endpoint
```python
# app/api/routes/health.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "MemoryLink"
    }

@router.get("/readiness")
async def readiness_check():
    # Check if all services are ready
    return {"ready": True}
```

#### Memory Endpoints (Stub)
```python
# app/api/routes/memory.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import MemoryCreate, MemoryResponse, SearchQuery, SearchResult

router = APIRouter()

@router.post("/memory", response_model=MemoryResponse)
async def add_memory(memory: MemoryCreate):
    # Stub implementation
    return MemoryResponse(
        id="temp-id",
        text=memory.text,
        tags=memory.tags,
        metadata=memory.metadata,
        timestamp=datetime.utcnow(),
        user_id=memory.user_id
    )

@router.get("/memory/search", response_model=SearchResult)
async def search_memory(query: SearchQuery):
    # Stub implementation
    return SearchResult(
        memories=[],
        total=0,
        query_time_ms=0.0
    )
```

### 1.5 Docker Configuration (Day 5-6)

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

# Copy application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  memorylink:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
      - ./config/.env:/app/.env
    environment:
      - MEMORYLINK_ENV=development
    networks:
      - memorylink-network

networks:
  memorylink-network:
    driver: bridge

volumes:
  memory-data:
```

### 1.6 Makefile Commands (Day 6)

```makefile
# Makefile
.PHONY: help start stop build test clean

help:
	@echo "MemoryLink Development Commands"
	@echo "================================"
	@echo "make start    - Start the MemoryLink server"
	@echo "make stop     - Stop the MemoryLink server"
	@echo "make build    - Build Docker containers"
	@echo "make test     - Run test suite"
	@echo "make clean    - Clean up containers and data"

start:
	@echo "🚀 Starting MemoryLink..."
	docker-compose up -d
	@echo "✅ MemoryLink is running at http://localhost:8080"
	@echo "📚 API docs available at http://localhost:8080/docs"

stop:
	@echo "🛑 Stopping MemoryLink..."
	docker-compose down

build:
	@echo "🔨 Building MemoryLink containers..."
	docker-compose build

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	rm -rf data/*
```

### 1.7 Basic Testing Framework (Day 6-7)

#### Test Configuration
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_memory():
    return {
        "text": "Test memory content",
        "tags": ["test", "sample"],
        "metadata": {"source": "test"}
    }
```

#### Basic Tests
```python
# tests/unit/test_health.py
def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# tests/unit/test_memory.py
def test_add_memory(client, sample_memory):
    response = client.post("/api/v1/memory", json=sample_memory)
    assert response.status_code == 200
    assert response.json()["text"] == sample_memory["text"]
```

## Dependencies

### Python Requirements

**requirements/base.txt**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
pyyaml==6.0.1
httpx==0.25.0
python-multipart==0.0.6
```

**requirements/dev.txt**
```
-r base.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.0
```

## Validation Checklist

### Infrastructure
- [ ] Project structure created
- [ ] FastAPI server running
- [ ] Basic endpoints responding
- [ ] Docker container builds
- [ ] Docker Compose works
- [ ] Makefile commands functional

### Code Quality
- [ ] Configuration management working
- [ ] Data models defined
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Tests passing

### Documentation
- [ ] API documentation auto-generated
- [ ] README updated
- [ ] Setup instructions clear
- [ ] Environment variables documented

## Deliverables

1. **Working API Server**
   - Health check endpoint
   - Basic memory endpoints (stubs)
   - Auto-generated API docs

2. **Docker Environment**
   - Dockerfile building successfully
   - Docker Compose configuration
   - Volume persistence

3. **Development Tools**
   - Makefile with common commands
   - Test framework setup
   - Configuration management

## Success Metrics

- API server starts without errors
- Health endpoint returns 200 OK
- Docker container runs successfully
- Basic tests pass
- API documentation accessible

## Known Issues & Mitigations

1. **Issue**: Cross-platform Docker compatibility
   **Mitigation**: Test on Windows, macOS, and Linux

2. **Issue**: Port conflicts
   **Mitigation**: Make port configurable via environment

3. **Issue**: Volume permissions
   **Mitigation**: Handle permissions in Dockerfile

## Next Phase

With core infrastructure in place, Phase 2 will implement the actual memory layer functionality including:
- Vector database integration
- Embedding generation
- Encryption implementation
- Actual memory storage and retrieval