"""
Health check endpoint providing real-time system and database diagnostics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.session import get_db, engine
from app.schemas.health import HealthResponse, DatabaseHealth

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System and Database Health Check",
    description="Returns real runtime status, version, and database connectivity metrics.",
)
def get_health(db: Session = Depends(get_db)) -> HealthResponse:
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    dialect_name = engine.dialect.name
    pool_info = f"size={engine.pool.size() if hasattr(engine.pool, 'size') else 'n/a'}"

    # Determine pgvector support readiness
    pgvector_ready = False
    if dialect_name == "postgresql" and db_connected:
        try:
            result = db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar()
            pgvector_ready = bool(result)
        except Exception:
            pgvector_ready = False
    elif dialect_name == "sqlite":
        pgvector_ready = False  # SQLite development mode

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=DatabaseHealth(
            connected=db_connected,
            dialect=dialect_name,
            pool_status=pool_info,
        ),
        details={
            "debug_mode": settings.DEBUG,
            "pgvector_extension_ready": pgvector_ready,
            "llm_provider": settings.LLM_PROVIDER,
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "embedding_model": settings.EMBEDDING_MODEL,
        },
    )
