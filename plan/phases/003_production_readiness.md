# Phase 3: Production Readiness & Monitoring

## Overview
This phase focuses on making MemoryLink production-ready with comprehensive monitoring, alerting, performance optimization, and operational excellence. Building on the solid deployment infrastructure already in place, this phase completes the production monitoring stack and operational procedures.

**Timeline:** 5-7 Days  
**Priority:** HIGH - Required for production deployment  
**Status:** Ready after Phase 2 completion  
**Dependencies:** Phase 1 (Critical Fixes) and Phase 2 (Authentication) must be completed

## Objectives
- Complete monitoring and alerting infrastructure
- Implement performance optimization and caching
- Set up comprehensive logging and observability
- Complete CI/CD pipeline with deployment automation
- Establish operational runbooks and procedures
- Implement backup and disaster recovery
- Add health checks and service monitoring
- Enable auto-scaling and resource management

## Current Production Infrastructure Analysis

### Existing Production-Ready Components ✅
- **Kubernetes manifests:** Complete with HPA, PDB, network policies
- **Docker configuration:** Production-hardened with security best practices
- **Prometheus integration:** Metrics collection framework ready
- **Grafana dashboards:** Template dashboards configured
- **Resource management:** Proper limits, requests, and scaling policies
- **Security hardening:** Non-root containers, network isolation
- **Health checks:** Kubernetes probes configured
- **Persistent storage:** PVC configuration for data persistence

### Missing Production Components 🚨
- **Alert Manager configuration:** No alerting rules defined
- **Log aggregation:** ELK/Loki stack not configured
- **Performance monitoring:** APM and tracing missing
- **Backup validation:** Automated backup testing missing
- **Operational runbooks:** No incident response procedures
- **CI/CD completion:** Build/deploy pipeline incomplete

## Implementation Tasks

### Task 3.1: Complete Monitoring & Alerting Stack (1.5 days)

#### 3.1.1: Prometheus Alerting Rules
**File:** `/k8s/monitoring/prometheus-alerts.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alerts
  namespace: memorylink
data:
  alerts.yaml: |
    groups:
    - name: memorylink.rules
      rules:
      # Application Health
      - alert: MemoryLinkDown
        expr: up{job="memorylink"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MemoryLink instance is down"
          description: "MemoryLink instance {{ $labels.instance }} has been down for more than 1 minute."
      
      # Performance Alerts
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket{job="memorylink"}) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s for {{ $labels.instance }}"
      
      # Memory Usage
      - alert: HighMemoryUsage
        expr: (process_resident_memory_bytes{job="memorylink"} / 1024 / 1024 / 1024) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}GB for instance {{ $labels.instance }}"
      
      # Database Connectivity
      - alert: DatabaseConnectionFailure
        expr: increase(database_connection_errors_total[5m]) > 5
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failures"
          description: "{{ $value }} database connection failures in the last 5 minutes"
      
      # Vector Store Health
      - alert: VectorStoreErrors
        expr: increase(vector_store_operation_errors_total[5m]) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Vector store operation errors"
          description: "{{ $value }} vector store errors in the last 5 minutes"
      
      # API Rate Limiting
      - alert: HighRateLimitHits
        expr: increase(rate_limit_exceeded_total[5m]) > 50
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High rate limit violations"
          description: "{{ $value }} rate limit violations in the last 5 minutes"
      
      # Resource Usage
      - alert: PodCPUThrottling
        expr: rate(container_cpu_cfs_throttled_seconds_total{container="memorylink"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pod CPU throttling detected"
          description: "Pod {{ $labels.pod }} is experiencing CPU throttling"
      
      # Embedding Service
      - alert: EmbeddingServiceSlow
        expr: histogram_quantile(0.95, embedding_generation_duration_seconds_bucket) > 5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Embedding generation is slow"
          description: "95th percentile embedding generation time is {{ $value }}s"
```

