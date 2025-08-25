# Phase 2: Memory Layer Implementation

## Overview
This phase implements the core memory functionality including vector storage, embedding generation, search capabilities, and encryption. This is the heart of the MemoryLink system.

## Objectives
- Integrate ChromaDB for vector storage
- Implement embedding generation with SentenceTransformers
- Create encryption/decryption layer
- Build memory service with add/search operations
- Implement metadata management
- Set up persistence layer

## Implementation Tasks

### 2.1 Vector Database Integration (Day 8-9)

#### ChromaDB Setup
```python
# app/db/vector_store.py
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid

class VectorStore:
    def __init__(self, persist_path: str):
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get the memory collection"""
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"description": "Personal memory storage"}
        )
    
    def add_memory(
        self,
        memory_id: str,
        embedding: List[float],
        metadata: Dict
    ) -> str:
        """Add a memory with its embedding to the vector store"""
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        return memory_id
    
    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar memories"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict if filter_dict else None
        )
        
        return [
            {
                "id": results["ids"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]
    
    def delete_memory(self, memory_id: str):
        """Delete a memory from the vector store"""
        self.collection.delete(ids=[memory_id])
    
    def reset(self):
        """Reset the entire collection"""
        self.client.delete_collection("memories")
        self._initialize_collection()
```

### 2.2 Embedding Generation (Day 9-10)

#### Local Embedding Model
```python
# app/services/embeddings.py
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from app.config import settings

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding model"""
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def generate_embedding(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for text or list of texts"""
        if isinstance(text, str):
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        else:
            embeddings = self.model.encode(text, convert_to_numpy=True)
            return embeddings.tolist()
    
    def batch_generate(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """Generate embeddings in batches for efficiency"""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(batch, convert_to_numpy=True)
            all_embeddings.extend(embeddings.tolist())
        return all_embeddings
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim
```

### 2.3 Encryption Layer (Day 10-11)

#### AES Encryption Implementation
```python
# app/core/encryption.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import json
from typing import Dict, Any

class EncryptionService:
    def __init__(self, key: str = None):
        """Initialize encryption service with key"""
        if key:
            self.key = self._derive_key(key)
        else:
            self.key = None
            
    def _derive_key(self, passphrase: str) -> bytes:
        """Derive encryption key from passphrase"""
        salt = b'memorylink_salt_v1'  # In production, use random salt
        key = PBKDF2(passphrase, salt, dkLen=32)
        return key
    
    def encrypt(self, plaintext: str) -> Dict[str, str]:
        """Encrypt plaintext and return encrypted data with nonce"""
        if not self.key:
            return {"encrypted": False, "data": plaintext}
            
        cipher = AES.new(self.key, AES.MODE_GCM)
        nonce = cipher.nonce
        
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        
        return {
            "encrypted": True,
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8')
        }
    
    def decrypt(self, encrypted_data: Dict[str, str]) -> str:
        """Decrypt encrypted data"""
        if not encrypted_data.get("encrypted"):
            return encrypted_data.get("data", "")
            
        if not self.key:
            raise ValueError("Encryption key not set")
            
        nonce = base64.b64decode(encrypted_data["nonce"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        tag = base64.b64decode(encrypted_data["tag"])
        
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext.decode('utf-8')
    
    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Encrypt dictionary as JSON"""
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: Dict[str, str]) -> Dict[str, Any]:
        """Decrypt to dictionary"""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str) if json_str else {}
```

### 2.4 SQLite Metadata Storage (Day 11-12)

#### Database Models
```python
# app/db/models.py
from sqlalchemy import Column, String, DateTime, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default="default")
    session_id = Column(String, nullable=True)
    
    # Encrypted content
    content_encrypted = Column(JSON, nullable=False)
    
    # Metadata
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Vector reference
    embedding_id = Column(String, nullable=True)
    embedding_model = Column(String, nullable=True)
    
    # Search optimization
    relevance_score = Column(Float, nullable=True)
```

#### Database Session Management
```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base
from app.config import settings

class DatabaseManager:
    def __init__(self, db_path: str):
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
```

### 2.5 Memory Service Implementation (Day 12-14)

