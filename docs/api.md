# 🔌 MemoryLink API Reference

> Complete reference for integrating MemoryLink into your applications

## 🚀 Quick Start

```bash
# Start the Memory Vault
make start

# API will be available at:
# http://localhost:8000
```

## 📋 Base Information

- **Base URL**: `http://localhost:8000`
- **Content Type**: `application/json`
- **Authentication**: None (local development)
- **Rate Limiting**: Not implemented (development mode)

## 🛡️ Health Check

### `GET /health`

Check if the Memory Vault server is running and healthy.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

**Status Codes**:
- `200`: Server is healthy
- `503`: Server is experiencing issues

## 💾 Memory Management

### `POST /memories/`

Store a new memory in the vault.

**Request Body**:
```json
{
  "content": "Your memory content here",
  "metadata": {
    "topic": "programming",
    "tags": ["python", "tutorial"],
    "source": "documentation",
    "difficulty": "beginner",
    "custom_field": "any value"
  }
}
```

**Response**:
```json
{
  "id": "uuid-string",
  "content": "Your memory content here",
  "metadata": {
    "topic": "programming",
    "tags": ["python", "tutorial"],
    "source": "documentation"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200`: Memory created successfully
- `400`: Invalid request body
- `500`: Server error

### `GET /memories/`

Retrieve all stored memories.

**Query Parameters**:
- `limit` (optional): Maximum number of memories to return (default: 100)
- `offset` (optional): Number of memories to skip (default: 0)

**Response**:
```json
[
  {
    "id": "uuid-1",
    "content": "First memory content",
    "metadata": {...},
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "uuid-2", 
    "content": "Second memory content",
    "metadata": {...},
    "created_at": "2024-01-15T10:29:00Z"
  }
]
```

**Status Codes**:
- `200`: Success
- `500`: Server error

### `GET /memories/{memory_id}`

Retrieve a specific memory by ID.

**Response**:
```json
{
  "id": "uuid-string",
  "content": "Memory content",
  "metadata": {...},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200`: Memory found
- `404`: Memory not found
- `500`: Server error

## 🔍 Semantic Search

### `POST /search/`

Search memories using AI-powered semantic similarity.

**Request Body**:
```json
{
  "query": "Python decorators and functions",
  "limit": 10,
  "threshold": 0.7
}
```

**Parameters**:
- `query` (required): Natural language search query
- `limit` (optional): Maximum results to return (default: 10, max: 100)
- `threshold` (optional): Similarity threshold (0.0-1.0, default: 0.3)

**Response**:
```json
[
  {
    "memory": {
      "id": "uuid-string",
      "content": "Memory content about Python decorators...",
      "metadata": {
        "topic": "programming",
        "language": "python"
      },
      "created_at": "2024-01-15T10:30:00Z"
    },
    "similarity": 0.85
  },
  {
    "memory": {...},
    "similarity": 0.78
  }
]
```

**Status Codes**:
- `200`: Search completed (may return empty array)
- `400`: Invalid request body
- `500`: Search service error

## 🏷️ Metadata Filtering

### `POST /search/advanced`

Advanced search with metadata filtering (if implemented).

**Request Body**:
```json
{
  "query": "machine learning",
  "limit": 20,
  "threshold": 0.5,
  "filters": {
    "topic": "programming",
    "difficulty": ["beginner", "intermediate"],
    "tags": ["python", "ml"]
  }
}
```

## 📊 Statistics

### `GET /stats`

Get vault statistics (if implemented).

**Response**:
```json
{
  "total_memories": 150,
  "total_size_bytes": 1048576,
  "oldest_memory": "2024-01-01T00:00:00Z",
  "newest_memory": "2024-01-15T10:30:00Z",
  "topics": {
    "programming": 45,
    "productivity": 32,
    "learning": 28
  }
}
```

## 🔧 Integration Examples

### Python Client

