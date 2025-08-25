# MemoryLink Developer Guide
*Comprehensive Guide for Contributing to MemoryLink*

## 💻 Welcome to MemoryLink Development

MemoryLink is built with modern Python technologies and follows industry best practices for maintainable, scalable software. This guide will help you understand the codebase, contribute effectively, and extend MemoryLink's capabilities.

### Development Philosophy

- **Local-First**: Privacy and control are paramount
- **Test-Driven Development**: Tests guide design and ensure reliability
- **Clean Architecture**: Separation of concerns and modularity
- **Security by Design**: Security considerations in every component
- **Performance Conscious**: Efficient algorithms and resource usage
- **Developer Experience**: Tools and processes that make development enjoyable

## 🏗️ Architecture Deep Dive

### System Overview

```
MemoryLink Architecture
┌────────────────────────────────────────────────────────────────────────────────────┐
│                           Client Layer                           │
│  CLI Interface  │  HTTP Clients  │  IDE Integrations  │  SDKs  │
├────────────────────────────────────────────────────────────────────────────────────┤
│                             API Layer                             │
│  FastAPI  │  Authentication  │  Validation  │  Rate Limiting  │
├────────────────────────────────────────────────────────────────────────────────────┤
│                           Service Layer                          │
│  Memory  │  Embedding  │  Encryption  │  Search  │  Cache  │
├────────────────────────────────────────────────────────────────────────────────────┤
│                          Storage Layer                          │
│  ChromaDB (Vectors)  │  SQLite (Metadata)  │  File System  │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
memorylink/
├── backend/                 # Backend application code
│   ├── src/                # Source code
│   │   ├── api/           # FastAPI routes and handlers
│   │   ├── config/        # Configuration management
│   │   ├── models/        # Pydantic data models
│   │   ├── services/      # Business logic services
│   │   ├── utils/         # Utility functions
│   │   └── main.py        # Application entry point
│   ├── tests/              # Test suites
│   ├── Dockerfile          # Container definition
│   └── requirements.txt    # Python dependencies
├── docs/                  # Documentation
├── examples/              # Usage examples
├── k8s/                   # Kubernetes manifests
├── scripts/               # Automation scripts
├── tests/                 # Integration tests
├── docker-compose.yml     # Local development
├── Makefile              # Development commands
└── README.md             # Project overview
```

## 🚀 Development Environment Setup

### Prerequisites

```bash
# System requirements
python --version        # Python 3.11+
docker --version        # Docker 20.10+
docker-compose --version # Docker Compose 2.0+
make --version          # Make 4.0+
git --version           # Git 2.30+

# Optional but recommended
kubectl version         # Kubernetes CLI
helm version            # Helm package manager
vscode --version        # VS Code editor
```

### Quick Setup

```bash
# Clone repository
git clone https://github.com/your-org/memorylink.git
cd memorylink

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/dev.txt

# Setup pre-commit hooks
pre-commit install

# Configure environment
cp config/.env.example .env
# Edit .env with your settings

# Initialize development environment
make setup
make dev
```

### IDE Configuration

#### VS Code Setup

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "backend/tests",
        "-v"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true
    }
}
```

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.mypy-type-checker",
        "charliermarsh.ruff",
        "ms-vscode.docker",
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        "redhat.vscode-yaml"
    ]
}
```

## 📝 Code Style and Standards

### Python Code Style

```python
# Example of properly formatted MemoryLink code
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class MemoryModel(BaseModel):
    """Memory data model with validation.
    
    This model represents a memory entry in the system,
    including content, metadata, and system fields.
    """
    
    id: str = Field(..., description="Unique memory identifier")
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=50000,
        description="Memory content (1-50,000 characters)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata dictionary"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryService:
    """Core memory management service.
    
    This service handles the business logic for memory operations,
    coordinating between storage, encryption, and embedding services.
    """
    
    def __init__(self, storage_service, encryption_service, embedding_service):
        self.storage = storage_service
        self.encryption = encryption_service
        self.embedding = embedding_service
        self.logger = logger.bind(service="memory")
    
    async def create_memory(self, content: str, metadata: Optional[Dict] = None) -> MemoryModel:
        """Create a new memory entry.
        
        Args:
            content: The memory content to store
            metadata: Optional metadata dictionary
            
        Returns:
            MemoryModel: The created memory with generated ID
            
        Raises:
            ValidationError: If content or metadata is invalid
            EncryptionError: If encryption fails
            StorageError: If storage operation fails
        """
        try:
            # Generate unique ID
            memory_id = self._generate_id()
            
            # Validate and process
            validated_content = self._validate_content(content)
            validated_metadata = self._validate_metadata(metadata or {})
            
            # Create memory model
            memory = MemoryModel(
                id=memory_id,
                content=validated_content,
                metadata=validated_metadata
            )
            
            # Store memory
            await self._store_memory(memory)
            
            self.logger.info(
                "Memory created successfully",
                memory_id=memory_id,
                content_length=len(validated_content),
                metadata_keys=list(validated_metadata.keys())
            )
            
            return memory
            
        except Exception as e:
            self.logger.error(
                "Failed to create memory",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def _generate_id(self) -> str:
        """Generate unique memory ID."""
        import uuid
        return f"mem_{uuid.uuid4().hex[:12]}"
    
    def _validate_content(self, content: str) -> str:
        """Validate memory content."""
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        if len(content) > 50000:
            raise ValueError("Content exceeds maximum length")
        
        return content.strip()
```

