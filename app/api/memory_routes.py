"""Memory API routes."""

import time
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ..models.memory_models import (
    AddMemoryRequest,
    AddMemoryResponse,
    SearchMemoryRequest,
    SearchMemoryResponse,
    MemorySearchResult,
    ErrorResponse
)
from ..services import MemoryService
from ..utils.logger import get_logger
from ..config import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/memory", tags=["Memory"])

# Dependency for memory service
async def get_memory_service() -> MemoryService:
    """Get initialized memory service."""
    service = MemoryService()
    await service.initialize()
    return service


@router.post("/add", response_model=AddMemoryResponse, summary="Add Memory")
async def add_memory(
    request: AddMemoryRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Add a new memory to the system."""
    try:
        start_time = time.time()
        
        # Add the memory
        memory_entry = await memory_service.add_memory(request)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = AddMemoryResponse(
            id=memory_entry.id,
            message="Memory added successfully",
            timestamp=memory_entry.timestamp
        )
        
        logger.info(f"Added memory {memory_entry.id} in {processing_time:.2f}ms")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error adding memory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Unexpected error adding memory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while adding memory"
        )


@router.post("/search", response_model=SearchMemoryResponse, summary="Search Memories")
async def search_memories(
    request: SearchMemoryRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Search for memories using semantic similarity."""
    try:
        start_time = time.time()
        
        # Perform the search
        results = await memory_service.search_memories(request)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = SearchMemoryResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            execution_time_ms=round(processing_time, 2)
        )
        
        logger.info(f"Search completed in {processing_time:.2f}ms, found {len(results)} results")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error in search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during search"
        )


@router.get("/user/{user_id}/count", summary="Get User Memory Count")
async def get_user_memory_count(
    user_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get the count of memories for a specific user."""
    try:
        count = await memory_service.get_user_memories_count(user_id)
        
        return {
            "user_id": user_id,
            "memory_count": count
        }
    
    except Exception as e:
        logger.error(f"Error getting memory count for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving memory count"
        )


@router.get("/{memory_id}", summary="Get Memory by ID")
async def get_memory(
    memory_id: str,
    user_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get a specific memory by its ID."""
    try:
        memory = await memory_service.get_memory(memory_id, user_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found or access denied"
            )
        
        return memory
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting memory {memory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving memory"
        )


@router.delete("/{memory_id}", summary="Delete Memory")
async def delete_memory(
    memory_id: str,
    user_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Delete a memory by its ID."""
    try:
        success = await memory_service.delete_memory(memory_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found or access denied"
            )
        
        return {
            "message": "Memory deleted successfully",
            "memory_id": memory_id
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error deleting memory {memory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting memory"
        )


@router.get("/stats/service", summary="Get Service Statistics")
async def get_service_stats(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get statistics about the memory service."""
    try:
        stats = await memory_service.get_service_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting service stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving service statistics"
        )