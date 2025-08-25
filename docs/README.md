# 📚 MemoryLink Documentation Hub

Welcome to the MemoryLink documentation! This guide provides comprehensive information for developers, users, and administrators working with the MemoryLink personal memory layer system.

## 🚀 Quick Start

- [User Guide](./USER_GUIDE.md) - Get started using MemoryLink
- [Developer Guide](./DEVELOPER_GUIDE.md) - Set up your development environment
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Deploy to production
- [API Documentation](./api.md) - RESTful API reference

## 📖 Core Documentation

### Architecture & Design
- [Executive Summary](./EXECUTIVE_SUMMARY.md) - High-level overview for stakeholders
- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md) - Complete technical reference
- [Architecture Specification](./architecture-specification.md) - Detailed system architecture
- [Architecture Summary](./architecture-summary.md) - Quick architecture overview
- [Component Interaction Diagram](./component-interaction-diagram.md) - Visual component relationships
- [Data Flow Diagrams](./data-flow-diagrams.md) - Data movement through the system

### Development
- [Developer Guide](./DEVELOPER_GUIDE.md) - Complete development setup and workflow
- [Development Setup](./development.md) - Quick development environment setup
- [Testing Guide](./TESTING.md) - Testing strategies and procedures
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
- [FAQ](./faq.md) - Frequently asked questions

### Deployment & Operations
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Deployment Configuration](./deployment.md) - Deployment options and settings
- [Deployment Validation Report](./DEPLOYMENT_VALIDATION_REPORT.md) - Production validation checklist
- [Production Readiness Certificate](./PRODUCTION_READINESS_CERTIFICATE.md) - Production certification

### IDE Integration
- [VSCode Integration Guide](./vscode-integration.md) - Set up MemoryLink with VSCode
- [Cursor Integration Guide](./cursor-integration.md) - Set up MemoryLink with Cursor
- [Custom Rules Guide](./custom-rules.md) - Create custom automation rules
- [Hooks & Automation](./hooks-automation.md) - Automate workflows with hooks

## 📋 Specifications

The `/specs` directory contains detailed technical specifications:

- [Specifications Overview](./specs/README.md) - Index of all specifications
- [MVP Specification](./specs/memorylink-mvp-specification.md) - Minimum viable product requirements
- [Data Models](./specs/data-models.md) - Database schema and data structures
- [Security Requirements](./specs/security-requirements.md) - Security and privacy specifications
- [Technical Constraints](./specs/technical-constraints.md) - System limitations and boundaries
- [Acceptance Criteria](./specs/acceptance-criteria.md) - Feature completion requirements
- [Gamification Requirements](./specs/gamification-requirements.md) - Engagement features

## 🔗 API Resources

- [API Reference](./api.md) - Complete REST API documentation
- [OpenAPI Specification](./specs/api-specification.yaml) - Machine-readable API spec
- [JavaScript Client Examples](../examples/javascript_client.js) - Sample JS/Node.js code
- [Python Client Examples](../examples/python_client.py) - Sample Python code

## 🛠️ Development Tools

### Claude Flow Integration
MemoryLink integrates with Claude Flow for AI-powered development:

```bash
# Initialize SPARC development
npx claude-flow sparc run spec-pseudocode "design memory feature"

# Run TDD workflow
npx claude-flow sparc tdd "implement vector search"

# Deploy with swarm coordination
npx claude-flow swarm init --topology mesh
```

### Docker Development
```bash
# Start development environment
docker-compose up -d

# Run with production config
docker-compose -f docker-compose.prod.yml up
```

### Kubernetes Deployment
```bash
# Deploy to development
kubectl apply -k k8s/overlays/development/

# Deploy to production
kubectl apply -k k8s/overlays/production/
```

## 📦 Project Structure

```
MemoryLink/
├── docs/              # This documentation
├── backend/           # FastAPI backend service
├── app/              # Application code
├── k8s/              # Kubernetes manifests
├── docker/           # Docker configurations
├── scripts/          # Utility scripts
├── tests/            # Test suites
└── examples/         # Client examples
```

## 🔍 Quick Reference

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `ENCRYPTION_KEY` - Fernet encryption key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis cache connection

### Default Ports
- API Server: `8000`
- PostgreSQL: `5432`
- Redis: `6379`
- pgAdmin: `5050`

### Health Checks
- Health: `GET /health`
- Metrics: `GET /metrics`
- Ready: `GET /ready`

## 🤝 Contributing

1. Read the [Developer Guide](./DEVELOPER_GUIDE.md)
2. Follow the [Testing Guide](./TESTING.md)
3. Check [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
4. Review [Architecture Specification](./architecture-specification.md)

## 📝 License

MemoryLink is proprietary software. See LICENSE file for details.

## 🆘 Support

- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [FAQ](./faq.md)
- [User Guide](./USER_GUIDE.md)
- GitHub Issues: [Report bugs and request features](https://github.com/tbowman01/MemoryLink/issues)

---

*Last updated: August 2025*