# 🛠️ MemoryLink Development Guide

> Complete guide for contributing to and extending MemoryLink

## 🚀 Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/your-username/MemoryLink.git
cd MemoryLink

# Development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Start development server
python src/main.py --reload
```

## 🏗️ Project Architecture

```
MemoryLink/
├── src/                    # Source code
│   ├── main.py            # FastAPI application
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── api/               # API endpoints
│   └── config.py          # Configuration
├── tests/                 # Test suite
├── scripts/               # CLI utilities
├── docs/                  # Documentation
├── examples/              # Integration examples
├── docker-compose.yml     # Development setup
├── Dockerfile             # Container definition
├── Makefile               # Gamified commands
└── requirements*.txt      # Dependencies
```

### 🧩 Core Components

#### 1. FastAPI Application (`src/main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MemoryLink",
    description="AI-powered personal memory layer",
    version="1.0.0"
)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
from api import memories, search
app.include_router(memories.router, prefix="/memories")
app.include_router(search.router, prefix="/search")
```

#### 2. Database Models (`src/models/memory.py`)
```python
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    embedding = Column(Text)  # Vector embedding as text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Memory(id={self.id}, content='{self.content[:50]}...')>"
```

#### 3. Services (`src/services/embedding_service.py`)
```python
import openai
from typing import List
import numpy as np

