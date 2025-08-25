# Phase 2: Authentication & Security Implementation

## Overview
This phase implements a comprehensive authentication and security system for MemoryLink, transforming it from a development prototype into a production-ready application with proper access controls, rate limiting, and security hardening.

**Timeline:** 3-5 Days  
**Priority:** HIGH - Required for production  
**Status:** Ready after Phase 1 completion  
**Dependencies:** Phase 1 (Critical Fixes) must be completed first

## Objectives
- Implement JWT-based authentication system
- Add API key management for programmatic access
- Create user registration and login endpoints
- Implement rate limiting and security middleware
- Add CORS and security headers configuration
- Establish audit logging and security monitoring
- Enable user-based data isolation

## Current Security State Analysis

### Existing Security Features ✅
- **Encryption at rest:** Fernet-based encryption with PBKDF2 key derivation
- **Container security:** Non-root user, minimal attack surface
- **Data isolation:** User-based memory separation (by user_id)
- **Input validation:** Pydantic model validation
- **CORS middleware:** Basic CORS configuration present

### Critical Security Gaps 🚨
- **No authentication:** Anyone can access all endpoints
- **No authorization:** User isolation relies only on user_id parameter
- **No rate limiting:** Vulnerable to DoS attacks
- **No audit logging:** No security event tracking
- **No session management:** No user state management

## Implementation Tasks

### Task 2.1: JWT Authentication System (1.5 days)

#### 2.1.1: Authentication Models and Schemas
**File:** `/backend/src/models/auth_models.py`
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class APIKey(BaseModel):
    id: str
    user_id: str
    name: str
    key_preview: str  # First 8 characters for identification
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
```

#### 2.1.2: Password Security Service
**File:** `/backend/src/services/auth_service.py`
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            return payload
        except JWTError:
            return None
    
    def generate_api_key(self, user_id: str, name: str) -> tuple[str, str]:
        """Generate API key and return (key, hash)"""
        api_key = f"ml_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return api_key, key_hash
```

#### 2.1.3: User Database Models
**File:** `/backend/src/db/auth_models.py`
```python
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class DBAPIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    key_preview = Column(String, nullable=False)  # First 8 chars for display
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class DBRefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 2.1.4: Authentication Dependencies
**File:** `/backend/src/api/dependencies.py`
```python
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import hashlib

from ..services.auth_service import AuthService
from ..db.session import get_db
from ..db.auth_models import DBUser, DBAPIKey

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = auth_service.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: DBUser = Depends(get_current_user)
) -> DBUser:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_user_from_api_key(
    api_key: str,
    db: Session = Depends(get_db)
) -> Optional[DBUser]:
    """Validate API key and return associated user"""
    if not api_key.startswith("ml_"):
        return None
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    api_key_record = db.query(DBAPIKey).filter(
        DBAPIKey.key_hash == key_hash,
        DBAPIKey.is_active == True
    ).first()
    
    if not api_key_record:
        return None
    
    # Update last used timestamp
    api_key_record.last_used = datetime.utcnow()
    db.commit()
    
    user = db.query(DBUser).filter(DBUser.id == api_key_record.user_id).first()
    return user if user and user.is_active else None
