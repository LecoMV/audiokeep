"""
AudioKeep Main Application
FastAPI application with audio processing capabilities
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1 import api_router
from app.db.session import engine
from app.models import base

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AudioKeep application...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Create database tables
    # In production, use Alembic migrations instead
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(base.Base.metadata.create_all)
            logger.info("Database tables created")

    yield

    # Shutdown
    logger.info("Shutting down AudioKeep application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Professional AI-powered audio restoration and enhancement platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
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

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if not settings.DEBUG else str(exc)
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.APP_ENV
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "description": "Professional AI-powered audio restoration platform",
        "docs": "/docs" if settings.DEBUG else "Contact support for API documentation",
        "health": "/health"
    }


# Include API router
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

# WebSocket endpoint for real-time job updates
from app.api.websocket import websocket_job_status

@app.websocket("/api/v1/ws/jobs/{job_id}")
async def websocket_endpoint(websocket, job_id: str, token: str):
    """WebSocket endpoint for real-time job status updates"""
    await websocket_job_status(websocket, job_id, token)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
