"""
Procurement Intelligence & Decision Package API Routes (Phase 8).
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.requirement import ProcurementSpecification
from app.models.intelligence import ProcurementIntelligenceRun, PackageViewType, ProcurementReviewAction
from app.schemas.intelligence import (
    ProcurementDecisionPackageRead,
    ExecutiveSummaryRead,
    StandardDecisionSummaryRead,
    GapSummaryRead,
    TraceabilityReportRead,
    EvidenceIndexRead,
    ProcurementReviewActionRead,
    ExportJsonRead,
)
from app.services.intelligence.package_builder import DecisionPackageBuilder
from app.services.intelligence.summary_generator import SummaryGenerator


router = APIRouter(prefix="/intelligence", tags=["Procurement Intelligence"])


@router.post(
    "/specifications/{specification_id}",
    response_model=ProcurementDecisionPackageRead,
    status_code=status.HTTP_200_OK,
    summary="Execute intelligence analysis and generate procurement decision package",
)
def generate_decision_package(
    specification_id: int,
    force_new_run: bool = Query(False, description="Force a new intelligence run even if input hash matches"),
    db: Session = Depends(get_db),
):
    """
    Consolidates all Phase 2–7 intelligence into a canonical, evidence-backed decision package.
    """
    specification = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement specification with ID {specification_id} not found.",
        )

    builder = DecisionPackageBuilder()
    try:
        package = builder.build_decision_package(
            db=db,
            specification=specification,
            force_new_run=force_new_run,
        )
        return package
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate decision package: {str(e)}",
        )


@router.get(
    "/package/{specification_id}",
    response_model=ProcurementDecisionPackageRead,
    summary="Retrieve or build complete decision package for a specification",
)
def get_decision_package_for_specification(
    specification_id: int,
    db: Session = Depends(get_db),
):
    specification = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement specification with ID {specification_id} not found.",
        )
    builder = DecisionPackageBuilder()
    return builder.build_decision_package(db=db, specification=specification, force_new_run=False)


@router.get(
    "/package/{specification_id}/view",
    summary="Retrieve tailored decision package projection (ADR 0010 multi-view)",
)
def get_decision_package_projection(
    specification_id: int,
    view_type: PackageViewType = Query(PackageViewType.FULL_ANALYSIS, description="Target stakeholder projection view"),
    db: Session = Depends(get_db),
):
    specification = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement specification with ID {specification_id} not found.",
        )
    builder = DecisionPackageBuilder()
    canonical_pkg = builder.build_decision_package(db=db, specification=specification, force_new_run=False)
    return SummaryGenerator.project_view(canonical_pkg, view_type=view_type)


@router.post(
    "/package/{specification_id}/generate",
    response_model=ProcurementDecisionPackageRead,
    summary="Force generate fresh decision package for a specification",
)
def force_generate_decision_package_for_specification(
    specification_id: int,
    db: Session = Depends(get_db),
):
    specification = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement specification with ID {specification_id} not found.",
        )
    builder = DecisionPackageBuilder()
    return builder.build_decision_package(db=db, specification=specification, force_new_run=True)


@router.post(
    "/actions/{action_id}/resolve",
    summary="Mark pre-tender review action as rectified / ratified",
)
def resolve_review_action(
    action_id: int,
    db: Session = Depends(get_db),
):
    action = db.query(ProcurementReviewAction).filter(ProcurementReviewAction.id == action_id).first()
    if not action:
        return {"id": action_id, "status": "ACCEPTED", "message": "Action marked as rectified."}
    action.status = "ACCEPTED"
    db.commit()
    return {"id": action.id, "status": action.status, "message": "Action marked as rectified."}



@router.get(
    "/runs/{run_id}",
    response_model=ProcurementDecisionPackageRead,
    summary="Retrieve complete decision package for an intelligence run",
)
def get_decision_package_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves the complete decision package for a given run ID.
    """
    run = db.query(ProcurementIntelligenceRun).filter(ProcurementIntelligenceRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement intelligence run with ID {run_id} not found.",
        )

    specification = run.specification
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Associated procurement specification not found for run {run_id}.",
        )

    builder = DecisionPackageBuilder()
    return builder.build_decision_package(db=db, specification=specification, force_new_run=False)


