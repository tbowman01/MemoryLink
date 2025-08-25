# MemoryLink Deployment Guide
*Production-Ready Deployment Procedures and Best Practices*

## 🎁 Deployment Overview

MemoryLink supports multiple deployment strategies from local development to enterprise Kubernetes clusters. This guide covers all deployment scenarios with security-hardened configurations and production best practices.

### Deployment Options

| Deployment Type | Use Case | Complexity | Scalability |
|----------------|----------|------------|-------------|
| **Local Development** | Development & testing | Low | Single user |
| **Docker Compose** | Small teams, demos | Medium | 1-10 users |
| **Kubernetes** | Production, enterprise | High | 10-10,000+ users |
| **Cloud Native** | Multi-region, HA | Very High | Unlimited |

## 💻 Local Development Deployment

### Quick Start (5 Minutes)

```bash
# Clone repository
git clone https://github.com/your-org/memorylink.git
cd memorylink

# Setup environment
make setup

# Configure encryption key
echo "ENCRYPTION_KEY=$(openssl rand -base64 32)" >> .env

# Start development server
make dev
```

**Access Points:**
- API: http://localhost:8080
- Docs: http://localhost:8080/docs
- Health: http://localhost:8080/health

### Development Environment Configuration

```bash
# .env file for development
API_HOST=127.0.0.1
API_PORT=8080
DEBUG=true
LOG_LEVEL=DEBUG

# Security (development only)
ENCRYPTION_KEY=your-32-character-key-here
API_KEY_REQUIRED=false

# Storage
DATA_PATH=./data
VECTOR_DB_PATH=./data/vector
METADATA_DB_PATH=./data/metadata/memorylink.db

# Performance
EMBEDDING_CACHE_SIZE=100
CONCURRENT_REQUESTS=5
```

### Development Commands

```bash
# Development lifecycle
make dev              # Complete development setup
make start            # Start services
make stop             # Stop services
make restart          # Restart services
make logs             # View logs
make shell            # Open container shell
make test             # Run test suite
make lint             # Code quality checks

# Data management
make backup           # Create backup
make reset            # Reset all data
make cleanup          # Clean containers/volumes
```

## 🐳 Docker Compose Production Deployment

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  memorylink:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: memorylink:latest
    container_name: memorylink-prod
    restart: unless-stopped
    
    ports:
      - "80:8080"      # HTTP
      - "443:8443"     # HTTPS (if SSL configured)
    
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8080
      - DEBUG=false
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
      - WORKERS=4
      
      # Security
      - API_KEY_REQUIRED=true
      - RATE_LIMIT_ENABLED=true
      - RATE_LIMIT_PER_MINUTE=60
      - CORS_ORIGINS=["https://yourdomain.com"]
      
      # SSL (optional)
      - SSL_ENABLED=false
      - SSL_CERT_PATH=/certs/cert.pem
      - SSL_KEY_PATH=/certs/key.pem
    
    env_file:
      - .env.prod
    
    volumes:
      # Data persistence
      - memorylink_data:/data
      - memorylink_logs:/data/logs
      
      # SSL certificates (if using HTTPS)
      - ./certs:/certs:ro
      
      # Configuration
      - ./config/prod:/app/config:ro
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    
    # Security
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:size=100M,noexec,nosuid,nodev
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.25'
    
    # Logging
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  memorylink_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/memorylink/data
  
  memorylink_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/memorylink/logs

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Production Environment Setup

