from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from app.core.config import settings
from app.core.database import engine
from app.core.database import Base, create_tables_sync
from app.core.mongodb import init_database, close_database, mongodb
from app.api.v1 import auth, voices, tts, training, users, verify, licenses, otp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Voice Clone Platform API")
    
    # Create database tables (SQLAlchemy)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLAlchemy database initialized")
    except Exception as e:
        logger.warning(f"SQLAlchemy database initialization failed: {e}")
    
    # Initialize MongoDB connection
    mongo_success = await init_database()
    if mongo_success:
        logger.info("MongoDB initialized successfully")
        # Create test data in development
        if settings.ENVIRONMENT == "development":
            await mongodb.create_test_data()
    else:
        logger.error("MongoDB initialization failed")
    
    yield
    
    # Cleanup
    await close_database()
    logger.info("Shutting down Voice Clone Platform API")


# Create FastAPI application
app = FastAPI(
    title="Voice Clone Platform API",
    description="Advanced AI voice cloning and text-to-speech platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Voice Clone Platform API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(voices.router, prefix="/api/v1/voices", tags=["Voice Management"])
app.include_router(licenses.router, prefix="/api/v1/licenses", tags=["Licensing"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])
app.include_router(training.router, prefix="/api/v1/training", tags=["Voice Training"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(verify.router, prefix="/api/v1/verify", tags=["Security & Verification"])
app.include_router(otp.router, prefix="/api/v1", tags=["OTP Auth"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