### Code Quality Tools

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = [
    "backend/tests",
    "tests"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
    "security: Security tests"
]

[tool.coverage.run]
source = ["backend/src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\(Protocol\):",
    "@(abc\.)?abstractmethod"
]
```

## 🧪 Testing Strategy

### Test Structure

```python
# backend/tests/unit/test_memory_service.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.services.memory_service import MemoryService
from src.models.memory_models import MemoryModel
from src.exceptions import ValidationError, StorageError


class TestMemoryService:
    """Test suite for MemoryService."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        return {
            'storage': AsyncMock(),
            'encryption': AsyncMock(),
            'embedding': AsyncMock()
        }
    
    @pytest.fixture
    def memory_service(self, mock_services):
        """Create MemoryService instance with mocked dependencies."""
        return MemoryService(
            storage_service=mock_services['storage'],
            encryption_service=mock_services['encryption'],
            embedding_service=mock_services['embedding']
        )
    
    @pytest.fixture
    def sample_memory_data(self):
        """Sample memory data for testing."""
        return {
            'content': 'This is a test memory about Python programming.',
            'metadata': {
                'tags': ['python', 'programming'],
                'category': 'education',
                'importance': 'high'
            }
        }
    
    @pytest_asyncio.fixture
    async def test_create_memory_success(self, memory_service, sample_memory_data, mock_services):
        """Test successful memory creation."""
        # Arrange
        content = sample_memory_data['content']
        metadata = sample_memory_data['metadata']
        
        # Mock successful operations
        mock_services['storage'].store_memory.return_value = True
        mock_services['encryption'].encrypt.return_value = b'encrypted_content'
        mock_services['embedding'].generate.return_value = [0.1, 0.2, 0.3]
        
        # Act
        result = await memory_service.create_memory(content, metadata)
        
        # Assert
        assert isinstance(result, MemoryModel)
        assert result.content == content
        assert result.metadata == metadata
        assert result.id.startswith('mem_')
        assert isinstance(result.created_at, datetime)
        
        # Verify service calls
        mock_services['storage'].store_memory.assert_called_once()
        mock_services['encryption'].encrypt.assert_called_once_with(content)
        mock_services['embedding'].generate.assert_called_once_with(content)
    
    @pytest_asyncio.fixture
    async def test_create_memory_validation_error(self, memory_service):
        """Test memory creation with validation error."""
        # Test empty content
        with pytest.raises(ValidationError, match="Content cannot be empty"):
            await memory_service.create_memory("")
        
        # Test content too long
        long_content = "x" * 50001
        with pytest.raises(ValidationError, match="Content exceeds maximum length"):
            await memory_service.create_memory(long_content)
    
    @pytest_asyncio.fixture
    async def test_create_memory_storage_error(self, memory_service, sample_memory_data, mock_services):
        """Test memory creation with storage error."""
        # Arrange
        content = sample_memory_data['content']
        mock_services['storage'].store_memory.side_effect = StorageError("Database unavailable")
        
        # Act & Assert
        with pytest.raises(StorageError, match="Database unavailable"):
            await memory_service.create_memory(content)
    
    @pytest_asyncio.fixture
    async def test_search_memories_success(self, memory_service, mock_services):
        """Test successful memory search."""
        # Arrange
        query = "python programming"
        expected_results = [
            {
                'id': 'mem_123',
                'content': 'Python is a programming language',
                'similarity': 0.85,
                'metadata': {'tags': ['python']}
            }
        ]
        
        mock_services['embedding'].generate.return_value = [0.1, 0.2, 0.3]
        mock_services['storage'].search_similar.return_value = expected_results
        
        # Act
        results = await memory_service.search_memories(query, limit=10)
        
        # Assert
        assert len(results) == 1
        assert results[0]['id'] == 'mem_123'
        assert results[0]['similarity'] == 0.85
        
        # Verify service calls
        mock_services['embedding'].generate.assert_called_once_with(query)
        mock_services['storage'].search_similar.assert_called_once()


# Integration test example
# tests/integration/test_memory_api.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from backend.src.main import app


class TestMemoryAPI:
    """Integration tests for Memory API endpoints."""
    
    @pytest_asyncio.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest_asyncio.fixture
    async def test_create_memory_endpoint(self, client):
        """Test memory creation endpoint."""
        # Arrange
        memory_data = {
            "content": "FastAPI is a modern Python web framework",
            "metadata": {
                "tags": ["python", "web", "framework"],
                "category": "technology"
            }
        }
        
        # Act
        response = await client.post("/memories/", json=memory_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "id" in data
        assert data["content"] == memory_data["content"]
        assert data["metadata"] == memory_data["metadata"]
        assert "created_at" in data
    
    @pytest_asyncio.fixture
    async def test_search_memories_endpoint(self, client):
        """Test memory search endpoint."""
        # First, create a memory
        memory_data = {
            "content": "Python list comprehensions are powerful",
            "metadata": {"tags": ["python", "programming"]}
        }
        
        create_response = await client.post("/memories/", json=memory_data)
        assert create_response.status_code == status.HTTP_200_OK
        
        # Then search for it
        search_data = {
            "query": "python programming",
            "limit": 10,
            "threshold": 0.3
        }
        
        search_response = await client.post("/search/", json=search_data)
        assert search_response.status_code == status.HTTP_200_OK
        
        results = search_response.json()
        assert len(results) > 0
        assert all("similarity" in result for result in results)
        assert all("memory" in result for result in results)


# Performance test example
# tests/performance/test_search_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor


class TestSearchPerformance:
    """Performance tests for search functionality."""
    
    @pytest.mark.slow
    def test_search_response_time(self, memory_service, large_dataset):
        """Test search response time meets requirements."""
        # Arrange
        query = "machine learning algorithms"
        max_response_time = 0.65  # 650ms requirement
        
        # Act
        start_time = time.time()
        results = memory_service.search_memories(query, limit=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Assert
        assert response_time < max_response_time, f"Search took {response_time:.3f}s, expected < {max_response_time}s"
        assert len(results) > 0, "Search should return results"
    
    @pytest.mark.slow
    def test_concurrent_searches(self, memory_service):
        """Test concurrent search performance."""
        queries = [
            "python programming",
            "machine learning",
            "web development",
            "database design",
            "api architecture"
        ]
        
        def perform_search(query):
            start_time = time.time()
            results = memory_service.search_memories(query)
            end_time = time.time()
            return {
                'query': query,
                'duration': end_time - start_time,
                'results_count': len(results)
            }
        
        # Execute concurrent searches
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            results = list(executor.map(perform_search, queries))
            total_time = time.time() - start_time
        
        # Assert performance requirements
        assert total_time < 2.0, f"Concurrent searches took {total_time:.3f}s, expected < 2.0s"
        
        for result in results:
            assert result['duration'] < 1.0, f"Individual search took {result['duration']:.3f}s"
            assert result['results_count'] >= 0, "Search should not fail"
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m "not slow"            # Skip slow tests

# Run tests with coverage
pytest --cov=backend/src --cov-report=html

# Run performance tests
pytest -m slow --durations=10

# Run tests in parallel
pytest -n auto

# Debug failing tests
pytest --pdb -x
```

## 🔧 Development Workflow

### Git Workflow

```bash
# Feature development workflow
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/semantic-search-improvement

# Make changes, commit frequently
git add .
git commit -m "Add improved semantic search algorithm"

# Keep branch updated
git fetch origin
git rebase origin/main

# Push feature branch
git push origin feature/semantic-search-improvement

# Create pull request
gh pr create --title "Improve semantic search algorithm" --body "Implements advanced semantic search with better relevance scoring"
```

### Commit Message Format

```
type(scope): short description

Longer explanation of the change, if needed.

Fixes #123
Closes #456
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(search): implement advanced semantic similarity scoring

fix(encryption): resolve AES key generation edge case

docs(api): add examples for batch memory operations

perf(embedding): optimize vector cache for large datasets
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements
  
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.4.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
  
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
        args: [-m, "not slow"]
```

## 📚 API Development

### Adding New Endpoints

```python
# backend/src/api/new_feature_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from ..services.new_feature_service import NewFeatureService
from ..models.response_models import SuccessResponse, ErrorResponse
from ..dependencies import get_new_feature_service
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/new-feature", tags=["New Feature"])


class NewFeatureRequest(BaseModel):
    """Request model for new feature."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    enabled: bool = Field(default=True)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Feature Name",
                "description": "Feature description",
                "enabled": True
            }
        }


