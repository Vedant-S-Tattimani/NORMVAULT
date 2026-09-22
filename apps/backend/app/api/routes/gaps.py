"""
Procurement Specification Gap Analysis & Compliance Readiness API Routes.
Exposes endpoints for evaluating missing parameters, ambiguities, contradictions,
standard coverage matrices, and specification readiness assessments.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.dependencies import DatabaseSession
from app.models.gap import SpecificationGap, ProcurementReadinessAssessment
from app.models.requirement import Requirement, ProcurementSpecification
from app.models.standard import IndianStandard, StandardEdition, EditionStatus
from app.models.applicability import ApplicabilityRun, ApplicabilityAssessment, ApplicabilityOutcome
from app.schemas.gap import (
    GapItemRead,
    CoverageMatrixItem,
    TraceabilityNode,
    RequirementGapAnalysisRead,
    SpecificationReadinessRead,
)
from app.services.gaps import ProcurementReadinessService
from app.services.currentness import TenderCitationExtractor


router = APIRouter()
readiness_service = ProcurementReadinessService()
citation_extractor = TenderCitationExtractor()


def _resolve_applicable_standard(
    db: Session,
    specification: ProcurementSpecification,
) -> tuple[Optional[IndianStandard], Optional[StandardEdition]]:
    """
    Resolves the primary applicable Indian Standard and active edition for a specification
    using applicability runs, requirements citations, or text scanning.
    """
    reqs = specification.requirements or []
    req_ids = [r.id for r in reqs]

    # 1. Check existing Applicability Assessments
    if req_ids:
        runs = db.query(ApplicabilityRun).filter(ApplicabilityRun.requirement_id.in_(req_ids)).all()
        run_ids = [r.id for r in runs]
        if run_ids:
            assess = (
                db.query(ApplicabilityAssessment)
                .filter(
                    ApplicabilityAssessment.run_id.in_(run_ids),
                    ApplicabilityAssessment.outcome == ApplicabilityOutcome.APPLICABLE,
                )
                .order_by(ApplicabilityAssessment.applicability_score.desc())
                .first()
            )
            if assess:
                std = db.query(IndianStandard).filter(IndianStandard.id == assess.standard_id).first()
                if std:
                    current_ed = next((e for e in std.editions if e.status == EditionStatus.CURRENT), None)
                    if not current_ed and std.editions:
                        current_ed = sorted(std.editions, key=lambda e: e.year or 0, reverse=True)[0]
                    return std, current_ed

    # 2. Check Tender Citations across requirements
    for r in reqs:
        citations = citation_extractor.extract_citations(r.extracted_text)
        for c in citations:
            std = db.query(IndianStandard).filter(IndianStandard.standard_number == c.standard_number).first()
            if std:
                target_ed = None
                if c.edition_year:
                    target_ed = next((e for e in std.editions if e.year == c.edition_year), None)
                if not target_ed:
                    target_ed = next((e for e in std.editions if e.status == EditionStatus.CURRENT), None)
                if not target_ed and std.editions:
                    target_ed = sorted(std.editions, key=lambda e: e.year or 0, reverse=True)[0]
                return std, target_ed

    # 3. Text fallback for IS 12615
    combined = " ".join(r.extracted_text for r in reqs).lower()
    if "12615" in combined or "motor" in combined or "induction" in combined:
        std = db.query(IndianStandard).filter(IndianStandard.standard_number.ilike("%12615%")).first()
        if std:
            current_ed = next((e for e in std.editions if e.status == EditionStatus.CURRENT), None)
            if not current_ed and std.editions:
                current_ed = sorted(std.editions, key=lambda e: e.year or 0, reverse=True)[0]
            return std, current_ed

    return None, None


@router.post("/requirements/{requirement_id}", response_model=RequirementGapAnalysisRead)
def evaluate_requirement_gaps(
    requirement_id: int,
    db: Session = DatabaseSession,
) -> RequirementGapAnalysisRead:
    """
    Evaluates an individual requirement clause for subjective, vague, or non-measurable expressions.
    """
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=404, detail=f"Requirement with ID {requirement_id} not found")

    return readiness_service.evaluate_requirement(req)


@router.post("/specifications/{specification_id}", response_model=SpecificationReadinessRead)
def evaluate_specification_gaps(
    specification_id: int,
    db: Session = DatabaseSession,
) -> SpecificationReadinessRead:
    """
    Executes full gap analysis and readiness assessment across an entire specification,
    identifying missing parameters, conflicts, test method gaps, safety omissions, and QCO issues.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification with ID {specification_id} not found")

    std, ed = _resolve_applicable_standard(db, spec)
    result = readiness_service.evaluate_specification(
        specification=spec,
        applicable_standard=std,
        applicable_edition=ed,
        db=db,
    )
    return result