```bash
#!/bin/bash
# setup-production.sh - Production environment setup script

set -e

# Configuration
APP_USER="memorylink"
APP_HOME="/opt/memorylink"
DATA_DIR="${APP_HOME}/data"
LOGS_DIR="${APP_HOME}/logs"
BACKUP_DIR="${APP_HOME}/backups"

# Create system user
sudo useradd --system --shell /bin/false --home ${APP_HOME} --create-home ${APP_USER}

# Create directories
sudo mkdir -p ${DATA_DIR}/{vector,metadata,cache} ${LOGS_DIR} ${BACKUP_DIR}
sudo chown -R ${APP_USER}:${APP_USER} ${APP_HOME}
sudo chmod 750 ${APP_HOME}
sudo chmod 700 ${DATA_DIR}/metadata  # Sensitive data

# Generate production secrets
echo "Generating production secrets..."
ENCRYPTION_KEY=$(openssl rand -base64 32)
API_KEY=$(openssl rand -base64 24)
JWT_SECRET=$(openssl rand -base64 32)

# Create production environment file
sudo tee ${APP_HOME}/.env.prod > /dev/null <<EOF
# MemoryLink Production Configuration
# Generated: $(date)

# Security
ENCRYPTION_KEY=${ENCRYPTION_KEY}
API_KEY=${API_KEY}
JWT_SECRET=${JWT_SECRET}
API_KEYS=["${API_KEY}"]

# SSL/TLS
SSL_ENABLED=false
HTTPS_REDIRECT=true

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
EOF

# Set secure permissions
sudo chown ${APP_USER}:${APP_USER} ${APP_HOME}/.env.prod
sudo chmod 600 ${APP_HOME}/.env.prod

echo "Production environment setup complete!"
echo "Next steps:"
echo "1. Review and adjust .env.prod configuration"
echo "2. Set up SSL certificates if needed"
echo "3. Configure monitoring and alerting"
echo "4. Run: make prod"
```

### Production Deployment Commands

```bash
# Production deployment
make build-prod       # Build production image
make start-prod       # Start production services
make deploy-prod      # Complete production deployment

# Monitoring
make status-prod      # Check service status
make logs-prod        # View production logs
make health-prod      # Health check
make metrics-prod     # System metrics

# Maintenance
make backup-prod      # Create backup
make update-prod      # Update deployment
make rollback-prod    # Rollback deployment
```

### SSL/TLS Configuration

```bash
# Generate self-signed certificate (development/testing)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Or use Let's Encrypt (production)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to MemoryLink
sudo mkdir -p /opt/memorylink/certs
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/memorylink/certs/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/memorylink/certs/key.pem
sudo chown -R memorylink:memorylink /opt/memorylink/certs
sudo chmod 600 /opt/memorylink/certs/*.pem
```

## ☸️ Kubernetes Production Deployment

### Prerequisites

```bash
# Required tools
kubectl version --client
helm version
kustomize version

# Cluster requirements
# - Kubernetes 1.24+
# - 4GB+ RAM per node
# - Persistent volume support
# - Ingress controller
# - Certificate manager (optional)
```

### Namespace and RBAC Setup

```yaml
# k8s/base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: memorylink
  labels:
    name: memorylink
    app.kubernetes.io/name: memorylink
    app.kubernetes.io/instance: production

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: memorylink-sa
  namespace: memorylink
automountServiceAccountToken: false

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: memorylink-role
  namespace: memorylink
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: memorylink-rolebinding
  namespace: memorylink
subjects:
- kind: ServiceAccount
  name: memorylink-sa
  namespace: memorylink
roleRef:
  kind: Role
  name: memorylink-role
  apiGroup: rbac.authorization.k8s.io
```

### ConfigMap and Secrets

```yaml
# k8s/base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: memorylink-config
  namespace: memorylink
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8080"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  
  # Performance
  WORKERS: "4"
  MAX_REQUESTS: "1000"
  CONCURRENT_REQUESTS: "20"
  
  # Features
  METRICS_ENABLED: "true"
  HEALTH_CHECK_INTERVAL: "30"
  
  # Storage
  DATA_PATH: "/data"
  VECTOR_DB_PATH: "/data/vector"
  METADATA_DB_PATH: "/data/metadata/memorylink.db"
  
  # Cache
  EMBEDDING_CACHE_SIZE: "1000"
  EMBEDDING_CACHE_TTL: "3600"
  SEARCH_CACHE_SIZE: "2000"
  SEARCH_CACHE_TTL: "600"

---
apiVersion: v1
kind: Secret
metadata:
  name: memorylink-secrets
  namespace: memorylink
type: Opaque
stringData:
  ENCRYPTION_KEY: "your-base64-encryption-key-32-chars"
  API_KEYS: '["your-api-key-here", "backup-api-key"]'
  JWT_SECRET: "your-jwt-secret-key"
```

### Persistent Storage

```yaml
# k8s/base/persistentvolume.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: memorylink-pv
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  hostPath:
    path: /opt/memorylink/data
    type: DirectoryOrCreate

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: memorylink-pvc
  namespace: memorylink
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd
```