```python
import requests
from typing import Dict, List, Optional

class MemoryVault:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def store(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Store a memory"""
        response = self.session.post(
            f"{self.base_url}/memories/",
            json={"content": content, "metadata": metadata or {}}
        )
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[Dict]:
        """Search memories"""
        response = self.session.post(
            f"{self.base_url}/search/",
            json={"query": query, "limit": limit, "threshold": threshold}
        )
        response.raise_for_status()
        return response.json()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all memories"""
        response = self.session.get(
            f"{self.base_url}/memories/",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    def get_by_id(self, memory_id: str) -> Dict:
        """Get specific memory"""
        response = self.session.get(f"{self.base_url}/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check if server is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

# Usage Example
vault = MemoryVault()

# Store a memory
result = vault.store(
    "Python list comprehensions provide concise syntax for creating lists",
    metadata={"topic": "python", "difficulty": "intermediate"}
)

# Search for related memories
memories = vault.search("Python syntax for lists", limit=5)

# Get all memories
all_memories = vault.get_all(limit=50)
```

### JavaScript/Node.js Client

```javascript
class MemoryVault {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async store(content, metadata = {}) {
    const response = await fetch(`${this.baseUrl}/memories/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content, metadata })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async search(query, limit = 10, threshold = 0.3) {
    const response = await fetch(`${this.baseUrl}/search/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, limit, threshold })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async getAll(limit = 100, offset = 0) {
    const response = await fetch(`${this.baseUrl}/memories/?limit=${limit}&offset=${offset}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Usage Example
const vault = new MemoryVault();

// Store and search
await vault.store("React hooks revolutionized state management", {
  framework: "react",
  concept: "hooks"
});

const results = await vault.search("React state management");
```

### cURL Examples

```bash
# Store a memory
curl -X POST http://localhost:8000/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Database indexing improves query performance",
    "metadata": {"topic": "database", "concept": "indexing"}
  }'

# Search memories  
curl -X POST http://localhost:8000/search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "improving database performance",
    "limit": 5,
    "threshold": 0.7
  }'

# Get all memories
curl http://localhost:8000/memories/

# Health check
curl http://localhost:8000/health
```

## ⚠️ Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "detail": "Detailed error information",
  "status_code": 400
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request format or parameters
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Valid JSON but invalid data
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Server temporarily unavailable

### Error Handling Best Practices

```python
# Python example with proper error handling
try:
    result = vault.store(content, metadata)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Invalid request format")
    elif e.response.status_code == 500:
        print("Server error - please try again")
    else:
        print(f"HTTP error: {e.response.status_code}")
except requests.exceptions.ConnectionError:
    print("Cannot connect to Memory Vault - is it running?")
except requests.exceptions.Timeout:
    print("Request timed out - server may be overloaded")
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0              # Host to bind to
API_PORT=8000                 # Port to listen on
API_WORKERS=1                 # Number of worker processes

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=memorylink
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# OpenAI
OPENAI_API_KEY=your-key-here  # Required for embeddings

# CORS (for web applications)
CORS_ORIGINS=["http://localhost:3000"]

# Security (production)
API_KEY_REQUIRED=false        # Enable API key authentication
RATE_LIMIT_PER_MINUTE=60     # Requests per minute per IP
```

### Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  memorylink:
    build: .
    ports:
      - "80:8000"
    environment:
      - API_WORKERS=4
      - POSTGRES_HOST=db
    depends_on:
      - db
    restart: unless-stopped
    
  db:
    image: ankane/pgvector
    environment:
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 📚 OpenAPI Documentation

MemoryLink automatically generates OpenAPI documentation. Access it at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`  
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🚀 Performance Tips

1. **Batch Operations**: Store multiple memories in quick succession
2. **Connection Pooling**: Reuse HTTP connections with session objects
3. **Appropriate Thresholds**: Higher thresholds = more precise but fewer results
4. **Limit Results**: Only request the number of results you need
5. **Cache Health Checks**: Don't check health on every request

## 🔐 Security Considerations

1. **Network Security**: Use HTTPS in production
2. **Input Validation**: Sanitize content before storage  
3. **Rate Limiting**: Implement request rate limiting
4. **API Keys**: Use authentication for production deployments
5. **CORS**: Configure appropriate CORS origins
6. **Data Privacy**: Be mindful of sensitive content in memories

---

For more examples and integration patterns, see the [`examples/`](../examples/) directory.