class EmbeddingService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.model = "text-embedding-ada-002"
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            response = await openai.Embedding.acreate(
                model=self.model,
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Embedding creation failed: {str(e)}")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        a = np.array(embedding1)
        b = np.array(embedding2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

#### 4. API Endpoints (`src/api/search.py`)
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.memory_service import MemoryService
from services.embedding_service import EmbeddingService

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    threshold: float = 0.3

class SearchResult(BaseModel):
    memory: dict
    similarity: float

@router.post("/", response_model=List[SearchResult])
async def search_memories(
    request: SearchRequest,
    memory_service: MemoryService = Depends(),
    embedding_service: EmbeddingService = Depends()
):
    """Semantic search for memories"""
    try:
        # Create query embedding
        query_embedding = await embedding_service.create_embedding(request.query)
        
        # Search similar memories
        results = await memory_service.search_similar(
            query_embedding,
            limit=request.limit,
            threshold=request.threshold
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🧪 Testing Strategy

### Test Structure
```
tests/
├── __init__.py
├── conftest.py           # Pytest configuration
├── test_api/             # API endpoint tests
│   ├── test_memories.py
│   └── test_search.py
├── test_services/        # Service layer tests
│   ├── test_embedding_service.py
│   └── test_memory_service.py
├── test_integration/     # Integration tests
│   └── test_full_workflow.py
└── test_performance/     # Performance tests
    └── test_search_speed.py
```

### Test Examples

#### Unit Tests (`tests/test_services/test_embedding_service.py`)
```python
import pytest
import numpy as np
from unittest.mock import AsyncMock, patch
from services.embedding_service import EmbeddingService

@pytest.fixture
def embedding_service():
    return EmbeddingService("test-api-key")

@pytest.mark.asyncio
async def test_create_embedding(embedding_service):
    with patch('openai.Embedding.acreate') as mock_create:
        mock_create.return_value = {
            'data': [{'embedding': [0.1, 0.2, 0.3]}]
        }
        
        result = await embedding_service.create_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]
        mock_create.assert_called_once()

def test_calculate_similarity(embedding_service):
    emb1 = [1.0, 0.0, 0.0]
    emb2 = [1.0, 0.0, 0.0]
    
    similarity = embedding_service.calculate_similarity(emb1, emb2)
    
    assert similarity == pytest.approx(1.0, rel=1e-5)
```

#### Integration Tests (`tests/test_integration/test_full_workflow.py`)
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_store_and_search_workflow():
    # Store a memory
    memory_data = {
        "content": "Python decorators are powerful features",
        "metadata": {"topic": "programming", "language": "python"}
    }
    
    store_response = client.post("/memories/", json=memory_data)
    assert store_response.status_code == 200
    
    memory_id = store_response.json()["id"]
    
    # Search for the memory
    search_data = {
        "query": "Python decorator functionality",
        "limit": 5,
        "threshold": 0.3
    }
    
    search_response = client.post("/search/", json=search_data)
    assert search_response.status_code == 200
    
    results = search_response.json()
    assert len(results) > 0
    
    # Verify the stored memory is found
    memory_ids = [result["memory"]["id"] for result in results]
    assert memory_id in memory_ids
```

### Performance Tests (`tests/test_performance/test_search_speed.py`)
```python
import time
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_search_response_time():
    """Test that search responds within acceptable time"""
    search_data = {
        "query": "performance test query",
        "limit": 10
    }
    
    start_time = time.time()
    response = client.post("/search/", json=search_data)
    duration = time.time() - start_time
    
    assert response.status_code == 200
    assert duration < 5.0  # Should respond within 5 seconds

@pytest.mark.performance
def test_bulk_storage_performance():
    """Test storing multiple memories quickly"""
    memories = [
        {"content": f"Performance test memory {i}", "metadata": {"test": True}}
        for i in range(10)
    ]
    
    start_time = time.time()
    
    for memory in memories:
        response = client.post("/memories/", json=memory)
        assert response.status_code == 200
    
    duration = time.time() - start_time
    assert duration < 30.0  # Should complete within 30 seconds
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_api/
pytest -m performance  # Performance tests only
pytest -v              # Verbose output

# Run tests in parallel
pytest -n auto

# Generate coverage report
coverage run -m pytest
coverage html
open htmlcov/index.html
```

## 🔧 Development Workflow

### 1. Setting Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### 2. Code Quality Tools

#### `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        args: [--line-length=88]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: [--profile=black]
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88, --ignore=E203,W503]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### 3. Development Environment Configuration

#### `requirements-dev.txt`
```txt
# Development dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-xdist>=3.0.0
black>=22.3.0
isort>=5.10.0
flake8>=4.0.0
mypy>=0.950
pre-commit>=2.17.0
httpx>=0.24.0  # For async testing
```

#### VS Code Configuration (`.vscode/settings.json`)
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## 🚢 Deployment Options

### Docker Development

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements*.txt ./
RUN pip install -r requirements-dev.txt

# Copy source code
COPY . .

# Development server with hot reload
CMD ["python", "src/main.py", "--reload", "--host", "0.0.0.0"]
```

### Production Deployment

#### Option 1: Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/memorylink
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
    restart: unless-stopped
    
  db:
    image: ankane/pgvector
    environment:
      POSTGRES_DB: memorylink
      POSTGRES_USER: user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Option 2: Kubernetes
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memorylink
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memorylink
  template:
    metadata:
      labels:
        app: memorylink
    spec:
      containers:
      - name: memorylink
        image: memorylink:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: memorylink-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: memorylink-secrets
              key: openai-api-key
```

## 🔌 Extending MemoryLink

### Adding New Endpoints

1. **Create the endpoint** (`src/api/analytics.py`):
```python
from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/stats")
async def get_vault_stats() -> Dict:
    """Get Memory Vault statistics"""
    # Implementation here
    return {"total_memories": 150, "topics": {...}}
```

2. **Register the router** (`src/main.py`):
```python
from api import analytics
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
```

### Custom Embedding Providers

```python
# src/services/custom_embedding_service.py
from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        pass

class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
    
    async def create_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode([text])
        return embedding[0].tolist()

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str):
        import openai
        openai.api_key = api_key
    
    async def create_embedding(self, text: str) -> List[float]:
        # OpenAI implementation
        pass
```

### Plugin System

```python
# src/plugins/base.py
from abc import ABC, abstractmethod

class MemoryLinkPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    async def process_memory(self, content: str, metadata: dict) -> dict:
        """Process memory before storage"""
        pass
    
    @abstractmethod
    async def enhance_search(self, query: str, results: list) -> list:
        """Enhance search results"""
        pass

# src/plugins/auto_tagger.py
class AutoTaggerPlugin(MemoryLinkPlugin):
    @property
    def name(self) -> str:
        return "auto_tagger"
    
    async def process_memory(self, content: str, metadata: dict) -> dict:
        # Auto-generate tags based on content
        tags = await self._extract_tags(content)
        metadata["auto_tags"] = tags
        return metadata
    
    async def enhance_search(self, query: str, results: list) -> list:
        # Enhance results based on tags
        return results
    
    async def _extract_tags(self, content: str) -> list:
        # Implementation for tag extraction
        pass
```

## 📊 Monitoring & Observability

### Logging Configuration

```python
# src/config/logging.py
import logging
import sys
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'logs/memorylink-{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )

# Usage in main.py
from config.logging import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
```

### Health Checks

```python
# src/api/health.py
from fastapi import APIRouter, status
from sqlalchemy.orm import Session
from database import get_db
import asyncio
import time

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    checks = {
        "database": await check_database_health(db),
        "embedding_service": await check_embedding_service(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage()
    }
    
    overall_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.utcnow(),
        "checks": checks
    }
```

### Metrics Collection

```python
# src/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🤝 Contributing Guidelines

### 1. Code Style
- Use Black for formatting (line length: 88)
- Sort imports with isort
- Follow PEP 8 guidelines
- Add type hints for all functions
- Write docstrings for public methods

### 2. Commit Messages
```
feat: add semantic search filtering by metadata
fix: resolve embedding service connection timeout  
docs: update API documentation with new endpoints
test: add integration tests for search functionality
refactor: extract embedding logic into separate service
```

### 3. Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks (`make test`, `make lint`)
5. Update documentation
6. Submit pull request

### 4. Issue Templates

**Bug Report Template:**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior  
What actually happens

## Environment
- OS: 
- Python version:
- MemoryLink version:
```

**Feature Request Template:**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches considered
```

## 🔒 Security Best Practices

### 1. Input Validation
```python
from pydantic import BaseModel, validator
import bleach

class MemoryCreate(BaseModel):
    content: str
    metadata: dict = {}
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Content cannot be empty')
        if len(v) > 100000:  # 100KB limit
            raise ValueError('Content too large')
        return bleach.clean(v)  # Sanitize HTML
```

### 2. Rate Limiting
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post("/search/")
@app.limiter.limit("10/minute")
async def search_memories(request: SearchRequest):
    # Implementation
    pass
```

### 3. Authentication (Production)
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_api_key(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials
```

---

Happy coding! 🚀 For questions, check the [FAQ](./faq.md) or open an issue on GitHub.