#### 3.1.2: AlertManager Configuration
**File:** `/k8s/monitoring/alertmanager-config.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: memorylink
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: 'smtp.gmail.com:587'
      smtp_from: 'memorylink-alerts@company.com'
      smtp_auth_username: 'memorylink-alerts@company.com'
      smtp_auth_password_file: '/etc/alertmanager/smtp_password'
    
    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'web.hook'
      routes:
      - match:
          severity: critical
        receiver: 'critical-alerts'
        group_wait: 5s
        repeat_interval: 5m
      - match:
          severity: warning
        receiver: 'warning-alerts'
        repeat_interval: 30m
    
    receivers:
    - name: 'web.hook'
      webhook_configs:
      - url: 'http://slack-webhook:5000/webhook'
        send_resolved: true
    
    - name: 'critical-alerts'
      email_configs:
      - to: 'devops@company.com'
        subject: '[CRITICAL] MemoryLink Alert - {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
          {{ end }}
      slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-critical'
        title: 'MemoryLink Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
    
    - name: 'warning-alerts'
      email_configs:
      - to: 'team@company.com'
        subject: '[WARNING] MemoryLink Alert - {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

#### 3.1.3: Enhanced Application Metrics
**File:** `/backend/src/services/metrics_service.py`
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
from functools import wraps
from typing import Callable
import psutil
import asyncio

# Application Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
MEMORY_OPERATIONS = Counter('memory_operations_total', 'Total memory operations', ['operation', 'status'])
EMBEDDING_DURATION = Histogram('embedding_generation_duration_seconds', 'Embedding generation duration')
VECTOR_STORE_OPERATIONS = Counter('vector_store_operations_total', 'Vector store operations', ['operation', 'status'])
VECTOR_STORE_ERRORS = Counter('vector_store_operation_errors_total', 'Vector store operation errors', ['operation', 'error_type'])
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
DATABASE_CONNECTION_ERRORS = Counter('database_connection_errors_total', 'Database connection errors')
RATE_LIMIT_EXCEEDED = Counter('rate_limit_exceeded_total', 'Rate limit exceeded count', ['identifier_type'])
ACTIVE_USERS = Gauge('active_users_count', 'Number of active users')
MEMORY_USAGE = Gauge('process_memory_usage_bytes', 'Process memory usage in bytes')
CPU_USAGE = Gauge('process_cpu_usage_percent', 'Process CPU usage percentage')

class MetricsService:
    def __init__(self):
        self.start_time = time.time()
        # Start background metrics collection
        asyncio.create_task(self._collect_system_metrics())
    
    @staticmethod
    def track_request_metrics(func: Callable) -> Callable:
        """Decorator to track HTTP request metrics"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = kwargs.get('request', args[0] if args else None).method if hasattr(kwargs.get('request', args[0] if args else None), 'method') else 'UNKNOWN'
            endpoint = func.__name__
            
            try:
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
                return result
            except Exception as e:
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=500).inc()
                raise
            finally:
                REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
        
        return wrapper
    
    @staticmethod
    def track_memory_operation(operation: str):
        """Decorator to track memory operations"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    MEMORY_OPERATIONS.labels(operation=operation, status='success').inc()
                    return result
                except Exception as e:
                    MEMORY_OPERATIONS.labels(operation=operation, status='error').inc()
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def track_embedding_generation(func: Callable) -> Callable:
        """Decorator to track embedding generation metrics"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                EMBEDDING_DURATION.observe(time.time() - start_time)
                return result
            except Exception as e:
                EMBEDDING_DURATION.observe(time.time() - start_time)
                raise
        return wrapper
    
    @staticmethod
    def track_vector_operation(operation: str):
        """Decorator to track vector store operations"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    VECTOR_STORE_OPERATIONS.labels(operation=operation, status='success').inc()
                    return result
                except Exception as e:
                    VECTOR_STORE_OPERATIONS.labels(operation=operation, status='error').inc()
                    VECTOR_STORE_ERRORS.labels(operation=operation, error_type=type(e).__name__).inc()
                    raise
            return wrapper
        return decorator
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics"""
        while True:
            try:
                # Memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                MEMORY_USAGE.set(memory_info.rss)
                
                # CPU usage
                cpu_percent = process.cpu_percent()
                CPU_USAGE.set(cpu_percent)
                
                await asyncio.sleep(15)  # Collect every 15 seconds
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def update_active_users(self, count: int):
        """Update active users gauge"""
        ACTIVE_USERS.set(count)
    
    def update_database_connections(self, count: int):
        """Update database connections gauge"""
        DATABASE_CONNECTIONS.set(count)
    
    def record_database_error(self):
        """Record database connection error"""
        DATABASE_CONNECTION_ERRORS.inc()
    
    def record_rate_limit_exceeded(self, identifier_type: str = "ip"):
        """Record rate limit exceeded event"""
        RATE_LIMIT_EXCEEDED.labels(identifier_type=identifier_type).inc()
```

