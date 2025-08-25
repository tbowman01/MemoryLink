"""API routes for MemoryLink backend."""

from .memory_routes import router as memory_router
from .health_routes import router as health_router

__all__ = ["memory_router", "health_router"]