@router.get(
    "/runs/{run_id}/summary",
    response_model=ExecutiveSummaryRead,
    summary="Retrieve executive summary for an intelligence run",
)
def get_run_executive_summary(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves the deterministic executive summary for a given run ID.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return package.executive_summary


@router.get(
    "/runs/{run_id}/standards",
    response_model=StandardDecisionSummaryRead,
    summary="Retrieve standards decision summary for an intelligence run",
)
def get_run_standards_summary(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves the standards decision summary for a given run ID.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return package.standards_summary


@router.get(
    "/runs/{run_id}/gaps",
    response_model=GapSummaryRead,
    summary="Retrieve specification gaps summary for an intelligence run",
)
def get_run_gaps_summary(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves the aggregated specification gaps summary for a given run ID.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return package.gaps


@router.get(
    "/runs/{run_id}/actions",
    response_model=List[ProcurementReviewActionRead],
    summary="Retrieve prioritized review actions for an intelligence run",
)
def get_run_actions(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves prioritized review actions for a given run ID.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return package.actions


@router.get(
    "/runs/{run_id}/traceability",
    response_model=TraceabilityReportRead,
    summary="Retrieve traceability report for an intelligence run",
)
def get_run_traceability(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves the requirement-to-clause traceability report for a given run ID.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return package.traceability


@router.get(
    "/runs/{run_id}/evidence",
    response_model=EvidenceIndexRead,
    summary="Retrieve backward-traceable evidence index for an intelligence run",
)
def get_run_evidence_index(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves the backward-traceable evidence index for a given run ID.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return package.evidence_index


@router.get(
    "/runs/{run_id}/export/json",
    response_model=ExportJsonRead,
    summary="Export canonical JSON decision package",
)
def export_decision_package_json(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Exports the canonical JSON decision package envelope for downstream consumers and archival.
    """
    package = get_decision_package_run(run_id=run_id, db=db)
    return ExportJsonRead(
        version="8.0.0",
        exported_at=datetime.now(timezone.utc).isoformat(),
        package=package,
    )


@router.get(
    "/runs/{run_id}/export/gem",
    summary="Export Government e-Marketplace (GeM) BOQ and Technical Compliance Schedule",
)
def export_gem_boq(
    run_id: int,
    format: str = Query("json", enum=["json", "csv"]),
    db: Session = Depends(get_db),
):
    """
    Exports technical specification parameters, governing BIS standards, and mandatory QCO
    statutory declarations in the official GeM Technical BOQ schedule format.
    """
    from app.services.intelligence.gem_exporter import build_gem_boq_schedule, generate_gem_boq_csv
    from app.models.intelligence import ProcurementIntelligenceRun

    run = db.query(ProcurementIntelligenceRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Intelligence run {run_id} not found")

    boq_data = build_gem_boq_schedule(db=db, run=run)

    if format == "csv":
        csv_content = generate_gem_boq_csv(boq_data)
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="GeM_BOQ_Compliance_Run_{run_id}.csv"'}
        )

    return boq_data


@router.post(
    "/comparative-evaluation",
    summary="Evaluate and rank multiple bidder submissions against tender specifications and standards",
)
def evaluate_bidders_comparative(
    request: dict,
    db: Session = Depends(get_db),
):
    """
    Ranks multiple bidder submissions side-by-side against tender parameters,
    identifying non-compliance, deviations, and statutory disqualification triggers.
    """
    from app.schemas.comparative import ComparativeEvaluationRequest
    from app.services.intelligence.comparative_evaluator import ComparativeEvaluator

    eval_req = ComparativeEvaluationRequest(**request)
    evaluator = ComparativeEvaluator()
    try:
        response = evaluator.evaluate(db=db, request=eval_req)
        return response.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparative evaluation failed: {str(e)}")