#### Complete Memory Service
```python
# app/services/memory_service.py
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from app.db.models import Memory
from app.db.session import DatabaseManager
from app.db.vector_store import VectorStore
from app.services.embeddings import EmbeddingService
from app.core.encryption import EncryptionService
from app.models.schemas import MemoryCreate, MemoryResponse, SearchQuery, SearchResult
import time

class MemoryService:
    def __init__(
        self,
        db_manager: DatabaseManager,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
        encryption_service: EncryptionService
    ):
        self.db = db_manager
        self.vector_store = vector_store
        self.embeddings = embedding_service
        self.encryption = encryption_service
    
    async def add_memory(self, memory_data: MemoryCreate) -> MemoryResponse:
        """Add a new memory to the system"""
        start_time = time.time()
        
        # Generate unique ID
        memory_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = self.embeddings.generate_embedding(memory_data.text)
        
        # Encrypt content
        encrypted_content = self.encryption.encrypt(memory_data.text)
        
        # Store in vector database
        vector_metadata = {
            "user_id": memory_data.user_id,
            "session_id": memory_data.session_id or "",
            "tags": ",".join(memory_data.tags),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.vector_store.add_memory(
            memory_id=memory_id,
            embedding=embedding,
            metadata=vector_metadata
        )
        
        # Store in metadata database
        with self.db.get_session() as session:
            memory = Memory(
                id=memory_id,
                user_id=memory_data.user_id,
                session_id=memory_data.session_id,
                content_encrypted=encrypted_content,
                tags=memory_data.tags,
                metadata=memory_data.metadata,
                embedding_id=memory_id,
                embedding_model=self.embeddings.model.get_name()
            )
            session.add(memory)
            session.commit()
            
            # Create response
            return MemoryResponse(
                id=memory_id,
                text=memory_data.text,
                tags=memory_data.tags,
                metadata=memory_data.metadata,
                timestamp=memory.timestamp,
                user_id=memory_data.user_id,
                embedding_id=memory_id
            )
    
    async def search_memories(self, query: SearchQuery) -> SearchResult:
        """Search for relevant memories"""
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.embeddings.generate_embedding(query.query)
        
        # Build filter for vector search
        filter_dict = {"user_id": query.user_id}
        if query.tags:
            filter_dict["tags"] = {"$in": query.tags}
        
        # Search in vector store
        similar_memories = self.vector_store.search_similar(
            query_embedding=query_embedding,
            top_k=query.top_k,
            filter_dict=filter_dict
        )
        
        # Fetch full memory data from database
        memory_responses = []
        with self.db.get_session() as session:
            for result in similar_memories:
                if result["distance"] <= query.threshold:
                    memory = session.query(Memory).filter(
                        Memory.id == result["id"]
                    ).first()
                    
                    if memory:
                        # Decrypt content
                        decrypted_text = self.encryption.decrypt(
                            memory.content_encrypted
                        )
                        
                        memory_responses.append(MemoryResponse(
                            id=memory.id,
                            text=decrypted_text,
                            tags=memory.tags,
                            metadata=memory.metadata,
                            timestamp=memory.timestamp,
                            user_id=memory.user_id,
                            embedding_id=memory.embedding_id
                        ))
        
        query_time = (time.time() - start_time) * 1000
        
        return SearchResult(
            memories=memory_responses,
            total=len(memory_responses),
            query_time_ms=query_time
        )
    
    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete a memory"""
        with self.db.get_session() as session:
            memory = session.query(Memory).filter(
                Memory.id == memory_id,
                Memory.user_id == user_id
            ).first()
            
            if memory:
                # Delete from vector store
                self.vector_store.delete_memory(memory_id)
                
                # Delete from database
                session.delete(memory)
                session.commit()
                return True
            
            return False
    
    async def get_memory_stats(self, user_id: str) -> Dict:
        """Get memory statistics for a user"""
        with self.db.get_session() as session:
            total_memories = session.query(Memory).filter(
                Memory.user_id == user_id
            ).count()
            
            # Get tag distribution
            memories = session.query(Memory).filter(
                Memory.user_id == user_id
            ).all()
            
            tag_counts = {}
            for memory in memories:
                for tag in memory.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            return {
                "total_memories": total_memories,
                "tag_distribution": tag_counts,
                "user_id": user_id
            }
```