class NewFeatureResponse(BaseModel):
    """Response model for new feature."""
    
    id: str
    name: str
    description: Optional[str]
    enabled: bool
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "feature_123",
                "name": "Feature Name",
                "description": "Feature description",
                "enabled": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


@router.post(
    "/",
    response_model=NewFeatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new feature",
    description="Create a new feature with specified configuration",
    responses={
        201: {"description": "Feature created successfully"},
        400: {"description": "Invalid request data"},
        500: {"description": "Internal server error"}
    }
)
async def create_feature(
    request: NewFeatureRequest,
    service: NewFeatureService = Depends(get_new_feature_service)
) -> NewFeatureResponse:
    """Create a new feature.
    
    Args:
        request: Feature creation request
        service: New feature service dependency
        
    Returns:
        NewFeatureResponse: Created feature data
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        logger.info(
            "Creating new feature",
            feature_name=request.name,
            enabled=request.enabled
        )
        
        feature = await service.create_feature(
            name=request.name,
            description=request.description,
            enabled=request.enabled
        )
        
        logger.info(
            "Feature created successfully",
            feature_id=feature.id,
            feature_name=feature.name
        )
        
        return NewFeatureResponse(**feature.dict())
        
    except ValueError as e:
        logger.warning(
            "Invalid feature request",
            error=str(e),
            feature_name=request.name
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Failed to create feature",
            error=str(e),
            error_type=type(e).__name__,
            feature_name=request.name
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feature"
        )


@router.get(
    "/{feature_id}",
    response_model=NewFeatureResponse,
    summary="Get feature by ID",
    description="Retrieve a specific feature by its ID"
)
async def get_feature(
    feature_id: str,
    service: NewFeatureService = Depends(get_new_feature_service)
) -> NewFeatureResponse:
    """Get feature by ID."""
    feature = await service.get_feature(feature_id)
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found"
        )
    
    return NewFeatureResponse(**feature.dict())


@router.get(
    "/",
    response_model=List[NewFeatureResponse],
    summary="List all features",
    description="Get a list of all features with optional filtering"
)
async def list_features(
    enabled: Optional[bool] = None,
    limit: int = Field(default=100, ge=1, le=1000),
    offset: int = Field(default=0, ge=0),
    service: NewFeatureService = Depends(get_new_feature_service)
) -> List[NewFeatureResponse]:
    """List all features with optional filtering."""
    features = await service.list_features(
        enabled=enabled,
        limit=limit,
        offset=offset
    )
    
    return [NewFeatureResponse(**feature.dict()) for feature in features]
```

### Service Layer Development

```python
# backend/src/services/new_feature_service.py
from typing import List, Optional
from datetime import datetime
import uuid

from ..models.feature_models import FeatureModel
from ..storage.feature_repository import FeatureRepository
from ..utils.logger import get_logger
from ..exceptions import ValidationError, StorageError

logger = get_logger(__name__)


class NewFeatureService:
    """Service for managing new features."""
    
    def __init__(self, repository: FeatureRepository):
        self.repository = repository
        self.logger = logger.bind(service="new_feature")
    
    async def create_feature(
        self, 
        name: str, 
        description: Optional[str] = None,
        enabled: bool = True
    ) -> FeatureModel:
        """Create a new feature.
        
        Args:
            name: Feature name (required)
            description: Feature description (optional)
            enabled: Whether feature is enabled (default: True)
            
        Returns:
            FeatureModel: Created feature
            
        Raises:
            ValidationError: If input validation fails
            StorageError: If storage operation fails
        """
        try:
            # Validate input
            self._validate_feature_name(name)
            
            # Check if feature already exists
            existing = await self.repository.get_by_name(name)
            if existing:
                raise ValidationError(f"Feature '{name}' already exists")
            
            # Create feature model
            feature = FeatureModel(
                id=self._generate_id(),
                name=name.strip(),
                description=description.strip() if description else None,
                enabled=enabled,
                created_at=datetime.utcnow()
            )
            
            # Store feature
            stored_feature = await self.repository.create(feature)
            
            self.logger.info(
                "Feature created",
                feature_id=feature.id,
                feature_name=feature.name,
                enabled=feature.enabled
            )
            
            return stored_feature
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to create feature",
                error=str(e),
                feature_name=name
            )
            raise StorageError(f"Failed to create feature: {str(e)}")
    
    async def get_feature(self, feature_id: str) -> Optional[FeatureModel]:
        """Get feature by ID.
        
        Args:
            feature_id: Feature identifier
            
        Returns:
            FeatureModel or None if not found
        """
        try:
            feature = await self.repository.get_by_id(feature_id)
            
            if feature:
                self.logger.debug(
                    "Feature retrieved",
                    feature_id=feature_id,
                    feature_name=feature.name
                )
            
            return feature
            
        except Exception as e:
            self.logger.error(
                "Failed to get feature",
                error=str(e),
                feature_id=feature_id
            )
            raise StorageError(f"Failed to retrieve feature: {str(e)}")
    
    async def list_features(
        self,
        enabled: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FeatureModel]:
        """List features with optional filtering.
        
        Args:
            enabled: Filter by enabled status (optional)
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip (default: 0)
            
        Returns:
            List[FeatureModel]: List of features
        """
        try:
            features = await self.repository.list(
                enabled=enabled,
                limit=limit,
                offset=offset
            )
            
            self.logger.debug(
                "Features listed",
                count=len(features),
                enabled_filter=enabled,
                limit=limit,
                offset=offset
            )
            
            return features
            
        except Exception as e:
            self.logger.error(
                "Failed to list features",
                error=str(e)
            )
            raise StorageError(f"Failed to list features: {str(e)}")
    
    def _generate_id(self) -> str:
        """Generate unique feature ID."""
        return f"feature_{uuid.uuid4().hex[:12]}"
    
    def _validate_feature_name(self, name: str) -> None:
        """Validate feature name."""
        if not name or not name.strip():
            raise ValidationError("Feature name cannot be empty")
        
        if len(name.strip()) > 100:
            raise ValidationError("Feature name too long (max 100 characters)")
        
        # Check for invalid characters
        if not name.replace('_', '').replace('-', '').replace(' ', '').isalnum():
            raise ValidationError("Feature name contains invalid characters")
```

## 🔍 Debugging and Profiling

### Debug Configuration

```python
# debug_config.py
import logging
from typing import Any, Dict

def setup_debug_logging() -> None:
    """Configure debug logging for development."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('debug.log')
        ]
    )
    
    # Set specific loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)