### Task 3.2: Log Aggregation and APM (1.5 days)

#### 3.2.1: Structured Logging Configuration
**File:** `/backend/src/utils/logger.py` (Enhanced)
```python
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
import traceback
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context"""
    
    def add_fields(self, log_record, record, message_dict):
        super(StructuredFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add service info
        log_record['service'] = 'memorylink'
        log_record['version'] = '1.0.0'
        
        # Add request context
        request_id = request_id_var.get('')
        if request_id:
            log_record['request_id'] = request_id
            
        user_id = user_id_var.get('')
        if user_id:
            log_record['user_id'] = user_id
        
        # Add level
        log_record['level'] = record.levelname
        
        # Add location info for errors
        if record.levelno >= logging.ERROR:
            log_record['filename'] = record.filename
            log_record['lineno'] = record.lineno
            log_record['funcName'] = record.funcName
            
            # Add exception info if available
            if record.exc_info:
                log_record['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': traceback.format_exception(*record.exc_info)
                }

class SecurityAuditLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger('security_audit')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_auth_attempt(self, email: str, success: bool, ip_address: str, user_agent: str):
        """Log authentication attempt"""
        self.logger.info("Authentication attempt", extra={
            'event_type': 'auth_attempt',
            'email': email,
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent
        })
    
    def log_rate_limit_exceeded(self, identifier: str, endpoint: str, limit: int):
        """Log rate limit exceeded event"""
        self.logger.warning("Rate limit exceeded", extra={
            'event_type': 'rate_limit_exceeded',
            'identifier': identifier,
            'endpoint': endpoint,
            'limit': limit
        })
    
    def log_suspicious_activity(self, description: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        self.logger.warning("Suspicious activity detected", extra={
            'event_type': 'suspicious_activity',
            'description': description,
            'details': details
        })
    
    def log_data_access(self, user_id: str, operation: str, resource_type: str, resource_id: str):
        """Log data access events"""
        self.logger.info("Data access", extra={
            'event_type': 'data_access',
            'user_id': user_id,
            'operation': operation,
            'resource_type': resource_type,
            'resource_id': resource_id
        })

def setup_logging(log_level: str = "INFO"):
    """Setup application logging"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove default handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    return root_logger

# Middleware for request context
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context to logs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user ID if available (from JWT or API key)
        user_id = getattr(request.state, 'user_id', '')
        if user_id:
            user_id_var.set(user_id)
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
```

#### 3.2.2: Distributed Tracing Setup
**File:** `/backend/src/services/tracing_service.py`
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import os

def setup_tracing(app, service_name: str = "memorylink"):
    """Setup distributed tracing with Jaeger"""
    
    if not os.getenv("JAEGER_ENABLED", "false").lower() == "true":
        return
    
    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_AGENT_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument HTTP clients
    HTTPXClientInstrumentor().instrument()
    
    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument()
    
    return trace.get_tracer(service_name)

