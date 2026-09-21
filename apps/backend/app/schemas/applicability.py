"""
Pydantic schemas for the Applicability Analysis and Standards Recommendation Engine.
Provides strongly typed models for requests, assessments, component evidence, conflicts, and missing information.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.applicability import (
    ApplicabilityOutcome,
    AbstentionReason,
    ConflictSeverity,
)


class ComponentEvidenceSchema(BaseModel):
    """
    Transparent component evidence breakdown.
    Replaces ambiguous 'AI confidence' with traceable signals.
    """
    scope_match: str = Field(..., description="EXACT, PARTIAL, MISMATCH, or UNCERTAIN")
    product_match: str = Field(..., description="EXACT, CATEGORY, AMBIGUOUS, or MISMATCH")
    application_match: str = Field(..., description="COMPATIBLE, MISMATCH, or UNCERTAIN")
    parameter_match: str = Field(..., description="COMPATIBLE, CONFLICT, UNCHECKED, or NOT_SPECIFIED")
    explicit_reference: bool = Field(False, description="Tender explicitly cites standard")
    exclusion_match: bool = Field(False, description="Standard scope explicitly excludes the product/condition")
    negative_evidence_count: int = Field(0, description="Total fatal and warning conflicts")
    retrieval_signals: Optional[Dict[str, float]] = Field(
        None, description="Retrieval component signals (lexical, semantic, metadata, rerank, fused)"
    )
    evidence_quality: str = Field("MEDIUM", description="HIGH, MEDIUM, or LOW")

    model_config = ConfigDict(from_attributes=True)


class AssessmentReasonSchema(BaseModel):
    """Structured positive or contextual justification."""
    title: str
    description: str
    is_positive: bool = True
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentConflictSchema(BaseModel):
    """
    Identified conflict or negative evidence disqualifying or degrading candidate applicability.
    """
    conflict_type: str = Field(..., description="SCOPE_EXCLUSION, PARAMETER_VIOLATION, APPLICATION_MISMATCH, etc.")
    description: str
    severity: ConflictSeverity = ConflictSeverity.WARNING
    tender_claim: Optional[str] = None
    standard_fact: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MissingInformationSchema(BaseModel):
    """
    Procurement detail required to make a definitive applicability determination.
    """
    field_name: str
    why_it_matters: str
    impact: str = Field("BLOCKING", description="BLOCKING or NON_BLOCKING")
    suggested_clarification: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentEvidenceRead(BaseModel):
    """Verifiable source quote or clause citation."""
    id: Optional[int] = None
    evidence_type: str
    snippet: str
    clause_number: Optional[str] = None
    is_supporting: bool = True
    relevance_weight: float = 1.0

    model_config = ConfigDict(from_attributes=True)


class ApplicabilityAssessmentRead(BaseModel):
    """
    Comprehensive applicability decision for a candidate Indian Standard.
    """
    id: Optional[int] = None
    standard_id: int
    standard_number: str
    title: str
    edition_year: Optional[int] = None
    status: str = "ACTIVE"
    division_code: Optional[str] = None
    is_mandatory_qco: bool = False
    qco_reference: Optional[str] = None
    outcome: ApplicabilityOutcome
    abstention_reason: AbstentionReason = AbstentionReason.NONE
    is_primary: bool = False
    primary_designation_reason: Optional[str] = None
    applicability_score: float = Field(
        ..., description="Multi-criteria evidence alignment index (0.0 to 1.0). Not probability."
    )
    summary_rationale: str
    component_evidence: ComponentEvidenceSchema
    reasons: List[AssessmentReasonSchema] = Field(default_factory=list)
    conflicts: List[AssessmentConflictSchema] = Field(default_factory=list)
    missing_information: List[MissingInformationSchema] = Field(default_factory=list)
    evidence_items: List[AssessmentEvidenceRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ApplicabilityRunRead(BaseModel):
    """
    Persisted execution run of applicability analysis.
    """
    id: int
    requirement_id: Optional[int] = None
    specification_id: Optional[int] = None
    retrieval_run_id: Optional[int] = None
    status: str
    engine_version: str
    policy_version: str
    llm_model: Optional[str] = None
    total_candidates_analyzed: int
    applicable_count: int
    possibly_applicable_count: int
    not_applicable_count: int
    abstained_count: int
    execution_duration_ms: float
    assessments: List[ApplicabilityAssessmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ApplicabilityAnalyzeRequest(BaseModel):
    """
    Configuration payload for triggering applicability analysis.
    """
    top_k: int = Field(5, ge=1, le=50, description="Max candidates to retrieve and evaluate")
    division_code: Optional[str] = Field(None, description="BIS Division code filter (e.g. ETD, CED)")
    include_withdrawn: bool = Field(False, description="Whether to consider withdrawn standards")
    require_exact_product: bool = Field(False, description="Enforce exact product domain match")


class SpecificationApplicabilityRead(BaseModel):
    """
    Multi-requirement consolidated applicability analysis across an entire procurement tender.
    """
    specification_id: int
    title: str
    status: str
    requirement_runs: List[ApplicabilityRunRead] = Field(default_factory=list)
    primary_standards: List[ApplicabilityAssessmentRead] = Field(default_factory=list)
    alternative_candidates: List[ApplicabilityAssessmentRead] = Field(default_factory=list)
    unresolved_gaps: List[MissingInformationSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