def debug_request_middleware(request, call_next):
    """Debug middleware to log requests and responses."""
    import time
    import json
    
    start_time = time.time()
    
    print(f"\n=== DEBUG REQUEST ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")
    
    response = call_next(request)
    
    process_time = time.time() - start_time
    print(f"Process time: {process_time:.4f}s")
    print(f"Status: {response.status_code}")
    print(f"=== END DEBUG REQUEST ===\n")
    
    return response


class DebugMemoryService:
    """Debug wrapper for MemoryService."""
    
    def __init__(self, memory_service):
        self.service = memory_service
    
    async def create_memory(self, content: str, metadata: Dict[str, Any] = None):
        """Debug version of create_memory."""
        print(f"\n=== DEBUG CREATE MEMORY ===")
        print(f"Content length: {len(content)}")
        print(f"Content preview: {content[:100]}...")
        print(f"Metadata: {metadata}")
        
        start_time = time.time()
        result = await self.service.create_memory(content, metadata)
        elapsed = time.time() - start_time
        
        print(f"Memory ID: {result.id}")
        print(f"Creation time: {elapsed:.4f}s")
        print(f"=== END DEBUG CREATE MEMORY ===\n")
        
        return result
    
    async def search_memories(self, query: str, limit: int = 10, threshold: float = 0.3):
        """Debug version of search_memories."""
        print(f"\n=== DEBUG SEARCH MEMORIES ===")
        print(f"Query: {query}")
        print(f"Limit: {limit}")
        print(f"Threshold: {threshold}")
        
        start_time = time.time()
        results = await self.service.search_memories(query, limit, threshold)
        elapsed = time.time() - start_time
        
        print(f"Results found: {len(results)}")
        print(f"Search time: {elapsed:.4f}s")
        
        for i, result in enumerate(results[:3]):
            print(f"  Result {i+1}: {result['similarity']:.3f} - {result['memory']['content'][:50]}...")
        
        print(f"=== END DEBUG SEARCH MEMORIES ===\n")
        
        return results
