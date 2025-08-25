# MemoryLink Development Makefile
# Provides convenient commands for development and deployment

.PHONY: help build start stop restart logs test clean setup lint format docker-test deploy backup

# Default target
help: ## Show this help message
	@echo "MemoryLink Development Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
setup: ## Set up development environment
	@echo "🚀 Setting up MemoryLink development environment..."
	cp config/.env.example .env
	mkdir -p data/{vector,metadata,logs,backups}
	chmod +x scripts/*.sh docker/entrypoint.sh
	@echo "✅ Setup completed. Edit .env file as needed."

# Docker operations
build: ## Build Docker image
	@echo "🔨 Building MemoryLink Docker image..."
	./scripts/build.sh

build-dev: ## Build development Docker image
	@echo "🔨 Building development Docker image..."
	./scripts/build.sh --env development --tag dev

build-prod: ## Build production Docker image
	@echo "🔨 Building production Docker image..."
	./scripts/build.sh --env production --tag latest

# Local development
start: ## Start MemoryLink development server
	@echo "🚀 Starting MemoryLink..."
	docker-compose up -d
	@echo "✅ MemoryLink is running at http://localhost:8080"
	@echo "📚 API docs available at http://localhost:8080/docs"

start-prod: ## Start MemoryLink in production mode
	@echo "🚀 Starting MemoryLink (Production)..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ MemoryLink production is running"

stop: ## Stop MemoryLink
	@echo "🛑 Stopping MemoryLink..."
	docker-compose down

stop-prod: ## Stop MemoryLink production
	@echo "🛑 Stopping MemoryLink production..."
	docker-compose -f docker-compose.prod.yml down

restart: ## Restart MemoryLink
	@echo "🔄 Restarting MemoryLink..."
	$(MAKE) stop
	sleep 2
	$(MAKE) start

restart-prod: ## Restart MemoryLink production
	@echo "🔄 Restarting MemoryLink production..."
	$(MAKE) stop-prod
	sleep 2
	$(MAKE) start-prod

# Monitoring and logs
logs: ## Show application logs
	docker-compose logs -f

logs-prod: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

status: ## Show service status
	docker-compose ps

status-prod: ## Show production status
	docker-compose -f docker-compose.prod.yml ps

health: ## Check application health
	@echo "🏥 Checking MemoryLink health..."
	@curl -s http://localhost:8080/api/v1/health | jq '.' || echo "Health check failed"

# Testing
test: ## Run test suite
	@echo "🧪 Running MemoryLink tests..."
	./scripts/test.sh

docker-test: ## Run comprehensive Docker tests
	@echo "🧪 Running Docker integration tests..."
	./scripts/test.sh

# Code quality
lint: ## Run code linting
	@echo "🔍 Running linter..."
	@if [ -d "app" ]; then \
		docker run --rm -v $(PWD):/app -w /app python:3.11-slim bash -c "pip install flake8 black mypy && flake8 app/ && mypy app/"; \
	else \
		echo "No app directory found"; \
	fi

format: ## Format code
	@echo "🎨 Formatting code..."
	@if [ -d "app" ]; then \
		docker run --rm -v $(PWD):/app -w /app python:3.11-slim bash -c "pip install black isort && black app/ && isort app/"; \
	else \
		echo "No app directory found"; \
	fi

# Deployment
deploy-dev: ## Deploy to development
	@echo "🚀 Deploying to development..."
	./scripts/deploy.sh -e development start

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	./scripts/deploy.sh -e production start

deploy-k8s-dev: ## Deploy to Kubernetes (development)
	@echo "🚀 Deploying to Kubernetes (development)..."
	kubectl apply -k k8s/overlays/development

deploy-k8s-prod: ## Deploy to Kubernetes (production)
	@echo "🚀 Deploying to Kubernetes (production)..."
	kubectl apply -k k8s/overlays/production

# Data management
backup: ## Create data backup
	@echo "💾 Creating backup..."
	./scripts/deploy.sh backup

restore: ## Restore from backup (requires BACKUP_PATH)
	@echo "📦 Restoring from backup..."
	@if [ -z "$(BACKUP_PATH)" ]; then \
		echo "Error: BACKUP_PATH not specified. Use: make restore BACKUP_PATH=/path/to/backup"; \
		exit 1; \
	fi
	./scripts/deploy.sh restore $(BACKUP_PATH)

# Maintenance
clean: ## Clean up containers and volumes
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

clean-all: ## Clean up everything including images
	@echo "🧹 Deep cleaning..."
	$(MAKE) clean
	docker image prune -a -f
	docker builder prune -a -f

reset: ## Reset development environment
	@echo "🔄 Resetting development environment..."
	$(MAKE) stop
	$(MAKE) clean
	rm -rf data/
	$(MAKE) setup
	$(MAKE) build-dev
	$(MAKE) start

# Scale operations (Kubernetes)
scale-up: ## Scale up to 3 replicas
	kubectl scale deployment/memorylink-deployment --replicas=3 -n memorylink

scale-down: ## Scale down to 1 replica
	kubectl scale deployment/memorylink-deployment --replicas=1 -n memorylink

# Security
security-scan: ## Run security scan on Docker image
	@echo "🔒 Running security scan..."
	@if command -v docker-scout >/dev/null 2>&1; then \
		docker scout cves memorylink:latest; \
	else \
		echo "Docker Scout not available. Install it for security scanning."; \
	fi

# Development utilities
shell: ## Open shell in running container
	docker-compose exec memorylink /bin/bash

shell-prod: ## Open shell in production container
	docker-compose -f docker-compose.prod.yml exec memorylink /bin/bash

db-shell: ## Open database shell
	docker-compose exec memorylink sqlite3 /data/metadata/memorylink.db

# Performance testing
perf-test: ## Run performance tests
	@echo "⚡ Running performance tests..."
	@echo "This will be implemented with load testing tools"

# Monitoring
metrics: ## Show system metrics
	@echo "📊 System metrics:"
	@docker stats --no-stream
	@echo ""
	@echo "🗄️  Volume usage:"
	@docker system df

# Quick commands for common workflows
dev: setup build-dev start ## Complete development setup
prod: build-prod start-prod ## Complete production setup
ci: lint test docker-test ## Run CI pipeline locally

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Documentation generation not implemented yet"