from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List
import logging
import os
from dotenv import load_dotenv

# Import routers
from .agent_controller import router as agent_router
from .mission_controller import router as mission_router
from .super_agent_controller import router as super_agent_router
from .auth_controller import router as auth_router

# Import authentication middleware
from .auth_middleware import get_current_user, has_role

# Import database
from .database import init_db

# Import schemas
from .schemas import ErrorResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("supermean-api")

# Create FastAPI app
app = FastAPI(
    title="SuperMean API",
    description="API for the SuperMean agent system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
from backend.utils.error_handler import SuperMeanException, APIValidationError, ConfigurationError, ModelConnectionError, SkillError, AgentError, MemoryError, OrchestrationError
from backend.utils.logger import logger as custom_logger # Use custom logger

@app.exception_handler(SuperMeanException)
async def supermean_exception_handler(request, exc: SuperMeanException):
    """Handle custom SuperMean exceptions"""
    custom_logger.error(f"SuperMeanException caught: {exc} for request {request.method} {request.url}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.message,
            error_code=exc.__class__.__name__.upper(),
        ).dict(),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    custom_logger.error(f"Validation error: {exc} for request {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()}
        ).dict(),
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    custom_logger.error(f"HTTP error {exc.status_code}: {exc.detail} for request {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code="HTTP_ERROR",
        ).dict(),
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    custom_logger.error(f"Unhandled exception caught: {exc} for request {request.method} {request.url}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="An unexpected internal server error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
        ).dict(),
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "SuperMean API is running!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(agent_router, prefix="/api/agents", tags=["agents"])
app.include_router(mission_router, prefix="/api/missions", tags=["missions"])
app.include_router(super_agent_router, prefix="/api/super-agent", tags=["super-agent"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("SuperMean API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("SuperMean API shutting down...")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)