```

### Performance Profiling

```python
# profiling_tools.py
import cProfile
import pstats
import functools
import time
from typing import Callable, Any

def profile_function(func: Callable) -> Callable:
    """Decorator to profile function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            
            # Save profile stats
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
            
            # Save to file
            profile_filename = f"{func.__name__}_profile.prof"
            profiler.dump_stats(profile_filename)
            print(f"Profile saved to {profile_filename}")
        
        return result
    return wrapper


def time_function(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class PerformanceMonitor:
    """Monitor performance of MemoryLink operations."""
    
    def __init__(self):
        self.metrics = {
            'memory_operations': [],
            'search_operations': [],
            'embedding_operations': []
        }
    
    def record_memory_operation(self, operation_type: str, duration: float, size: int):
        """Record memory operation metrics."""
        self.metrics['memory_operations'].append({
            'type': operation_type,
            'duration': duration,
            'size': size,
            'timestamp': time.time()
        })
    
    def record_search_operation(self, query: str, duration: float, results_count: int):
        """Record search operation metrics."""
        self.metrics['search_operations'].append({
            'query_length': len(query),
            'duration': duration,
            'results_count': results_count,
            'timestamp': time.time()
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        report = {}
        
        # Memory operations analysis
        memory_ops = self.metrics['memory_operations']
        if memory_ops:
            durations = [op['duration'] for op in memory_ops]
            report['memory_operations'] = {
                'count': len(memory_ops),
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations)
            }
        
        # Search operations analysis
        search_ops = self.metrics['search_operations']
        if search_ops:
            durations = [op['duration'] for op in search_ops]
            report['search_operations'] = {
                'count': len(search_ops),
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations),
                'avg_results': sum(op['results_count'] for op in search_ops) / len(search_ops)
            }
        
        return report


# Usage example
@profile_function
@time_function
async def benchmark_search(memory_service, queries):
    """Benchmark search performance with multiple queries."""
    results = []
    for query in queries:
        result = await memory_service.search_memories(query)
        results.append(result)
    return results
```

## 🔧 Extension Development

### Creating Custom Services

```python
# backend/src/services/analytics_service.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from ..models.analytics_models import AnalyticsReport, UsageMetrics
from ..storage.analytics_repository import AnalyticsRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and usage tracking."""
    
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository
        self.logger = logger.bind(service="analytics")
    
    async def track_memory_operation(
        self,
        operation_type: str,
        duration_ms: float,
        content_size: int,
        user_id: Optional[str] = None
    ):
        """Track memory operation for analytics."""
        try:
            await self.repository.record_operation(
                operation_type=operation_type,
                duration_ms=duration_ms,
                content_size=content_size,
                user_id=user_id,
                timestamp=datetime.utcnow()
            )
            
            self.logger.debug(
                "Operation tracked",
                operation_type=operation_type,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to track operation",
                error=str(e),
                operation_type=operation_type
            )
    
    async def generate_usage_report(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None
    ) -> AnalyticsReport:
        """Generate comprehensive usage analytics report."""
        try:
            # Get raw data
            operations = await self.repository.get_operations(
                start_date=start_date,
                end_date=end_date,
                user_id=user_id
            )
            
            # Process metrics
            metrics = self._process_operations(operations)
            
            # Generate insights
            insights = self._generate_insights(metrics)
            
            report = AnalyticsReport(
                start_date=start_date,
                end_date=end_date,
                user_id=user_id,
                metrics=metrics,
                insights=insights,
                generated_at=datetime.utcnow()
            )
            
            self.logger.info(
                "Analytics report generated",
                operations_count=len(operations),
                date_range=f"{start_date.date()} to {end_date.date()}"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(
                "Failed to generate analytics report",
                error=str(e)
            )
            raise
    
    def _process_operations(self, operations: List[Dict]) -> UsageMetrics:
        """Process raw operations into metrics."""
        if not operations:
            return UsageMetrics(
                total_operations=0,
                average_response_time=0,
                operations_by_type={},
                peak_usage_hours=[],
                performance_percentiles={}
            )
        
        # Basic counts
        total_operations = len(operations)
        
        # Response time analysis
        durations = [op['duration_ms'] for op in operations]
        avg_response_time = statistics.mean(durations)
        
        # Operations by type
        operations_by_type = {}
        for op in operations:
            op_type = op['operation_type']
            operations_by_type[op_type] = operations_by_type.get(op_type, 0) + 1
        
        # Peak usage analysis (by hour)
        hourly_usage = {}
        for op in operations:
            hour = op['timestamp'].hour
            hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
        
        peak_hours = sorted(hourly_usage.keys(), key=lambda h: hourly_usage[h], reverse=True)[:3]
        
        # Performance percentiles
        percentiles = {
            'p50': statistics.median(durations),
            'p90': statistics.quantiles(durations, n=10)[8],  # 90th percentile
            'p95': statistics.quantiles(durations, n=20)[18],  # 95th percentile
            'p99': statistics.quantiles(durations, n=100)[98]  # 99th percentile
        }
        
        return UsageMetrics(
            total_operations=total_operations,
            average_response_time=avg_response_time,
            operations_by_type=operations_by_type,
            peak_usage_hours=peak_hours,
            performance_percentiles=percentiles
        )
    
    def _generate_insights(self, metrics: UsageMetrics) -> List[str]:
        """Generate insights from metrics."""
        insights = []
        
        # Performance insights
        if metrics.performance_percentiles['p95'] > 1000:  # 1 second
            insights.append("95% of operations complete in over 1 second - consider performance optimization")
        
        # Usage pattern insights
        if metrics.peak_usage_hours:
            peak_hour = metrics.peak_usage_hours[0]
            insights.append(f"Peak usage occurs at {peak_hour}:00 - consider scaling during this time")
        
        # Operation type insights
        if 'search' in metrics.operations_by_type:
            search_count = metrics.operations_by_type['search']
            total = metrics.total_operations
            search_percentage = (search_count / total) * 100
            
            if search_percentage > 70:
                insights.append(f"Search operations account for {search_percentage:.1f}% of usage - optimize search performance")
        
        return insights
```

### Plugin System

```python
# backend/src/plugins/plugin_manager.py
from typing import Dict, List, Any, Type, Protocol
from abc import ABC, abstractmethod
import importlib
import inspect

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MemoryLinkPlugin(Protocol):
    """Protocol for MemoryLink plugins."""
    
    name: str
    version: str
    description: str
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        ...
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        ...


class MemoryProcessorPlugin(MemoryLinkPlugin):
    """Base class for memory processing plugins."""
    
    @abstractmethod
    async def process_memory(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process memory content and return enhanced metadata."""
        pass


class SearchEnhancerPlugin(MemoryLinkPlugin):
    """Base class for search enhancement plugins."""
    
    @abstractmethod
    async def enhance_search_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance search results with additional data."""
        pass


class PluginManager:
    """Manager for MemoryLink plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, MemoryLinkPlugin] = {}
        self.memory_processors: List[MemoryProcessorPlugin] = []
        self.search_enhancers: List[SearchEnhancerPlugin] = []
        self.logger = logger.bind(component="plugin_manager")
    
    def load_plugin(self, plugin_module_path: str, config: Dict[str, Any] = None) -> bool:
        """Load and initialize a plugin."""
        try:
            # Import plugin module
            module = importlib.import_module(plugin_module_path)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, (MemoryProcessorPlugin, SearchEnhancerPlugin)) and
                    obj not in (MemoryProcessorPlugin, SearchEnhancerPlugin)):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_module_path}")
            
            # Initialize plugin
            plugin_instance = plugin_class()
            plugin_instance.initialize(config or {})
            
            # Register plugin
            self.plugins[plugin_instance.name] = plugin_instance
            
            # Add to appropriate category
            if isinstance(plugin_instance, MemoryProcessorPlugin):
                self.memory_processors.append(plugin_instance)
            elif isinstance(plugin_instance, SearchEnhancerPlugin):
                self.search_enhancers.append(plugin_instance)
            
            self.logger.info(
                "Plugin loaded successfully",
                plugin_name=plugin_instance.name,
                plugin_version=plugin_instance.version
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to load plugin",
                plugin_path=plugin_module_path,
                error=str(e)
            )
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            
            # Remove from categories
            if isinstance(plugin, MemoryProcessorPlugin):
                self.memory_processors.remove(plugin)
            elif isinstance(plugin, SearchEnhancerPlugin):
                self.search_enhancers.remove(plugin)
            
            # Cleanup plugin
            plugin.cleanup()
            
            # Remove from registry
            del self.plugins[plugin_name]
            
            self.logger.info(
                "Plugin unloaded successfully",
                plugin_name=plugin_name
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to unload plugin",
                plugin_name=plugin_name,
                error=str(e)
            )
            return False
    
    async def process_memory_with_plugins(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process memory through all registered memory processor plugins."""
        enhanced_metadata = metadata.copy()
        
        for plugin in self.memory_processors:
            try:
                plugin_metadata = await plugin.process_memory(content, enhanced_metadata)
                enhanced_metadata.update(plugin_metadata)
                
                self.logger.debug(
                    "Memory processed by plugin",
                    plugin_name=plugin.name
                )
                
            except Exception as e:
                self.logger.error(
                    "Plugin failed to process memory",
                    plugin_name=plugin.name,
                    error=str(e)
                )
        
        return enhanced_metadata
    
    async def enhance_search_with_plugins(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance search results through all registered search enhancer plugins."""
        enhanced_results = results.copy()
        
        for plugin in self.search_enhancers:
            try:
                enhanced_results = await plugin.enhance_search_results(query, enhanced_results)
                
                self.logger.debug(
                    "Search results enhanced by plugin",
                    plugin_name=plugin.name
                )
                
            except Exception as e:
                self.logger.error(
                    "Plugin failed to enhance search results",
                    plugin_name=plugin.name,
                    error=str(e)
                )
        
        return enhanced_results
    
    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information about all loaded plugins."""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "type": type(plugin).__name__
            }
            for plugin in self.plugins.values()
        ]


# Example plugin implementation
# plugins/sentiment_analyzer.py
import asyncio
from typing import Dict, Any

class SentimentAnalyzerPlugin(MemoryProcessorPlugin):
    """Plugin to analyze sentiment of memory content."""
    
    name = "sentiment_analyzer"
    version = "1.0.0"
    description = "Analyzes sentiment of memory content"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize sentiment analyzer."""
        self.enabled = config.get('enabled', True)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        pass
    
    async def process_memory(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze sentiment and add to metadata."""
        if not self.enabled:
            return {}
        
        # Simulate sentiment analysis (replace with actual implementation)
        sentiment_score = await self._analyze_sentiment(content)
        
        if sentiment_score['confidence'] >= self.confidence_threshold:
            return {
                'sentiment': sentiment_score['sentiment'],
                'sentiment_confidence': sentiment_score['confidence']
            }
        
        return {}
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Simulate sentiment analysis (replace with real implementation)."""
        # Simulate async operation
        await asyncio.sleep(0.1)
        
        # Simple sentiment analysis simulation
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return {'sentiment': 'positive', 'confidence': 0.8}
        elif negative_count > positive_count:
            return {'sentiment': 'negative', 'confidence': 0.8}
        else:
            return {'sentiment': 'neutral', 'confidence': 0.6}
```

## 📦 Contributing Guidelines

### Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Follow code style** guidelines and run linters
4. **Update documentation** for any public API changes
5. **Submit pull request** with clear description

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Description of testing approach and any new test cases.

## Checklist:
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)

## Additional Notes
```

### Code Review Guidelines

**For Authors:**
- Keep PRs small and focused
- Write clear commit messages
- Include tests and documentation
- Respond promptly to feedback

**For Reviewers:**
- Be constructive and specific
- Focus on code quality, security, and maintainability
- Suggest improvements, don't just point out problems
- Approve when ready, request changes when needed

---

## 🏁 Development Best Practices

### Security Considerations
- Never commit secrets or API keys
- Validate all user inputs
- Use parameterized queries for database operations
- Implement proper error handling without information leakage
- Follow principle of least privilege
- Keep dependencies updated

### Performance Guidelines
- Use async/await for I/O operations
- Implement caching where appropriate
- Optimize database queries
- Profile performance-critical code
- Monitor resource usage

### Documentation Standards
- Document all public APIs
- Include examples in docstrings
- Keep README and guides updated
- Write clear commit messages
- Comment complex algorithms

---

**Ready to contribute to MemoryLink?**

```bash
git clone https://github.com/your-org/memorylink.git
cd memorylink
make setup
make dev
```

Join our community of developers building the future of personal knowledge management!