# MemoryLink Docker Deployment Guide

## Overview

This guide covers the complete Docker containerization and deployment setup for MemoryLink, including development and production configurations, Kubernetes deployment, and operational procedures.

## 📁 Project Structure

```
MemoryLink/
├── Dockerfile                      # Multi-stage production Docker build
├── docker-compose.yml             # Development environment
├── docker-compose.prod.yml        # Production environment
├── .dockerignore                   # Build optimization
├── Makefile                        # Development commands
├── docker/
│   └── entrypoint.sh              # Container initialization script
├── scripts/
│   ├── build.sh                   # Docker build automation
│   ├── deploy.sh                  # Deployment automation
│   └── test.sh                    # Container testing
├── k8s/                           # Kubernetes manifests
│   ├── base/                      # Base Kubernetes resources
│   └── overlays/                  # Environment-specific configs
│       ├── development/
│       └── production/
├── requirements/                   # Python dependencies
│   ├── base.txt                   # Core dependencies
│   ├── dev.txt                    # Development dependencies
│   └── prod.txt                   # Production optimizations
└── config/
    └── .env.example               # Environment template
```

## 🚀 Quick Start

### Development Setup

```bash
# 1. Clone and setup
git clone <repository>
cd MemoryLink

# 2. Complete development setup (creates .env, builds image, starts services)
make dev

# 3. Verify deployment
make health
```

### Production Setup

```bash
# 1. Build production image
make build-prod

# 2. Configure environment
cp config/.env.example .env
# Edit .env with production values

# 3. Start production services
make start-prod

# 4. Verify deployment
make health
```

## 🐳 Docker Configuration

### Dockerfile Features

- **Multi-stage build** for optimized image size
- **Security hardening** with non-root user
- **Health checks** for container monitoring  
- **Environment-based configuration**
- **Cross-platform compatibility**

### Key Security Features

```dockerfile
# Non-root user execution
RUN groupadd -r memorylink && \
    useradd -r -g memorylink -d /app -s /bin/bash memorylink
USER memorylink

# Health monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Resource constraints in compose
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
```

### Environment Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MEMORYLINK_ENV` | Environment (dev/prod) | `production` | ✓ |
| `MEMORYLINK_HOST` | Server bind address | `0.0.0.0` | ✓ |
| `MEMORYLINK_PORT` | Server port | `8080` | ✓ |
| `MEMORYLINK_ENCRYPTION_KEY` | Data encryption key | - | ✓ |
| `MEMORYLINK_DATA_PATH` | Data storage path | `/data` | ✓ |

## 🛠️ Build System

### Build Script Features

```bash
# Build development image
./scripts/build.sh --env development --tag dev

# Build with multiple platforms
./scripts/build.sh --multi-platform --tag v1.0.0

# Build and push to registry
./scripts/build.sh --push --registry your-registry.com

# Build with security scanning
./scripts/build.sh --tag latest  # Automatically runs Docker Scout if available
```

### Build Arguments

- `BUILD_ENV`: Target environment (development/production)
- `APP_VERSION`: Application version tag
- `BUILD_DATE`: Build timestamp
- `VCS_REF`: Git commit reference

## 🚢 Deployment Options

### 1. Docker Compose (Recommended for Development)

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# With custom environment
MEMORYLINK_VERSION=v1.0.0 docker-compose -f docker-compose.prod.yml up -d
```

### 2. Kubernetes Deployment

```bash
# Development deployment
kubectl apply -k k8s/overlays/development

# Production deployment  
kubectl apply -k k8s/overlays/production

# Using deployment script
./scripts/deploy.sh -t kubernetes -e production start
```

### 3. Standalone Docker

```bash
# Basic run
docker run -d -p 8080:8080 \
  -v memorylink-data:/data \
  -e MEMORYLINK_ENCRYPTION_KEY="your-key" \
  memorylink:latest

# Production run with all options
docker run -d \
  --name memorylink \
  --restart unless-stopped \
  -p 8080:8080 \
  -v /opt/memorylink/data:/data:rw \
  -v /opt/memorylink/logs:/logs:rw \
  --memory=2g \
  --cpus=1.0 \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --cap-add CHOWN,DAC_OVERRIDE,SETGID,SETUID \
  -e MEMORYLINK_ENV=production \
  -e MEMORYLINK_ENCRYPTION_KEY="${ENCRYPTION_KEY}" \
  memorylink:latest
```

## ☸️ Kubernetes Deployment

### Kustomize Structure

The deployment uses Kustomize for environment management:

```
k8s/
├── base/                    # Common resources
│   ├── deployment.yaml     # Application deployment
│   ├── service.yaml        # Service definitions
│   ├── configmap.yaml      # Configuration
│   ├── secret.yaml         # Secrets template
│   └── persistentvolume.yaml # Storage
└── overlays/
    ├── development/        # Dev-specific patches
    └── production/         # Prod-specific patches
        ├── hpa.yaml       # Auto-scaling
        ├── network-policy.yaml # Network security
        └── pod-disruption-budget.yaml # Availability
```

### Production Features

- **Horizontal Pod Autoscaling** (2-10 replicas based on CPU/memory)
- **Network Policies** for security isolation
- **Pod Disruption Budget** for high availability
- **Resource limits** and requests
- **Security contexts** and RBAC

### Deployment Commands

```bash
# Deploy to development
make deploy-k8s-dev

# Deploy to production
make deploy-k8s-prod

# Scale deployment
make scale-up    # Scale to 3 replicas
make scale-down  # Scale to 1 replica

# Manual scaling
kubectl scale deployment/memorylink-deployment --replicas=5 -n memorylink-prod
```

## 📊 Monitoring & Health Checks

### Health Endpoints

- **Health**: `GET /api/v1/health` - Basic health status
- **Readiness**: `GET /api/v1/readiness` - Service readiness
- **Metrics**: `GET /metrics` - Prometheus metrics (if enabled)

### Container Health Checks

```yaml
# Docker Compose
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