# Custom tracing decorators
def trace_function(operation_name: str):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("function.name", func.__name__)
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("function.result", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("function.name", func.__name__)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("function.result", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
```

### Task 3.3: Performance Optimization & Caching (1.5 days)

#### 3.3.1: Redis Caching Layer
**File:** `/backend/src/services/cache_service.py`
```python
import redis
import json
import pickle
import hashlib
from typing import Any, Optional, Union
from datetime import timedelta
import asyncio
import aioredis

class CacheService:
    """Redis-based caching service with async support"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.sync_client = redis.from_url(redis_url, decode_responses=False)
    
    async def initialize(self):
        """Initialize async Redis connection"""
        self.redis_client = await aioredis.from_url(
            self.redis_url,
            encoding='utf-8',
            decode_responses=False
        )
    
    def _serialize_key(self, key: str, namespace: str = "ml") -> str:
        """Create namespaced, hashed key"""
        full_key = f"{namespace}:{key}"
        return hashlib.md5(full_key.encode()).hexdigest()
    
    async def get(self, key: str, namespace: str = "ml") -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            await self.initialize()
        
        cache_key = self._serialize_key(key, namespace)
        try:
            value = await self.redis_client.get(cache_key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Union[int, timedelta] = 3600,
        namespace: str = "ml"
    ) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            await self.initialize()
        
        cache_key = self._serialize_key(key, namespace)
        try:
            serialized_value = pickle.dumps(value)
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            return await self.redis_client.setex(cache_key, ttl, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str, namespace: str = "ml") -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            await self.initialize()
        
        cache_key = self._serialize_key(key, namespace)
        try:
            return await self.redis_client.delete(cache_key) > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str, namespace: str = "ml") -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            await self.initialize()
        
        cache_key = self._serialize_key(key, namespace)
        try:
            return await self.redis_client.exists(cache_key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

# Caching decorators
def cache_result(ttl: int = 3600, namespace: str = "ml"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            cache_service = CacheService()
            
            # Try to get from cache first
            cached_result = await cache_service.get(cache_key, namespace)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl, namespace)
            
            return result
        return wrapper
    return decorator

# Embedding cache optimization
class EmbeddingCache:
    """Specialized cache for embeddings with similarity search"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.namespace = "embeddings"
    
    async def get_embedding(self, text: str) -> Optional[list]:
        """Get cached embedding for text"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return await self.cache.get(text_hash, self.namespace)
    
    async def set_embedding(self, text: str, embedding: list, ttl: int = 86400):
        """Cache embedding for text (24 hour default TTL)"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        await self.cache.set(text_hash, embedding, ttl, self.namespace)
    
    async def get_similar_embeddings(self, text: str, threshold: float = 0.95) -> list:
        """Get similar cached embeddings (basic implementation)"""
        # This would be enhanced with vector similarity search in Redis
        # For now, just return exact matches
        return await self.get_embedding(text)
```

#### 3.3.2: Database Connection Pooling
**File:** `/backend/src/db/connection_pool.py`
```python
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

class DatabasePool:
    """Enhanced database connection pool management"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool with optimized settings"""
        
        # Pool configuration for production
        pool_settings = {
            "poolclass": QueuePool,
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
            "pool_pre_ping": True,  # Validate connections before use
            "connect_args": {
                "check_same_thread": False,  # For SQLite
                "timeout": 20
            }
        }
        
        self.engine = create_engine(
            self.database_url,
            **pool_settings,
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        """Get database session with automatic cleanup"""
        return self.SessionLocal()
    
    def get_pool_status(self) -> dict:
        """Get connection pool status for monitoring"""
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalidated": pool.invalidated()
        }
    
    def close_all_connections(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
```

### Task 3.4: Complete CI/CD Pipeline (1 day)

#### 3.4.1: Enhanced GitHub Actions Workflow
**File:** `.github/workflows/deploy.yml`
```yaml
name: Build and Deploy MemoryLink

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: memorylink

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_USER: test_user
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements/*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        pip install -r requirements/dev.txt
    
    - name: Run security scan
      run: |
        bandit -r backend/src/ -f json -o bandit-report.json
        safety check --json --output safety-report.json
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=backend/src --cov-report=xml --cov-report=html
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    permissions:
      contents: read
      packages: write
    
    outputs:
      image-tag: ${{ steps.image-tag.outputs.tag }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Generate image tag
      id: image-tag
      run: |
        if [[ $GITHUB_REF == refs/heads/main ]]; then
          echo "tag=latest" >> $GITHUB_OUTPUT
        else
          echo "tag=develop" >> $GITHUB_OUTPUT
        fi
        echo "sha-tag=${{ github.sha }}" >> $GITHUB_OUTPUT
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        platforms: linux/amd64,linux/arm64
        tags: |
          ${{ env.REGISTRY }}/${{ github.repository }}:${{ steps.image-tag.outputs.tag }}
          ${{ env.REGISTRY }}/${{ github.repository }}:${{ steps.image-tag.outputs.sha-tag }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Run security scan on image
      uses: anchore/scan-action@v3
      with:
        image: ${{ env.REGISTRY }}/${{ github.repository }}:${{ steps.image-tag.outputs.sha-tag }}
        output-format: table

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    environment:
      name: staging
      url: https://staging.memorylink.com
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to staging
      run: |
        kubectl set image deployment/memorylink memorylink=${{ env.REGISTRY }}/${{ github.repository }}:${{ needs.build.outputs.image-tag }} -n memorylink-staging
        kubectl rollout status deployment/memorylink -n memorylink-staging --timeout=600s
    
    - name: Run smoke tests
      run: |
        sleep 30  # Wait for deployment to settle
        curl -f https://staging.memorylink.com/health || exit 1
        # Add more smoke tests here

  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    environment:
      name: production
      url: https://memorylink.com
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG_PRODUCTION }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to production
      run: |
        kubectl set image deployment/memorylink memorylink=${{ env.REGISTRY }}/${{ github.repository }}:${{ needs.build.outputs.image-tag }} -n memorylink-production
        kubectl rollout status deployment/memorylink -n memorylink-production --timeout=600s
    
    - name: Run production smoke tests
      run: |
        sleep 60  # Wait longer for production deployment
        curl -f https://memorylink.com/health || exit 1
        # Add comprehensive smoke tests
    
    - name: Notify team on success
      uses: 8398a7/action-slack@v3
      if: success()
      with:
        status: success
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        message: 'MemoryLink deployed successfully to production! 🚀'
    
    - name: Notify team on failure
      uses: 8398a7/action-slack@v3
      if: failure()
      with:
        status: failure
        channel: '#alerts'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        message: 'MemoryLink production deployment failed! 🚨'
```

### Task 3.5: Operational Runbooks (1 day)

#### 3.5.1: Incident Response Runbook
**File:** `/docs/operations/incident-response.md`
```markdown
# MemoryLink Incident Response Runbook

## Alert Classifications

### Critical Alerts (P1)
- Service completely down
- Data loss or corruption
- Security breach
- Response time: 15 minutes

### High Priority (P2)
- Performance degradation >50%
- Partial service outage
- Authentication failures
- Response time: 1 hour

### Medium Priority (P3)
- Minor performance issues
- Non-critical feature failures
- Response time: 4 hours

## Response Procedures

### Service Down (MemoryLinkDown)
1. **Immediate Actions (0-5 minutes)**
   ```bash
   # Check service status
   kubectl get pods -n memorylink
   kubectl describe deployment memorylink -n memorylink
   kubectl logs -l app=memorylink -n memorylink --tail=100
   ```

2. **Diagnosis (5-15 minutes)**
   ```bash
   # Check resource usage
   kubectl top pods -n memorylink
   
   # Check events
   kubectl get events -n memorylink --sort-by=.metadata.creationTimestamp
   
   # Check dependencies
   kubectl get pods -n postgres
   kubectl get pods -n redis
   ```

3. **Resolution Steps**
   - If pod is crashlooping: Check logs and fix configuration
   - If resource exhaustion: Scale up replicas or increase limits
   - If dependency failure: Restart dependent services
   - If persistent issues: Rollback to previous version

### High Response Time Alert
1. **Check Metrics**
   ```bash
   # View Grafana dashboard
   # Check prometheus metrics: http_request_duration_seconds
   ```

2. **Common Causes & Solutions**
   - Database connection issues: Check connection pool
   - Vector store slowness: Check ChromaDB performance
   - Memory pressure: Increase memory limits or scale pods
   - Rate limiting: Check if legitimate traffic spike

### Database Connection Failures
1. **Immediate Check**
   ```bash
   kubectl get pods -n postgres
   kubectl logs -l app=postgres -n postgres --tail=50
   ```

2. **Connection Pool Issues**
   ```python
   # Check pool status via metrics endpoint
   curl http://memorylink:8080/metrics | grep database_connections
   ```

3. **Resolution**
   - Restart database if hung
   - Increase connection pool size
   - Check for connection leaks in application

## Rollback Procedures

### Application Rollback
```bash
# Get current deployment
kubectl get deployments -n memorylink

# Rollback to previous version
kubectl rollout undo deployment/memorylink -n memorylink

# Check rollback status
kubectl rollout status deployment/memorylink -n memorylink
```

### Database Rollback
```bash
# For schema changes
kubectl exec -it postgres-pod -- psql -d memorylink
# Run rollback SQL scripts from /migrations/rollback/
```

## Escalation Matrix

### Level 1: On-call Engineer
- Initial response and diagnosis
- Execute standard runbook procedures
- Escalate if not resolved in 30 minutes (P1) or 2 hours (P2)

### Level 2: Senior Engineer + Team Lead
- Complex debugging and analysis
- Architecture-level decisions
- Coordinate with other teams if needed

### Level 3: Engineering Manager + CTO
- Business impact decisions
- External communication
- Post-incident review coordination

## Communication Templates

### Initial Alert (Slack)
```
🚨 P1 INCIDENT: [Brief Description]
Status: Investigating
Impact: [Customer/Internal impact]
ETA for update: [Time]
War room: [Link if applicable]
```

### Status Update
```
📊 INCIDENT UPDATE: [Brief Description]
Status: [Investigating/Fixing/Monitoring]
Actions taken: [Brief summary]
Next steps: [What's happening next]
ETA for resolution: [Time estimate]
```

### Resolution Notice
```
✅ RESOLVED: [Brief Description]
Resolution: [What was done]
Duration: [Total incident time]
Post-mortem: [Link when available]
```

## Post-Incident Procedures

### Immediate (Within 24 hours)
- Create incident report document
- Schedule post-mortem meeting
- Identify immediate action items

### Post-Mortem Meeting (Within 1 week)
- Timeline review
- Root cause analysis
- Action items identification
- Process improvements

### Follow-up (Within 2 weeks)
- Implement preventive measures
- Update monitoring and alerting
- Update runbooks based on learnings
- Communicate improvements to stakeholders
```

## Updated Dependencies

### Python Requirements:
```txt
# Add to requirements/base.txt
redis==4.6.0
aioredis==2.0.1
pythonjsonlogger==2.0.7
prometheus-client==0.17.1
opentelemetry-api==1.19.0
opentelemetry-sdk==1.19.0
opentelemetry-exporter-jaeger==1.19.0
opentelemetry-instrumentation-fastapi==0.40b0
opentelemetry-instrumentation-httpx==0.40b0
opentelemetry-instrumentation-sqlalchemy==0.40b0
psutil==5.9.5
```

## Success Criteria

### Monitoring & Alerting:
- [ ] Prometheus alerts configured and tested
- [ ] AlertManager routing rules working
- [ ] Grafana dashboards showing real-time data
- [ ] Log aggregation collecting structured logs
- [ ] Distributed tracing capturing request flows

### Performance & Caching:
- [ ] Redis caching reducing database load
- [ ] Connection pooling optimizing DB connections
- [ ] Response times improved by 30%+
- [ ] Memory usage stable under load
- [ ] Auto-scaling responding to traffic

### Operations:
- [ ] CI/CD pipeline deploying automatically
- [ ] Rollback procedures tested and documented
- [ ] Incident response runbooks available
- [ ] Team trained on operational procedures
- [ ] Monitoring coverage for all critical paths

This phase completes the production readiness of MemoryLink, providing enterprise-grade monitoring, performance optimization, and operational procedures for reliable production deployment.