```

### Task 2.2: Authentication Endpoints (1 day)

#### 2.2.1: Authentication Routes
**File:** `/backend/src/api/routes/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from ...models.auth_models import UserCreate, UserLogin, User, Token, APIKey
from ...services.auth_service import AuthService
from ...db.session import get_db
from ...db.auth_models import DBUser, DBAPIKey, DBRefreshToken
from ...api.dependencies import get_current_active_user, get_auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    # Check if user exists
    if db.query(DBUser).filter(DBUser.email == user_create.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = auth_service.get_password_hash(user_create.password)
    db_user = DBUser(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return User(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        last_login=db_user.last_login
    )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = db.query(DBUser).filter(DBUser.email == user_credentials.email).first()
    
    if not user or not auth_service.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800  # 30 minutes
    )

@router.get("/me", response_model=User)
async def read_current_user(current_user: DBUser = Depends(get_current_active_user)):
    return User(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/api-keys", response_model=APIKey)
async def create_api_key(
    name: str,
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    # Generate API key
    api_key, key_hash = auth_service.generate_api_key(current_user.id, name)
    
    db_api_key = DBAPIKey(
        user_id=current_user.id,
        name=name,
        key_hash=key_hash,
        key_preview=api_key[:8] + "..." + api_key[-4:]
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return APIKey(
        id=db_api_key.id,
        user_id=db_api_key.user_id,
        name=db_api_key.name,
        key_preview=db_api_key.key_preview,
        created_at=db_api_key.created_at,
        last_used=db_api_key.last_used,
        is_active=db_api_key.is_active
    )

@router.get("/api-keys", response_model=List[APIKey])
async def list_api_keys(
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    api_keys = db.query(DBAPIKey).filter(
        DBAPIKey.user_id == current_user.id,
        DBAPIKey.is_active == True
    ).all()
    
    return [
        APIKey(
            id=key.id,
            user_id=key.user_id,
            name=key.name,
            key_preview=key.key_preview,
            created_at=key.created_at,
            last_used=key.last_used,
            is_active=key.is_active
        ) for key in api_keys
    ]
```

### Task 2.3: Rate Limiting Implementation (0.5 day)

#### 2.3.1: Rate Limiting Service
**File:** `/backend/src/services/rate_limit_service.py`
```python
from typing import Dict, Optional
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    async def is_allowed(
        self,
        identifier: str,
        rate_limit: int = 60,  # requests per minute
        window: int = 60  # window in seconds
    ) -> tuple[bool, Dict[str, int]]:
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Get requests for this identifier
        user_requests = self.requests[identifier]
        
        # Remove old requests outside window
        user_requests[:] = [req_time for req_time in user_requests 
                           if current_time - req_time < window]
        
        # Check rate limit
        current_count = len(user_requests)
        allowed = current_count < rate_limit
        
        if allowed:
            user_requests.append(current_time)
        
        # Calculate remaining and reset time
        remaining = max(0, rate_limit - current_count - (1 if allowed else 0))
        reset_time = int(current_time + window)
        
        return allowed, {
            "limit": rate_limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": int(window - (current_time - min(user_requests))) if user_requests else 0
        }
    
    async def _cleanup_old_entries(self):
        current_time = time.time()
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < 3600  # Keep last hour
            ]
            if not self.requests[identifier]:
                del self.requests[identifier]
```

#### 2.3.2: Rate Limiting Middleware
**File:** `/backend/src/middleware/rate_limit.py`
```python
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        rate_limiter,
        calls: int = 60,
        period: int = 60,
        identifier: str = "ip"
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.calls = calls
        self.period = period
        self.identifier = identifier
    
    def get_identifier(self, request: Request) -> str:
        if self.identifier == "ip":
            return request.client.host
        elif self.identifier == "user":
            # Extract user ID from token if available
            auth_header = request.headers.get("authorization")
            if auth_header:
                return auth_header  # Simplified - should extract user ID
            return request.client.host
        return request.client.host
    
    async def dispatch(self, request: Request, call_next):
        identifier = self.get_identifier(request)
        
        # Check rate limit
        allowed, rate_info = await self.rate_limiter.is_allowed(
            identifier, self.calls, self.period
        )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. {self.calls} requests per {self.period} seconds allowed.",
                    "rate_limit": rate_info
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["retry_after"])
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response
```

### Task 2.4: Security Headers and CORS (0.5 day)

#### 2.4.1: Security Middleware
**File:** `/backend/src/middleware/security.py`
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.openai.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response
```

### Task 2.5: Updated Memory Service with Authentication (0.5 day)

#### 2.5.1: Secure Memory Operations
**File:** `/backend/src/api/routes/memory.py` (Updated)
```python
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional

from ...models.memory_models import MemoryCreate, MemoryResponse, SearchQuery, SearchResult
from ...services.memory_service import MemoryService
from ...db.auth_models import DBUser
from ...api.dependencies import get_current_active_user, get_user_from_api_key, get_memory_service

router = APIRouter(prefix="/api/v1", tags=["memory"])

async def get_authenticated_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    jwt_user: Optional[DBUser] = Depends(get_current_active_user)
) -> DBUser:
    """Get user from JWT token or API key"""
    if jwt_user:
        return jwt_user
    
    if x_api_key:
        api_user = await get_user_from_api_key(x_api_key)
        if api_user:
            return api_user
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide JWT token or API key."
    )

@router.post("/memory", response_model=MemoryResponse)
async def add_memory(
    memory: MemoryCreate,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Add a memory for the authenticated user"""
    # Override user_id with authenticated user's ID
    memory.user_id = user.id
    result = await service.add_memory(memory)
    return result

@router.post("/memory/search", response_model=SearchResult)
async def search_memory(
    query: SearchQuery,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Search memories for the authenticated user"""
    # Override user_id with authenticated user's ID
    query.user_id = user.id
    results = await service.search_memories(query)
    return results

@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    user: DBUser = Depends(get_authenticated_user),
    service: MemoryService = Depends(get_memory_service)
):
    """Delete a memory for the authenticated user"""
    success = await service.delete_memory(memory_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "memory_id": memory_id}
```

## Updated Dependencies

### Python Requirements:
```txt
# Add to requirements/base.txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
bcrypt==4.0.1
```

## Configuration Updates

### Environment Variables:
```env
# Security settings
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_CREDENTIALS=true
```

## Testing Requirements

### Authentication Tests:
```python
# tests/unit/test_auth.py
async def test_user_registration():
    # Test user registration flow
    pass

async def test_jwt_token_validation():
    # Test JWT token creation and validation
    pass

async def test_api_key_authentication():
    # Test API key authentication
    pass

async def test_rate_limiting():
    # Test rate limiting functionality
    pass
```

### Security Tests:
```python
# tests/security/test_auth_security.py
async def test_password_hashing():
    # Test password security
    pass

async def test_jwt_expiration():
    # Test token expiration
    pass

async def test_rate_limit_bypass_attempts():
    # Test rate limit security
    pass
```

## Success Criteria

### Authentication System:
- [ ] User registration and login work correctly
- [ ] JWT tokens generate and validate properly
- [ ] API key authentication functions
- [ ] Password security meets standards
- [ ] Session management works properly

### Security Features:
- [ ] Rate limiting prevents abuse
- [ ] Security headers protect against attacks
- [ ] CORS configuration works properly
- [ ] Input validation prevents injection
- [ ] Audit logging captures events

### Integration:
- [ ] Memory operations require authentication
- [ ] User data isolation is enforced
- [ ] API responses include security headers
- [ ] All endpoints respect rate limits
- [ ] Error handling doesn't leak information

## Risk Mitigation

### Security Risks:
- **JWT secret compromise:** Use strong, randomly generated secrets
- **Password attacks:** Implement bcrypt with proper cost factor
- **Token replay:** Use short expiration times and refresh tokens
- **Rate limit bypass:** Implement multiple layers of protection

### Implementation Risks:
- **Database migration:** Careful schema updates with rollback plan
- **Existing data:** Migrate existing memories to user accounts
- **API compatibility:** Maintain backward compatibility where possible
- **Performance impact:** Monitor authentication overhead

This phase transforms MemoryLink from a development prototype into a production-ready application with enterprise-grade security features.