### Deployment Configuration

```yaml
# k8s/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memorylink-deployment
  namespace: memorylink
  labels:
    app: memorylink
    component: api
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memorylink
      component: api
  template:
    metadata:
      labels:
        app: memorylink
        component: api
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: memorylink-sa
      automountServiceAccountToken: false
      
      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      
      containers:
      - name: memorylink
        image: memorylink:latest
        imagePullPolicy: Always
        
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        
        # Environment configuration
        envFrom:
        - configMapRef:
            name: memorylink-config
        - secretRef:
            name: memorylink-secrets
        
        # Resource management
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        
        # Volume mounts
        volumeMounts:
        - name: data-volume
          mountPath: /data
        - name: tmp-volume
          mountPath: /tmp
        - name: cache-volume
          mountPath: /cache
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /health
            port: http
            scheme: HTTP
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
          successThreshold: 1
        
        readinessProbe:
          httpGet:
            path: /health
            port: http
            scheme: HTTP
          initialDelaySeconds: 15
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 2
          successThreshold: 1
        
        startupProbe:
          httpGet:
            path: /health
            port: http
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 12  # 120 seconds total
          successThreshold: 1
        
        # Security context
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
            add:
            - NET_BIND_SERVICE  # If binding to port < 1024
        
        # Lifecycle hooks
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: memorylink-pvc
      - name: tmp-volume
        emptyDir:
          sizeLimit: "1Gi"
      - name: cache-volume
        emptyDir:
          sizeLimit: "500Mi"
      
      # Pod management
      restartPolicy: Always
      terminationGracePeriodSeconds: 30
      
      # Node selection
      nodeSelector:
        kubernetes.io/arch: amd64
      
      # Anti-affinity for high availability
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values: ["memorylink"]
              topologyKey: kubernetes.io/hostname
```

### Service and Ingress

```yaml
# k8s/base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: memorylink-service
  namespace: memorylink
  labels:
    app: memorylink
    component: api
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  selector:
    app: memorylink
    component: api

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: memorylink-ingress
  namespace: memorylink
  annotations:
    # NGINX Ingress Controller
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    
    # Rate limiting
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    
    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization"
    
    # SSL Certificate
    cert-manager.io/cluster-issuer: letsencrypt-prod
    
    # Security headers
    nginx.ingress.kubernetes.io/server-snippet: |
      add_header X-Frame-Options DENY;
      add_header X-Content-Type-Options nosniff;
      add_header X-XSS-Protection "1; mode=block";
      add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
spec:
  tls:
  - hosts:
    - api.memorylink.yourdomain.com
    secretName: memorylink-tls
  rules:
  - host: api.memorylink.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: memorylink-service
            port:
              number: 80
```

### Kustomization for Environment Management

```yaml
# k8s/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - namespace.yaml
  - configmap.yaml
  - secret.yaml
  - persistentvolume.yaml
  - deployment.yaml
  - service.yaml
  - ingress.yaml

commonLabels:
  app.kubernetes.io/name: memorylink
  app.kubernetes.io/part-of: memorylink
  app.kubernetes.io/managed-by: kustomize

namePrefix: ""
nameSuffix: ""

images:
  - name: memorylink
    newTag: latest
```

```yaml
# k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base
  - hpa.yaml
  - pod-disruption-budget.yaml
  - network-policy.yaml
  - monitoring.yaml

patchesStrategicMerge:
  - deployment-patch.yaml
  - configmap-patch.yaml

nameSuffix: "-prod"

commonLabels:
  environment: production

images:
  - name: memorylink
    newTag: v1.0.0

replicas:
  - name: memorylink-deployment
    count: 5
```

### Deployment Commands

```bash
# Deploy to Kubernetes
kubectl apply -k k8s/base                    # Base deployment
kubectl apply -k k8s/overlays/development    # Development
kubectl apply -k k8s/overlays/production     # Production

# Or use Make targets
make deploy-k8s-dev      # Deploy to development
make deploy-k8s-prod     # Deploy to production

# Check deployment status
kubectl get pods -n memorylink
kubectl get services -n memorylink
kubectl get ingress -n memorylink

# Monitor deployment
kubectl logs -f deployment/memorylink-deployment -n memorylink
kubectl describe deployment memorylink-deployment -n memorylink
```

