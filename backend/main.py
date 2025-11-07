"""
BREEZER_X Backend API
Main application entry point
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import logging

from api.routes import agent, health, tasks, context
from core.config import settings
from core.database import init_db
from core.embeddings import init_embeddings
from services.vector_store import init_vector_store

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting BREEZER_X Backend...")
    
    # Initialize databases
    logger.info("Initializing databases...")
    await init_db()
    
    # Initialize vector store
    logger.info("Initializing vector store...")
    await init_vector_store()
    
    # Initialize embeddings model (GPU if available)
    logger.info("Initializing embeddings...")
    await init_embeddings()
    
    logger.info("✅ BREEZER_X Backend ready!")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="BREEZER_X API",
    description="AI-Powered Development Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(context.router, prefix="/api/context", tags=["context"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "BREEZER_X API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1
    )
