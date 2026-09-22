"""
Currentness & Edition Adjudication API Routes.
Evaluates edition resolution, supersession, withdrawal, and procurement warnings for tender requirements.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import DatabaseSession
from app.models.standard import IndianStandard
from app.models.requirement import Requirement, ProcurementSpecification
from app.models.applicability import ApplicabilityAssessment, ApplicabilityOutcome
from app.schemas.edition import CurrentnessEvaluation, TenderCitationExtraction, CitationType
from app.services.currentness import CurrentnessAnalyzer, TenderCitationExtractor

router = APIRouter()
currentness_analyzer = CurrentnessAnalyzer()
citation_extractor = TenderCitationExtractor()


@router.post("/requirements/{requirement_id}", response_model=List[CurrentnessEvaluation])
def evaluate_requirement_currentness(
    requirement_id: int,
    db: Session = DatabaseSession,
) -> List[CurrentnessEvaluation]:
    """
    Adjudicates standard edition currentness, amendments, and citations for a single requirement.
    """
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    from app.models.applicability import ApplicabilityRun

    # 1. Check if applicability assessments exist for this requirement
    runs = db.query(ApplicabilityRun).filter(ApplicabilityRun.requirement_id == requirement_id).all()
    run_ids = [r.id for r in runs]

    assessments = (
        db.query(ApplicabilityAssessment)
        .filter(
            ApplicabilityAssessment.run_id.in_(run_ids),
            ApplicabilityAssessment.outcome.in_([
                ApplicabilityOutcome.APPLICABLE,
                ApplicabilityOutcome.POSSIBLY_APPLICABLE,
            ]),
        )
        .all()
        if run_ids
        else []
    )

    evaluations: List[CurrentnessEvaluation] = []
    evaluated_std_ids = set()

    # If assessments exist, evaluate currentness for each applicable candidate
    for assess in assessments:
        std = db.query(IndianStandard).filter(IndianStandard.id == assess.standard_id).first()
        if std and std.id not in evaluated_std_ids:
            evaluated_std_ids.add(std.id)
            evaluation = currentness_analyzer.evaluate_requirement_currentness(
                db=db,
                standard=std,
                requirement_text=req.extracted_text,
                technical_applicability=assess.outcome.value,
            )
            evaluations.append(evaluation)

    # 2. Also check if there are direct citations in the requirement text not yet assessed
    citations = citation_extractor.extract_citations(req.extracted_text or "")
    for cit in citations:
        std = db.query(IndianStandard).filter(IndianStandard.standard_number == cit.standard_number).first()
        if std and std.id not in evaluated_std_ids:
            evaluated_std_ids.add(std.id)
            evaluation = currentness_analyzer.evaluate_requirement_currentness(
                db=db,
                standard=std,
                requirement_text=req.extracted_text,
                technical_applicability="APPLICABLE",
            )
            evaluations.append(evaluation)

    return evaluations


@router.post("/specifications/{specification_id}", response_model=List[CurrentnessEvaluation])
def evaluate_specification_currentness(
    specification_id: int,
    db: Session = DatabaseSession,
) -> List[CurrentnessEvaluation]:
    """
    Adjudicates standard edition currentness and checks for conflicting edition citations
    across all requirements in an entire procurement specification.
    """
    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == specification_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Procurement specification not found")

    requirements = db.query(Requirement).filter(Requirement.specification_id == specification_id).all()

    # Collect all citations across all clauses to detect conflicts
    all_citations: List[TenderCitationExtraction] = []
    for req in requirements:
        sec_name = req.evidence.section_heading if req.evidence else req.clause_reference
        raw_ext = citation_extractor.extract_citations(req.extracted_text or "", section_name=sec_name)
        all_citations.extend(raw_ext)

    # Detect conflicts across the specification
    resolved_citations = citation_extractor.detect_conflicts(all_citations)
    conflict_stds = {
        cit.standard_number for cit in resolved_citations if cit.citation_type == CitationType.CONFLICTING
    }

    evaluations: List[CurrentnessEvaluation] = []
    evaluated_std_ids = set()

    for req in requirements:
        req_evals = evaluate_requirement_currentness(requirement_id=req.id, db=db)
        for ev in req_evals:
            if ev.standard_number in conflict_stds:
                ev.status = "CONFLICTING_EDITION_REFERENCES"
                ev.edition_applicability = "CONFLICTING_REFERENCES"
                ev.procurement_warning = (
                    f"Conflicting edition citations detected across tender clauses for {ev.standard_number}. "
                    "Manual clarification required before tender issuance."
                )
            if (ev.standard_number, ev.resolved_edition_year) not in evaluated_std_ids:
                evaluated_std_ids.add((ev.standard_number, ev.resolved_edition_year))
                evaluations.append(ev)

    return evaluations
