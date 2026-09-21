"""
NORMVAULT Backend Application Entrypoint.
Smart India Hackathon Problem Statement 26108.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine, check_db_connection
from app.api.routes import (
    health_router,
    standards_router,
    editions_router,
    analysis_router,
    compliance_router,
    recommendations_router,
    documents_router,
    retrieval_router,
    applicability_router,
    currentness_router,
    gaps_router,
    readiness_router,
    intelligence_router,
)
from app.api.routes.specifications import router as specifications_router

setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
logger = logging.getLogger("normvault.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing NORMVAULT Standards Intelligence Engine...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | API Prefix: {settings.API_V1_STR}")

    # Verify and initialize database tables
    try:
        db_ok = check_db_connection()
        if db_ok:
            logger.info("Database connection established successfully.")
            # Automatically create schema tables for dev/testing
            Base.metadata.create_all(bind=engine)
            logger.info("Database metadata schema synchronized.")
        else:
            logger.warning("Database is currently unreachable. Operating in degraded mode.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

    yield

    logger.info("Shutting down NORMVAULT Engine.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production API for NORMVAULT: AI-Powered Recommendation Engine for "
        "Identifying Applicable Indian Standards for Procurement Specifications (SIH PS 26108)."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers for consistent error envelope
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The submitted payload failed validation constraints.",
                "details": exc.errors(),
            }
        },
    )


from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )
    logger.exception(f"Unhandled server exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing the request.",
                "details": str(exc) if settings.DEBUG else None,
            }
        },
    )



# Root information endpoint
@app.get("/", tags=["System"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "health_url": f"{settings.API_V1_STR}/health",
    }


# Mount API v1 Routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(documents_router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(specifications_router, prefix=f"{settings.API_V1_STR}/specifications", tags=["Specifications"])
app.include_router(analysis_router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Analysis"])
app.include_router(standards_router, prefix=f"{settings.API_V1_STR}/standards", tags=["Standards"])
app.include_router(editions_router, prefix=f"{settings.API_V1_STR}/editions", tags=["Editions"])
app.include_router(recommendations_router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Recommendations"])
app.include_router(compliance_router, prefix=f"{settings.API_V1_STR}/compliance", tags=["Compliance"])
app.include_router(retrieval_router, prefix=f"{settings.API_V1_STR}/retrieval", tags=["Retrieval"])
app.include_router(applicability_router, prefix=f"{settings.API_V1_STR}/applicability", tags=["Applicability"])
app.include_router(currentness_router, prefix=f"{settings.API_V1_STR}/currentness", tags=["Currentness"])
app.include_router(gaps_router, prefix=f"{settings.API_V1_STR}/gaps", tags=["Gaps"])
app.include_router(readiness_router, prefix=f"{settings.API_V1_STR}/readiness", tags=["Readiness"])
app.include_router(intelligence_router, prefix=f"{settings.API_V1_STR}", tags=["Procurement Intelligence"])