## 🌐 Cloud-Native Deployment

### AWS EKS Deployment

```bash
#!/bin/bash
# deploy-aws-eks.sh - Deploy MemoryLink to AWS EKS

set -e

# Configuration
CLUSTER_NAME="memorylink-prod"
REGION="us-west-2"
NODE_INSTANCE_TYPE="t3.medium"
NODE_COUNT="3"

# Create EKS cluster
eksctl create cluster \
  --name ${CLUSTER_NAME} \
  --region ${REGION} \
  --node-type ${NODE_INSTANCE_TYPE} \
  --nodes ${NODE_COUNT} \
  --nodes-min 2 \
  --nodes-max 6 \
  --managed \
  --enable-ssm

# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/aws/deploy.yaml

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create EBS storage class
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
EOF

# Deploy MemoryLink
kubectl apply -k k8s/overlays/production

echo "MemoryLink deployed to AWS EKS cluster: ${CLUSTER_NAME}"
echo "Wait for Load Balancer to be ready, then configure DNS"
```

### Google GKE Deployment

```bash
#!/bin/bash
# deploy-gke.sh - Deploy MemoryLink to Google GKE

set -e

# Configuration
PROJECT_ID="your-project-id"
CLUSTER_NAME="memorylink-prod"
ZONE="us-central1-a"
NODE_COUNT="3"

# Create GKE cluster
gcloud container clusters create ${CLUSTER_NAME} \
  --project=${PROJECT_ID} \
  --zone=${ZONE} \
  --machine-type=e2-standard-2 \
  --num-nodes=${NODE_COUNT} \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=6

# Get credentials
gcloud container clusters get-credentials ${CLUSTER_NAME} \
  --zone=${ZONE} \
  --project=${PROJECT_ID}

# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Deploy MemoryLink
kubectl apply -k k8s/overlays/production

echo "MemoryLink deployed to GKE cluster: ${CLUSTER_NAME}"
```

## 📊 Monitoring and Observability

### Prometheus Monitoring

```yaml
# k8s/overlays/production/monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: memorylink-metrics
  namespace: memorylink
  labels:
    app: memorylink
spec:
  selector:
    matchLabels:
      app: memorylink
      component: api
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s

---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: memorylink-alerts
  namespace: memorylink
spec:
  groups:
  - name: memorylink
    rules:
    - alert: MemoryLinkDown
      expr: up{job="memorylink"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "MemoryLink service is down"
        description: "MemoryLink has been down for more than 5 minutes"
    
    - alert: MemoryLinkHighErrorRate
      expr: rate(memorylink_memory_operations_total{status="error"}[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High error rate in MemoryLink"
        description: "Error rate is {{ $value }} errors per second"
    
    - alert: MemoryLinkSlowResponse
      expr: histogram_quantile(0.95, rate(memorylink_search_duration_seconds_bucket[5m])) > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "MemoryLink search is slow"
        description: "95th percentile search time is {{ $value }}s"
    
    - alert: MemoryLinkHighMemoryUsage
      expr: container_memory_usage_bytes{pod=~"memorylink-.*"} / container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage in MemoryLink"
        description: "Memory usage is {{ $value | humanizePercentage }}"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "MemoryLink Operations Dashboard",
    "tags": ["memorylink", "production"],
    "panels": [
      {
        "title": "Memory Operations Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(memorylink_memory_operations_total[5m])",
            "legendFormat": "{{ operation }}"
          }
        ]
      },
      {
        "title": "Search Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(memorylink_search_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(memorylink_search_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Memories",
        "type": "singlestat",
        "targets": [
          {
            "expr": "memorylink_active_memories_total"
          }
        ]
      },
      {
        "title": "Storage Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "memorylink_storage_usage_bytes",
            "legendFormat": "{{ storage_type }}"
          }
        ]
      }
    ]
  }
}
```

## 🔒 Security Hardening

### Security Checklist

#### Container Security
- ✅ Non-root user execution (UID 1000)
- ✅ Read-only root filesystem
- ✅ Dropped capabilities (ALL)
- ✅ Security contexts configured
- ✅ No privileged escalation
- ✅ Secure base image (distroless or alpine)
- ✅ Multi-stage builds for minimal attack surface

