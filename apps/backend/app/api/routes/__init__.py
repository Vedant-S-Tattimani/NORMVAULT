"""
API route exports.
"""

from app.api.routes.health import router as health_router
from app.api.routes.standards import router as standards_router
from app.api.routes.editions import router as editions_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.compliance import router as compliance_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.documents import router as documents_router
from app.api.routes.retrieval import router as retrieval_router
from app.api.routes.applicability import router as applicability_router
from app.api.routes.currentness import router as currentness_router
from app.api.routes.gaps import router as gaps_router
from app.api.routes.readiness import router as readiness_router
from app.api.routes.intelligence import router as intelligence_router

__all__ = [
    "health_router",
    "standards_router",
    "editions_router",
    "analysis_router",
    "compliance_router",
    "recommendations_router",
    "documents_router",
    "retrieval_router",
    "applicability_router",
    "currentness_router",
    "gaps_router",
    "readiness_router",
    "intelligence_router",
]


