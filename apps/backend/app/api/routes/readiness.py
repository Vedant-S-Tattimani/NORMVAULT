"""
Procurement Readiness Assessment API Routes.
Exposes endpoints for evaluating overall readiness state and completeness categories for tender specifications.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import DatabaseSession
from app.models.requirement import ProcurementSpecification
from app.schemas.gap import SpecificationReadinessRead
from app.api.routes.gaps import _resolve_applicable_standard, readiness_service

router = APIRouter()


@router.get("/specifications/{specification_id}", response_model=SpecificationReadinessRead)
def get_specification_readiness(
    specification_id: int,
    db: Session = DatabaseSession,
) -> SpecificationReadinessRead:
    """
    Retrieves the comprehensive procurement readiness assessment for a specification,
    including explainable completeness counts, categorized gaps, and summary rationale.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification with ID {specification_id} not found")

    std, ed = _resolve_applicable_standard(db, spec)
    return readiness_service.evaluate_specification(spec, std, ed, db=db)


@router.post("/specifications/{specification_id}", response_model=SpecificationReadinessRead)
def recalculate_specification_readiness(
    specification_id: int,
    db: Session = DatabaseSession,
) -> SpecificationReadinessRead:
    """
    Forces recalculation and database persistence of readiness assessment for a specification.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification with ID {specification_id} not found")

    std, ed = _resolve_applicable_standard(db, spec)
    return readiness_service.evaluate_specification(spec, std, ed, db=db)
