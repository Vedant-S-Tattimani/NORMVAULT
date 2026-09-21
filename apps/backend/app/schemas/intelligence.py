"""
Pydantic Schemas for Procurement Intelligence Runs and Consolidated Decision Packages (Phase 8).
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.intelligence import ActionPriority, ActionType, PackageViewType


# ---------------------------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------------------------

class ExecutiveSummaryRead(BaseModel):
    procurement_title: str
    specification_id: int
    requirements_count: int
    standards_count: int
    applicable_standards_count: int
    primary_standard: Optional[str] = None
    alternative_standards: List[str] = Field(default_factory=list)
    currentness_status: str
    critical_gaps_count: int
    high_gaps_count: int
    ambiguities_count: int
    readiness_state: str
    summary_rationale: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Standard Decision Summary
# ---------------------------------------------------------------------------

class StandardDecisionItemRead(BaseModel):
    standard_id: int
    standard_code: str
    title: str
    edition: Optional[str] = None
    currentness: str
    applicability_outcome: str
    evidence_alignment_score: float
    scope_result: str
    product_result: str
    parameter_result: str
    application_result: str
    has_negative_evidence: bool = False
    negative_evidence_summary: Optional[str] = None
    is_explicit_tender_citation: bool = False
    qco_status: str
    dependency_count: int = 0
    designation_reason: str


class StandardDecisionSummaryRead(BaseModel):
    primary_standard: Optional[StandardDecisionItemRead] = None
    alternative_candidates: List[StandardDecisionItemRead] = Field(default_factory=list)
    possibly_applicable: List[StandardDecisionItemRead] = Field(default_factory=list)
    not_applicable: List[StandardDecisionItemRead] = Field(default_factory=list)
    insufficient_evidence: List[StandardDecisionItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Edition & Currentness Summary
# ---------------------------------------------------------------------------

class EditionCurrentnessItemRead(BaseModel):
    standard_code: str
    standard_family: str
    edition: str
    edition_status: str
    amendments_count: int = 0
    active_amendments: List[str] = Field(default_factory=list)
    superseded_by: Optional[str] = None
    is_withdrawn: bool = False
    tender_citation: Optional[str] = None
    qco_edition_match: bool = False
    currentness_evidence: str


class EditionCurrentnessSummaryRead(BaseModel):
    items: List[EditionCurrentnessItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Dependency Summary
# ---------------------------------------------------------------------------

class DependencyItemRead(BaseModel):
    referenced_standard: str
    edition: Optional[str] = None
    category: str
    reference_type: str
    normative_classification: str
    depth: int
    triggering_clause: Optional[str] = None
    evidence: str
    procurement_impact: str


class DependencySummaryRead(BaseModel):
    test_methods: List[DependencyItemRead] = Field(default_factory=list)
    safety: List[DependencyItemRead] = Field(default_factory=list)
    installation: List[DependencyItemRead] = Field(default_factory=list)
    allied_products: List[DependencyItemRead] = Field(default_factory=list)
    certification_qco: List[DependencyItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# QCO & Certification Summary
# ---------------------------------------------------------------------------

class QcoCertificationItemRead(BaseModel):
    qco_name: str
    notifying_ministry: str
    standard_code: str
    edition: Optional[str] = None
    effective_date: Optional[str] = None
    certification_scheme: str
    status: str
    evidence: str
    currentness: str


class QcoCertificationSummaryRead(BaseModel):
    mandatory_qco_enforced: bool = False
    items: List[QcoCertificationItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Specification Gaps Summary
# ---------------------------------------------------------------------------

class GapSummaryItemRead(BaseModel):
    gap_id: Optional[int] = None
    gap_type: str
    severity: str
    affected_parameter: Optional[str] = None
    original_text: Optional[str] = None
    applicable_standard: Optional[str] = None
    edition: Optional[str] = None
    clause: Optional[str] = None
    evidence: Optional[str] = None
    why_it_matters: str
    suggested_clarification: Optional[str] = None
    status: str


class GapSummaryRead(BaseModel):
    total_gaps: int
    critical_gaps: List[GapSummaryItemRead] = Field(default_factory=list)
    high_gaps: List[GapSummaryItemRead] = Field(default_factory=list)
    medium_gaps: List[GapSummaryItemRead] = Field(default_factory=list)
    low_gaps: List[GapSummaryItemRead] = Field(default_factory=list)
    info_gaps: List[GapSummaryItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Traceability Report
# ---------------------------------------------------------------------------

class TraceabilityReportRead(BaseModel):
    chains: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Evidence Index
# ---------------------------------------------------------------------------

class EvidenceIndexItemRead(BaseModel):
    evidence_id: str
    source_type: str
    source_url: Optional[str] = None
    source_hash: Optional[str] = None
    provenance_id: Optional[int] = None
    standard_id: Optional[int] = None
    standard_code: Optional[str] = None
    edition_id: Optional[int] = None
    clause_id: Optional[int] = None
    clause_number: Optional[str] = None
    requirement_id: Optional[int] = None
    document_offset: Optional[str] = None
    verified_at: str
    description: str


class EvidenceIndexRead(BaseModel):
    total_entries: int
    entries: List[EvidenceIndexItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Clarification Package & Checklist
# ---------------------------------------------------------------------------

class ClarificationQuestionRead(BaseModel):
    question_number: int
    question_text: str
    reason: str
    evidence_clause: Optional[str] = None
    affected_parameter: Optional[str] = None


class ClarificationPackageRead(BaseModel):
    questions: List[ClarificationQuestionRead] = Field(default_factory=list)


class ChecklistItemRead(BaseModel):
    item_id: str
    label: str
    is_verified: bool
    category: str
    record_reference: str


class TenderReviewChecklistRead(BaseModel):
    items: List[ChecklistItemRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Procurement Review Actions
# ---------------------------------------------------------------------------

class ProcurementReviewActionRead(BaseModel):
    id: int
    run_id: int
    action_type: ActionType
    priority: ActionPriority
    description: str
    reason: str
    suggested_action: Optional[str] = None
    source_gap_id: Optional[int] = None
    affected_requirement_id: Optional[int] = None
    affected_standard_id: Optional[int] = None
    evidence: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Intelligence Run
# ---------------------------------------------------------------------------

class ProcurementIntelligenceRunRead(BaseModel):
    id: int
    specification_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    engine_version: str
    model_version: str
    status: str
    requirements_count: int
    standards_count: int
    applicable_count: int
    possible_count: int
    not_applicable_count: int
    insufficient_evidence_count: int
    gap_count: int
    critical_gap_count: int
    high_gap_count: int
    readiness_state: str
    overall_status: str
    input_hash: Optional[str] = None
    run_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# System Limitation
# ---------------------------------------------------------------------------

class SystemLimitationRead(BaseModel):
    code: str
    description: str
    boundary: str


# ---------------------------------------------------------------------------
# Consolidated Decision Package
# ---------------------------------------------------------------------------

class ProcurementDecisionPackageRead(BaseModel):
    run: ProcurementIntelligenceRunRead
    executive_summary: ExecutiveSummaryRead
    standards_summary: StandardDecisionSummaryRead
    edition_currentness: EditionCurrentnessSummaryRead
    dependencies: DependencySummaryRead
    certification_qco: QcoCertificationSummaryRead
    gaps: GapSummaryRead
    traceability: TraceabilityReportRead
    readiness: Dict[str, Any]
    actions: List[ProcurementReviewActionRead] = Field(default_factory=list)
    clarifications: ClarificationPackageRead
    checklist: TenderReviewChecklistRead
    evidence_index: EvidenceIndexRead
    system_limitations: List[SystemLimitationRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Canonical Export JSON Envelope
# ---------------------------------------------------------------------------

class ExportJsonRead(BaseModel):
    version: str = "8.0.0"
    exported_at: str
    package: ProcurementDecisionPackageRead
