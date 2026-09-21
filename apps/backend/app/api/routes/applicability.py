"""
REST API Endpoints for Standards Applicability & Recommendations.
Handles requirement-level and specification-level applicability assessments, runs, and evidence queries.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.requirement import Requirement, ProcurementSpecification
from app.models.applicability import ApplicabilityRun
from app.schemas.applicability import (
    ApplicabilityAnalyzeRequest,
    ApplicabilityRunRead,
    ApplicabilityAssessmentRead,
    SpecificationApplicabilityRead,
)
from app.services.applicability.engine import ApplicabilityEngine

router = APIRouter()
applicability_engine = ApplicabilityEngine()


@router.post(
    "/requirements/{requirement_id}",
    response_model=ApplicabilityRunRead,
    summary="Assess Standards Applicability for a Single Requirement",
    description="Evaluates candidate Indian Standards using verified scope, parameter compatibility, and negative evidence.",
)
def assess_requirement_applicability(
    requirement_id: int,
    payload: Optional[ApplicabilityAnalyzeRequest] = None,
    db: Session = Depends(get_db),
) -> ApplicabilityRunRead:
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {requirement_id} not found.",
        )

    config = payload or ApplicabilityAnalyzeRequest()
    run = applicability_engine.analyze_requirement(
        db=db,
        requirement=req,
        top_k=config.top_k,
        division_code=config.division_code,
        include_withdrawn=config.include_withdrawn,
        require_exact_product=config.require_exact_product,
    )
    return applicability_engine._serialize_run(run)


@router.post(
    "/specifications/{specification_id}",
    response_model=SpecificationApplicabilityRead,
    summary="Assess Standards Applicability for an Entire Specification",
    description="Consolidates applicability analysis across all extracted requirements of a procurement tender.",
)
def assess_specification_applicability(
    specification_id: int,
    payload: Optional[ApplicabilityAnalyzeRequest] = None,
    db: Session = Depends(get_db),
) -> SpecificationApplicabilityRead:
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement Specification with ID {specification_id} not found.",
        )

    config = payload or ApplicabilityAnalyzeRequest()
    return applicability_engine.analyze_specification(
        db=db,
        specification=spec,
        top_k=config.top_k,
        division_code=config.division_code,
        include_withdrawn=config.include_withdrawn,
    )


@router.get(
    "/runs/{run_id}",
    response_model=ApplicabilityRunRead,
    summary="Get Applicability Run by ID",
    description="Retrieves a persisted, auditable applicability execution record and its assessments.",
)
def get_applicability_run(
    run_id: int,
    db: Session = Depends(get_db),
) -> ApplicabilityRunRead:
    run = db.query(ApplicabilityRun).filter(ApplicabilityRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicability run with ID {run_id} not found.",
        )
    return applicability_engine._serialize_run(run)


@router.get(
    "/runs/{run_id}/assessments",
    response_model=List[ApplicabilityAssessmentRead],
    summary="Get Assessments for an Applicability Run",
    description="Retrieves individual candidate assessments, component evidence, and conflicts.",
)
def get_run_assessments(
    run_id: int,
    db: Session = Depends(get_db),
) -> List[ApplicabilityAssessmentRead]:
    run = db.query(ApplicabilityRun).filter(ApplicabilityRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicability run with ID {run_id} not found.",
        )
    serialized = applicability_engine._serialize_run(run)
    return serialized.assessments


from app.services.dependencies.engine import StandardsComplianceEngine

compliance_engine = StandardsComplianceEngine()


@router.post(
    "/runs/{run_id}/dependencies",
    summary="Generate Compliance and Dependency Intelligence for Run",
    description="Gathers dependency graphs, test methods, safety requirements, and QCO status for all recommended standards in an applicability run.",
)
def get_run_dependencies(
    run_id: int,
    db: Session = Depends(get_db),
):
    try:
        return compliance_engine.get_applicability_run_compliance(db, run_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