#### Network Security
- ✅ Network policies for pod isolation
- ✅ TLS termination at ingress
- ✅ Rate limiting configured
- ✅ CORS policies set
- ✅ Security headers enabled
- ✅ Internal service mesh encryption (optional)

#### Data Security
- ✅ Encryption at rest (application level)
- ✅ Secrets management (Kubernetes secrets)
- ✅ Key rotation procedures
- ✅ Backup encryption
- ✅ Access logging and auditing

#### Authentication & Authorization
- ✅ API key authentication
- ✅ RBAC for Kubernetes resources
- ✅ Service account restrictions
- ✅ JWT token validation (if applicable)
- ✅ Request validation and sanitization

### Security Scanning

```bash
#!/bin/bash
# security-scan.sh - Comprehensive security scanning

set -e

echo "Running MemoryLink security scans..."

# Container image vulnerability scan
if command -v docker-scout >/dev/null 2>&1; then
    echo "Scanning container image for vulnerabilities..."
    docker scout cves memorylink:latest
fi

# Kubernetes security scan with kubesec
if command -v kubesec >/dev/null 2>&1; then
    echo "Scanning Kubernetes manifests..."
    kubesec scan k8s/base/deployment.yaml
fi

# Network policy validation
if command -v opa >/dev/null 2>&1; then
    echo "Validating network policies..."
    opa test security/policies/
fi

# OWASP ZAP security scan (if available)
if [ -n "${ZAP_PROXY}" ]; then
    echo "Running OWASP ZAP security scan..."
    docker run -t owasp/zap2docker-stable zap-baseline.py \
        -t http://api.memorylink.yourdomain.com
fi

echo "Security scan completed"
```

## 🔄 Backup and Recovery

### Automated Backup Strategy

```bash
#!/bin/bash
# backup-kubernetes.sh - Kubernetes backup strategy

set -e

# Configuration
NAMESPACE="memorylink"
BACKUP_BUCKET="s3://memorylink-backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p "/tmp/backup_${TIMESTAMP}"

# Backup Kubernetes resources
echo "Backing up Kubernetes resources..."
kubectl get all,pv,pvc,configmaps,secrets -n ${NAMESPACE} -o yaml > "/tmp/backup_${TIMESTAMP}/kubernetes_resources.yaml"

# Backup persistent data
echo "Backing up persistent data..."
kubectl exec -n ${NAMESPACE} deployment/memorylink-deployment -- tar czf - /data > "/tmp/backup_${TIMESTAMP}/data.tar.gz"

# Upload to cloud storage
echo "Uploading to cloud storage..."
aws s3 cp "/tmp/backup_${TIMESTAMP}" "${BACKUP_BUCKET}/backup_${TIMESTAMP}" --recursive

# Cleanup old backups
echo "Cleaning up old backups..."
aws s3 ls "${BACKUP_BUCKET}/" | grep "backup_" | while read -r line; do
    backup_date=$(echo $line | awk '{print $2}' | cut -d'_' -f2)
    if [ $(( $(date +%s) - $(date -d "$backup_date" +%s) )) -gt $(( $RETENTION_DAYS * 24 * 3600 )) ]; then
        backup_name=$(echo $line | awk '{print $4}')
        aws s3 rm "${BACKUP_BUCKET}/${backup_name}" --recursive
        echo "Deleted old backup: ${backup_name}"
    fi
done

# Cleanup local backup
rm -rf "/tmp/backup_${TIMESTAMP}"

echo "Backup completed: backup_${TIMESTAMP}"
```

### Disaster Recovery Procedure