# Kubernetes
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 30
```

### Monitoring Stack (Production)

```bash
# Enable monitoring profile
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

## 💾 Data Persistence

### Volume Configuration

```yaml
# Development (Docker Compose)
volumes:
  - memorylink-data:/data           # Vector database
  - memorylink-logs:/logs           # Application logs

# Production (Kubernetes)
volumes:
  - name: data-storage
    persistentVolumeClaim:
      claimName: memorylink-data-pvc
```

### Backup Strategy

```bash
# Create backup
make backup

# Automated backup (production)
docker-compose -f docker-compose.prod.yml --profile backup up -d

# Manual backup
./scripts/deploy.sh backup
```

### Data Locations

- **Vector Database**: `/data/vector` (ChromaDB)
- **Metadata Database**: `/data/metadata/memorylink.db` (SQLite)
- **Logs**: `/logs` or `/data/logs`
- **Backups**: `/data/backups`

## 🔒 Security Configuration

### Container Security

- **Non-root user execution** (UID 1000)
- **Read-only root filesystem** where possible
- **Dropped capabilities** (ALL) with minimal additions
- **No privilege escalation**
- **Security context** constraints

### Network Security

```yaml
# Kubernetes Network Policy
spec:
  podSelector:
    matchLabels:
      app: memorylink
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: nginx-ingress
```

### Environment Security

```bash
# Required secrets
MEMORYLINK_ENCRYPTION_KEY=<32-byte-key>  # Data encryption
MEMORYLINK_API_KEY=<api-key>             # API authentication (if enabled)
```

## 🧪 Testing

### Automated Testing

```bash
# Complete test suite
make test

# Docker-specific tests
make docker-test

# Manual test execution
./scripts/test.sh
```

### Test Coverage

- **Image build validation**
- **Container startup and health**
- **API endpoint functionality**
- **Data persistence verification**
- **Resource constraint testing**
- **Security configuration validation**

### Load Testing

```bash
# Basic load test with curl
for i in {1..100}; do
  curl -X POST http://localhost:8080/api/v1/memory \
    -H "Content-Type: application/json" \
    -d '{"text":"Load test message '$i'","tags":["loadtest"]}' &
done
```

## 📈 Performance Tuning

### Resource Configuration

```yaml
# Development
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "1Gi"
    cpu: "500m"

# Production  
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Environment Variables

```bash
# Performance tuning
MEMORYLINK_WORKERS=4                    # Uvicorn workers
MEMORYLINK_MAX_MEMORY_SIZE=100000      # Memory cache size
MEMORYLINK_EMBEDDING_BATCH_SIZE=128    # Batch processing
```

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check container logs
docker logs memorylink-dev

# Check health status  
docker inspect memorylink-dev | jq '.[0].State.Health'

# Debug with shell access
docker run -it --entrypoint /bin/bash memorylink:latest
```

#### API Not Accessible

```bash
# Verify port mapping
docker port memorylink-dev

# Check service binding
curl -v http://localhost:8080/api/v1/health

# Network connectivity
docker network ls
docker network inspect memorylink-dev-network
```

#### Data Not Persisting

```bash
# Check volume mounts
docker inspect memorylink-dev | jq '.[0].Mounts'

# Verify volume exists
docker volume ls | grep memorylink

# Check permissions
docker exec memorylink-dev ls -la /data
```

#### Performance Issues

```bash
# Monitor resource usage
docker stats memorylink-dev

# Check logs for errors
make logs | grep ERROR

# Memory usage analysis
docker exec memorylink-dev python -c "import psutil; print(f'Memory: {psutil.virtual_memory()}')"
```

### Debug Commands

```bash
# Container inspection
make status          # Service status
make logs           # View logs
make shell          # Container shell
make metrics        # Resource metrics

# Health verification
make health         # API health check
curl -f http://localhost:8080/api/v1/health

# Database access
make db-shell       # SQLite shell
docker exec memorylink-dev ls -la /data/vector/
```

## 🚀 Production Deployment Checklist

### Pre-deployment

- [ ] Environment variables configured
- [ ] Secrets properly set
- [ ] Resource limits defined
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] SSL/TLS certificates ready
- [ ] DNS records configured

### Deployment

- [ ] Build production image
- [ ] Run security scan
- [ ] Deploy to staging first
- [ ] Validate functionality
- [ ] Deploy to production
- [ ] Verify health checks
- [ ] Test key functionality
- [ ] Monitor performance

### Post-deployment

- [ ] Set up log monitoring
- [ ] Configure alerts
- [ ] Schedule backups
- [ ] Document rollback procedure
- [ ] Performance baseline
- [ ] Security review

## 📚 Additional Resources

### Makefile Commands

```bash
make help           # Show all available commands
make dev            # Complete development setup
make prod           # Complete production setup  
make ci             # Run CI pipeline locally
make clean          # Clean up resources
make security-scan  # Security analysis
```

### Environment Files

- `config/.env.example` - Environment template
- `.env` - Local environment (gitignored)
- `docker-compose.prod.yml` - Production overrides

### Scripts

- `scripts/build.sh` - Docker build automation
- `scripts/deploy.sh` - Deployment automation  
- `scripts/test.sh` - Testing automation
- `docker/entrypoint.sh` - Container initialization

## 🤝 Support

For deployment issues:

1. Check the troubleshooting section
2. Review container logs
3. Verify environment configuration
4. Test with minimal configuration
5. Create an issue with full logs and configuration

---

**Production Ready**: This deployment configuration is designed for production use with security, monitoring, and operational best practices.