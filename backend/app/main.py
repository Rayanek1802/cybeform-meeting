"""
CybeMeeting Backend - FastAPI Application
Main entry point for the BTP meeting analysis platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv

from app.api.routes import router
from app.core.config import settings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 CybeMeeting API starting...")
    
    # Ensure data directories exist
    os.makedirs(settings.DATA_PATH, exist_ok=True)
    os.makedirs(os.path.join(settings.DATA_PATH, "projects"), exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("👋 CybeMeeting API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="CybeMeeting API",
    description="API pour l'analyse intelligente de réunions BTP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "CybeMeeting API",
            "version": "1.0.0"
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "CybeMeeting API",
            "docs": "/docs",
            "health": "/health"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

