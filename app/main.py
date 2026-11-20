from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.core.logging_config import logger
from app.database.connection import init_db
from app.services.face_service import face_service
from app.api.students import router as students_router
from app.api.attendance import router as attendance_router
from app.api.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management.
    Initializes database schema and prepares the computer vision pipeline.
    """
    logger.info("Initializing Face Recognition Attendance System Backend...")
    try:
        init_db()
        logger.info("Database connection and tables initialized.")
    except Exception as e:
        logger.error(f"Database initialization warning: {e}")

    # Log model status
    if face_service.is_model_loaded:
        logger.info(f"Computer Vision pipeline ready with {len(face_service.label_map)} identities.")
    else:
        logger.warning("LBPH Model not found on disk. Upload face samples and trigger /api/v1/students/train/model to train.")

    yield
    logger.info("Shutting down Face Recognition Attendance System Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready FastAPI backend for Face Recognition Attendance Management using OpenCV and MySQL.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    safe_errors = []
    for err in exc.errors():
        safe_errors.append({
            "type": err.get("type"),
            "loc": [str(l) for l in err.get("loc", [])],
            "msg": err.get("msg"),
            "input": str(err.get("input", "")),
        })
    logger.warning(f"Validation error on {request.url}: {safe_errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": safe_errors
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "A database persistence error occurred. Please check database connectivity."
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc)
        }
    )

# Register API Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(students_router, prefix="/api/v1/students", tags=["Students"])
app.include_router(attendance_router, prefix="/api/v1/attendance", tags=["Attendance"])

@app.get("/", tags=["Health"])
def root():
    """System status and API overview."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "model_loaded": face_service.is_model_loaded,
        "mapped_identities": len(face_service.label_map),
        "database": settings.DB_NAME
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Quick health probe endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