@router.get("/specifications/{specification_id}", response_model=List[GapItemRead])
def get_specification_gaps(
    specification_id: int,
    db: Session = DatabaseSession,
) -> List[GapItemRead]:
    """
    Retrieves all identified specification gaps and ambiguities for a procurement specification.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification with ID {specification_id} not found")

    gaps = (
        db.query(SpecificationGap)
        .filter(SpecificationGap.specification_id == specification_id)
        .all()
    )

    if not gaps:
        # Run evaluation dynamically
        std, ed = _resolve_applicable_standard(db, spec)
        res = readiness_service.evaluate_specification(spec, std, ed, db=db)
        return res.gaps

    std, _ = _resolve_applicable_standard(db, spec)
    return [
        GapItemRead(
            id=g.id,
            specification_id=specification_id,
            requirement_id=g.requirement_id,
            gap_type=g.gap_type,
            severity=g.severity,
            status=g.status,
            title=g.title,
            description=g.description,
            why_it_matters=g.why_it_matters or "",
            required_clarification=g.required_clarification or "",
            affected_parameter=g.affected_parameter,
            current_value=g.current_value,
            expected_information=g.expected_information,
            affected_standard_id=g.affected_standard_id,
            affected_standard_number=std.standard_number if std else None,
            affected_edition_id=g.affected_edition_id,
            affected_clause=g.affected_clause,
            evidence_snippet=g.evidence_snippet,
            source=g.source,
        )
        for g in gaps
    ]


@router.get("/specifications/{specification_id}/readiness", response_model=SpecificationReadinessRead)
def get_specification_readiness(
    specification_id: int,
    db: Session = DatabaseSession,
) -> SpecificationReadinessRead:
    """
    Retrieves the comprehensive procurement readiness assessment for a specification under gaps.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification with ID {specification_id} not found")

    std, ed = _resolve_applicable_standard(db, spec)
    return readiness_service.evaluate_specification(spec, std, ed, db=db)


@router.get("/specifications/{specification_id}/matrix", response_model=List[CoverageMatrixItem])
def get_specification_coverage_matrix(
    specification_id: int,
    db: Session = DatabaseSession,
) -> List[CoverageMatrixItem]:
    """
    Retrieves the Standard Coverage Matrix comparing tender requirements to the applicable Indian Standard.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification with ID {specification_id} not found")

    std, ed = _resolve_applicable_standard(db, spec)
    res = readiness_service.evaluate_specification(spec, std, ed, db=None)
    return res.coverage_matrix


@router.get("/{gap_id}", response_model=GapItemRead)
def get_gap_by_id(
    gap_id: int,
    db: Session = DatabaseSession,
) -> GapItemRead:
    """
    Retrieves a single specification gap by its ID.
    """
    gap = db.query(SpecificationGap).filter(SpecificationGap.id == gap_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail=f"Gap with ID {gap_id} not found")

    std = (
        db.query(IndianStandard).filter(IndianStandard.id == gap.affected_standard_id).first()
        if gap.affected_standard_id
        else None
    )

    return GapItemRead(
        id=gap.id,
        specification_id=gap.specification_id or 0,
        requirement_id=gap.requirement_id,
        gap_type=gap.gap_type,
        severity=gap.severity,
        status=gap.status,
        title=gap.title,
        description=gap.description,
        why_it_matters=gap.why_it_matters or "",
        required_clarification=gap.required_clarification or "",
        affected_parameter=gap.affected_parameter,
        current_value=gap.current_value,
        expected_information=gap.expected_information,
        affected_standard_id=gap.affected_standard_id,
        affected_standard_number=std.standard_number if std else None,
        affected_edition_id=gap.affected_edition_id,
        affected_clause=gap.affected_clause,
        evidence_snippet=gap.evidence_snippet,
        source=gap.source,
    )