```bash
#!/bin/bash
# disaster-recovery.sh - Complete disaster recovery procedure

set -e

BACKUP_NAME="$1"
if [ -z "$BACKUP_NAME" ]; then
    echo "Usage: $0 <backup_name>"
    echo "Available backups:"
    aws s3 ls s3://memorylink-backups/ | grep backup_
    exit 1
fi

echo "Starting disaster recovery from backup: $BACKUP_NAME"

# Download backup
echo "Downloading backup..."
aws s3 cp "s3://memorylink-backups/$BACKUP_NAME" "/tmp/$BACKUP_NAME" --recursive

# Stop current deployment
echo "Stopping current deployment..."
kubectl scale deployment memorylink-deployment --replicas=0 -n memorylink

# Restore Kubernetes resources
echo "Restoring Kubernetes resources..."
kubectl apply -f "/tmp/$BACKUP_NAME/kubernetes_resources.yaml"

# Restore data
echo "Restoring data..."
kubectl exec -n memorylink deployment/memorylink-deployment -- rm -rf /data/*
kubectl exec -n memorylink deployment/memorylink-deployment -- tar xzf - -C / < "/tmp/$BACKUP_NAME/data.tar.gz"

# Restart deployment
echo "Restarting deployment..."
kubectl scale deployment memorylink-deployment --replicas=3 -n memorylink

# Wait for deployment to be ready
kubectl rollout status deployment/memorylink-deployment -n memorylink

# Verify recovery
echo "Verifying recovery..."
sleep 30
kubectl exec -n memorylink deployment/memorylink-deployment -- curl -f http://localhost:8080/health

echo "Disaster recovery completed successfully"

# Cleanup
rm -rf "/tmp/$BACKUP_NAME"
```

## 📦 Update and Rollback Procedures

### Rolling Update Strategy

```bash
#!/bin/bash
# rolling-update.sh - Safe rolling update procedure

set -e

NEW_VERSION="$1"
if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <new_version>"
    exit 1
fi

echo "Performing rolling update to version: $NEW_VERSION"

# Pre-update backup
echo "Creating pre-update backup..."
./backup-kubernetes.sh

# Update image version
echo "Updating image version..."
kubectl set image deployment/memorylink-deployment \
    memorylink=memorylink:$NEW_VERSION \
    -n memorylink

# Monitor rollout
echo "Monitoring rollout..."
kubectl rollout status deployment/memorylink-deployment \
    -n memorylink \
    --timeout=600s

# Health check
echo "Performing health check..."
sleep 30
for i in {1..5}; do
    if kubectl exec -n memorylink deployment/memorylink-deployment -- \
        curl -f http://localhost:8080/health >/dev/null 2>&1; then
        echo "Health check passed ($i/5)"
        break
    else
        echo "Health check failed ($i/5), retrying..."
        sleep 10
    fi
done

# Verify update
echo "Verifying update..."
ACTUAL_VERSION=$(kubectl get deployment memorylink-deployment \
    -n memorylink \
    -o jsonpath='{.spec.template.spec.containers[0].image}' | \
    cut -d':' -f2)

if [ "$ACTUAL_VERSION" = "$NEW_VERSION" ]; then
    echo "Update successful: $NEW_VERSION"
else
    echo "Update failed: expected $NEW_VERSION, got $ACTUAL_VERSION"
    exit 1
fi

echo "Rolling update completed successfully"
```

### Rollback Procedure

```bash
#!/bin/bash
# rollback.sh - Quick rollback procedure

set -e

echo "Initiating rollback..."

# Show rollout history
echo "Rollout history:"
kubectl rollout history deployment/memorylink-deployment -n memorylink

# Rollback to previous version
echo "Rolling back to previous version..."
kubectl rollout undo deployment/memorylink-deployment -n memorylink

# Monitor rollback
echo "Monitoring rollback..."
kubectl rollout status deployment/memorylink-deployment \
    -n memorylink \
    --timeout=300s

# Verify rollback
echo "Verifying rollback..."
sleep 15
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    curl -f http://localhost:8080/health

echo "Rollback completed successfully"
```

## 📊 Performance Tuning

### Resource Optimization

```yaml
# Performance-tuned deployment configuration
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: memorylink
        resources:
          requests:
            memory: "1Gi"    # Increased for better performance
            cpu: "500m"      # Higher baseline for consistent performance
          limits:
            memory: "4Gi"    # Allow bursting for large operations
            cpu: "2000m"     # Higher limit for peak loads
        
        env:
        # Performance tuning
        - name: WORKERS
          value: "8"         # More workers for concurrency
        - name: MAX_REQUESTS
          value: "2000"      # Higher request limit
        - name: CONCURRENT_REQUESTS
          value: "50"        # More concurrent processing
        
        # Cache optimization
        - name: EMBEDDING_CACHE_SIZE
          value: "2000"      # Larger embedding cache
        - name: EMBEDDING_CACHE_TTL
          value: "7200"      # 2 hours
        - name: SEARCH_CACHE_SIZE
          value: "5000"      # Larger search cache
        - name: SEARCH_CACHE_TTL
          value: "1800"      # 30 minutes
```

