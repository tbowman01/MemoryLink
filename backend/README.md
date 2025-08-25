# MemoryLink Backend

A FastAPI-based backend for the MemoryLink personal memory system with semantic search capabilities.

## Features

- **Semantic Search**: Uses sentence transformers for intelligent memory retrieval
- **End-to-End Encryption**: AES-256 encryption for data at rest
- **Vector Storage**: ChromaDB for efficient similarity search
- **RESTful API**: Clean, documented endpoints with automatic OpenAPI generation
- **Docker Ready**: Containerized deployment with health checks
- **Local-First**: Designed for local deployment and privacy

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and navigate to backend directory
cd backend

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Start with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run the application
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

## API Endpoints

### Core Memory Operations

- `POST /memory/add` - Add a new memory
- `POST /memory/search` - Search memories semantically
- `GET /memory/{id}` - Get specific memory
- `DELETE /memory/{id}` - Delete memory

### Utility Endpoints

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with dependencies
- `GET /memory/user/{user_id}/count` - Get memory count for user
- `GET /memory/stats/service` - Service statistics

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

Key environment variables in `.env`:

```env
# API Configuration
APP_NAME="MemoryLink Backend"
DEBUG=false
HOST=127.0.0.1
PORT=8000

# Security
ENCRYPTION_KEY=your-secure-key-here
ALLOWED_ORIGINS=http://localhost:3000

# Database
CHROMA_DB_PATH=./data/chromadb
CHROMA_COLLECTION_NAME=memory_embeddings

# AI/ML
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

## Architecture

```
backend/
├── src/
│   ├── api/           # API routes
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   ├── config/        # Configuration
│   ├── utils/         # Utilities
│   └── main.py        # FastAPI app
├── tests/             # Test suite
├── Dockerfile         # Container config
└── requirements.txt   # Dependencies
```

### Key Components

- **MemoryService**: Core business logic
- **EmbeddingService**: Text-to-vector conversion
- **VectorStore**: ChromaDB interface
- **EncryptionService**: Data encryption/decryption

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Security Features

- **Local-Only Binding**: Binds to localhost by default
- **AES-256 Encryption**: All content encrypted at rest
- **No External Dependencies**: Runs completely offline
- **User Isolation**: Memory access controlled by user_id
- **Input Validation**: Comprehensive request validation

## Performance

- **Async/Await**: Non-blocking I/O operations
- **Vector Optimization**: Efficient similarity search
- **Memory Efficient**: Streaming and batching support
- **Caching Ready**: ChromaDB persistent storage

## Production Deployment

### Docker Production

```bash
# Build production image
docker build -t memorylink-backend .

# Run with production settings
docker run -d \
  --name memorylink-backend \
  -p 8000:8000 \
  -v memorylink_data:/app/data \
  -e DEBUG=false \
  -e ENCRYPTION_KEY=your-production-key \
  memorylink-backend
```

### Environment Recommendations

- **Encryption Key**: Generate strong key with `openssl rand -base64 32`
- **Data Persistence**: Mount `/app/data` volume for ChromaDB
- **Resource Limits**: 2GB RAM minimum for embedding models
- **Health Checks**: Use `/health/detailed` for monitoring

## Troubleshooting

### Common Issues

1. **Embedding Model Loading**
   - First run downloads ~90MB model
   - Ensure internet connection during initial setup
   - Model cached locally afterward

2. **ChromaDB Permissions**
   - Ensure data directory is writable
   - Check Docker volume mounts

3. **Memory Usage**
   - Embedding models require ~1GB RAM
   - Monitor with `/health/detailed` endpoint

### Logs

```bash
# Docker logs
docker logs memorylink-backend

# Local development
# Logs output to stdout with structured format
```

## API Usage Examples

### Add Memory

```bash
curl -X POST "http://localhost:8000/memory/add" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Remember to buy groceries tomorrow",
    "tags": ["shopping", "reminder"],
    "user_id": "user123"
  }'
```

### Search Memories

```bash
curl -X POST "http://localhost:8000/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "grocery shopping",
    "user_id": "user123",
    "limit": 10,
    "min_similarity": 0.5
  }'
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

MIT License - see LICENSE file for details.