### 2.6 Updated API Implementation (Day 14)

#### Complete Memory Endpoints
```python
# app/api/routes/memory.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import MemoryCreate, MemoryResponse, SearchQuery, SearchResult
from app.services.memory_service import MemoryService
from app.api.dependencies import get_memory_service

router = APIRouter()

@router.post("/memory", response_model=MemoryResponse)
async def add_memory(
    memory: MemoryCreate,
    service: MemoryService = Depends(get_memory_service)
):
    """Add a new memory to the system"""
    try:
        result = await service.add_memory(memory)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/search", response_model=SearchResult)
async def search_memory(
    query: SearchQuery,
    service: MemoryService = Depends(get_memory_service)
):
    """Search for relevant memories"""
    try:
        results = await service.search_memories(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: str = "default",
    service: MemoryService = Depends(get_memory_service)
):
    """Delete a memory"""
    success = await service.delete_memory(memory_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "memory_id": memory_id}

@router.get("/memory/stats")
async def get_stats(
    user_id: str = "default",
    service: MemoryService = Depends(get_memory_service)
):
    """Get memory statistics"""
    stats = await service.get_memory_stats(user_id)
    return stats
```

## Updated Dependencies

### Python Requirements

**requirements/base.txt** (additions)
```
chromadb==0.4.18
sentence-transformers==2.2.2
sqlalchemy==2.0.23
pycryptodome==3.19.0
numpy==1.24.3
torch==2.1.0
```

## Testing

### Integration Tests
```python
# tests/integration/test_memory_flow.py
import pytest
from app.services.memory_service import MemoryService

@pytest.mark.asyncio
async def test_memory_lifecycle(memory_service):
    # Add memory
    memory_data = MemoryCreate(
        text="Important meeting notes about project X",
        tags=["meeting", "project-x"],
        metadata={"priority": "high"}
    )
    
    created = await memory_service.add_memory(memory_data)
    assert created.id is not None
    
    # Search for memory
    query = SearchQuery(
        query="project meeting",
        top_k=5
    )
    
    results = await memory_service.search_memories(query)
    assert len(results.memories) > 0
    assert "project-x" in results.memories[0].tags
    
    # Delete memory
    deleted = await memory_service.delete_memory(
        created.id, 
        "default"
    )
    assert deleted == True
```

## Performance Optimization

### Caching Strategy
```python
# app/core/cache.py
from functools import lru_cache
import hashlib

class EmbeddingCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
    
    def get_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str):
        key = self.get_key(text)
        return self.cache.get(key)
    
    def set(self, text: str, embedding):
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction
            self.cache.pop(next(iter(self.cache)))
        key = self.get_key(text)
        self.cache[key] = embedding
```

## Validation Checklist

### Core Functionality
- [ ] Vector store initialized
- [ ] Embeddings generated correctly
- [ ] Encryption/decryption working
- [ ] Memory add operation successful
- [ ] Memory search returning results
- [ ] Metadata stored properly

### Performance
- [ ] Search latency < 500ms
- [ ] Batch embedding processing
- [ ] Caching implemented
- [ ] Database indices created

### Security
- [ ] Content encrypted at rest
- [ ] Key derivation secure
- [ ] No plaintext in logs
- [ ] User isolation working

## Deliverables

1. **Working Memory Service**
   - Add memory with encryption
   - Search with semantic similarity
   - Delete functionality
   - Statistics endpoint

2. **Storage Layer**
   - ChromaDB integration
   - SQLite metadata storage
   - Persistent data across restarts

3. **Security Implementation**
   - AES-256 encryption
   - Key management
   - Secure storage

## Success Metrics

- Memory operations complete successfully
- Search returns relevant results
- Data persists across restarts
- Encryption verified working
- Performance within targets

## Next Phase

Phase 3 will focus on integration and API enhancements:
- MCP protocol compliance
- Advanced search features
- Batch operations
- API authentication
- Rate limiting