### Database Optimization

```sql
-- SQLite optimization for metadata database
PRAGMA journal_mode = WAL;          -- Write-Ahead Logging
PRAGMA synchronous = NORMAL;        -- Good balance of safety/performance
PRAGMA cache_size = 10000;         -- 10MB cache
PRAGMA temp_store = memory;         -- Use memory for temp storage
PRAGMA mmap_size = 268435456;       -- 256MB memory mapped

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories(tags);
CREATE INDEX IF NOT EXISTS idx_memories_content_hash ON memories(content_hash);
```

## 📎 Troubleshooting Guide

### Common Deployment Issues

#### Pod Fails to Start

```bash
# Check pod status
kubectl get pods -n memorylink
kubectl describe pod <pod-name> -n memorylink

# Check logs
kubectl logs <pod-name> -n memorylink

# Common solutions:
# 1. Resource constraints
kubectl describe nodes

# 2. Image pull issues
kubectl get events -n memorylink --sort-by='.lastTimestamp'

# 3. Configuration errors
kubectl get configmap memorylink-config -n memorylink -o yaml
kubectl get secret memorylink-secrets -n memorylink -o yaml
```

#### Service Not Accessible

```bash
# Check service configuration
kubectl get svc memorylink-service -n memorylink -o yaml

# Check endpoints
kubectl get endpoints -n memorylink

# Test internal connectivity
kubectl run test-pod --image=curlimages/curl -it --rm -- sh
# Inside pod:
curl http://memorylink-service.memorylink.svc.cluster.local/health

# Check ingress
kubectl get ingress -n memorylink
kubectl describe ingress memorylink-ingress -n memorylink
```

#### High Memory Usage

```bash
# Monitor resource usage
kubectl top pods -n memorylink
kubectl top nodes

# Check for memory leaks
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    cat /proc/meminfo

# Review cache configuration
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    curl -s http://localhost:8080/metrics | grep cache
```

### Performance Issues

```bash
# Check response times
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8080/health

# Monitor database performance
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    sqlite3 /data/metadata/memorylink.db ".timer on" "SELECT COUNT(*) FROM memories;"

# Check vector database performance
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    ls -la /data/vector/

# Review embedding cache hit rates
kubectl exec -n memorylink deployment/memorylink-deployment -- \
    curl -s http://localhost:8080/metrics | grep embedding_cache
```

## 📊 Cost Optimization

### Resource Right-Sizing

```yaml
# Cost-optimized configuration for development/testing
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 1  # Single replica for development
  template:
    spec:
      containers:
      - name: memorylink
        resources:
          requests:
            memory: "256Mi"  # Minimal memory for development
            cpu: "100m"      # Low CPU request
          limits:
            memory: "1Gi"    # Reasonable limit
            cpu: "500m"      # Conservative limit
        
        env:
        - name: WORKERS
          value: "2"         # Fewer workers
        - name: EMBEDDING_CACHE_SIZE
          value: "500"       # Smaller cache
        - name: SEARCH_CACHE_SIZE
          value: "1000"      # Smaller cache
```

### Auto-Scaling Configuration

```yaml
# k8s/overlays/production/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: memorylink-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: memorylink-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 600  # Longer stabilization for scale down
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

---

## 🏁 Deployment Success Checklist

### Pre-Deployment
- ☐ Environment configuration reviewed
- ☐ Secrets and encryption keys generated
- ☐ SSL certificates obtained (if applicable)
- ☐ DNS configuration prepared
- ☐ Monitoring and alerting configured
- ☐ Backup strategy implemented

### Deployment
- ☐ Infrastructure provisioned
- ☐ Application deployed successfully
- ☐ Health checks passing
- ☐ Security scans completed
- ☐ Performance tests executed
- ☐ Load testing completed

### Post-Deployment
- ☐ Monitoring dashboards configured
- ☐ Alerting rules active
- ☐ Backup verification completed
- ☐ Documentation updated
- ☐ Team training completed
- ☐ Support procedures documented

---

*This deployment guide provides comprehensive procedures for deploying MemoryLink across all environments. Follow the appropriate section based on your deployment target and requirements.*

**Ready for production deployment?**

```bash
make deploy-prod
```