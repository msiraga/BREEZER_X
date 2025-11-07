"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime
import psutil
import torch

from core.config import settings
from services.vector_store import get_collection_stats

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with system info"""
    try:
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # GPU info
        gpu_available = torch.cuda.is_available()
        gpu_info = None
        if gpu_available:
            gpu_info = {
                "name": torch.cuda.get_device_name(0),
                "memory_allocated": torch.cuda.memory_allocated(0),
                "memory_reserved": torch.cuda.memory_reserved(0)
            }
        
        # Vector store stats
        try:
            vector_stats = await get_collection_stats()
        except:
            vector_stats = {"status": "unavailable"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3)
            },
            "gpu": {
                "available": gpu_available,
                "info": gpu_info
            },
            "services": {
                "vector_store": vector_stats,
                "sandbox": settings.SANDBOX_ENABLED
            },
            "configuration": {
                "embeddings_provider": settings.EMBEDDINGS_PROVIDER,
                "embeddings_device": settings.EMBEDDINGS_DEVICE if settings.EMBEDDINGS_PROVIDER == "local" else "N/A"
            }
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
