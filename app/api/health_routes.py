"""Health check routes."""

from datetime import datetime
from fastapi import APIRouter, Depends
from ..config import get_settings
from ..models.memory_models import ErrorResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Health Check")
async def health_check():
    """Basic health check endpoint."""
    settings = get_settings()
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.debug else "production"
    }


@router.get("/detailed", summary="Detailed Health Check")
async def detailed_health_check():
    """Detailed health check with service dependencies."""
    settings = get_settings()
    
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": {"status": "healthy"},
            "config": {"status": "healthy"},
            "encryption": {"status": "healthy"}
        }
    }
    
    # Test embedding service
    try:
        from ..services import EmbeddingService
        embedding_service = EmbeddingService()
        health_status["components"]["embedding_service"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["embedding_service"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Test vector store
    try:
        from ..services import VectorStore
        vector_store = VectorStore()
        await vector_store.initialize()
        stats = await vector_store.get_collection_stats()
        health_status["components"]["vector_store"] = {
            "status": "healthy",
            "stats": stats
        }
    except Exception as e:
        health_status["components"]["vector_store"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status