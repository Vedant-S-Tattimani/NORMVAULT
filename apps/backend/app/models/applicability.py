"""
Domain models for the Applicability Analysis and Standards Recommendation Engine.
Tracks applicability runs, candidate assessments, multi-factor evidence, conflicts, and missing information.

CRITICAL BOUNDARIES (Phase 4):
- Semantic similarity is evidence for retrieval, NOT evidence of legal/technical applicability by itself.
- Produces APPLICABLE, POSSIBLY_APPLICABLE, NOT_APPLICABLE, or INSUFFICIENT_EVIDENCE (abstention).
- Transparent component evidence without opaque "AI confidence %".
- Negative evidence (scope exclusions, parameter limits, application mismatch) has priority over retrieval similarity.
"""

from enum import Enum
from typing import List, Optional, Any, Dict
from sqlalchemy import String, Text, Boolean, Integer, Float, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ApplicabilityOutcome(str, Enum):
    APPLICABLE = "APPLICABLE"
    POSSIBLY_APPLICABLE = "POSSIBLY_APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AbstentionReason(str, Enum):
    NONE = "NONE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    MULTIPLE_PLAUSIBLE_STANDARDS = "MULTIPLE_PLAUSIBLE_STANDARDS"
    SCOPE_UNCLEAR = "SCOPE_UNCLEAR"
    MISSING_REQUIREMENT_INFORMATION = "MISSING_REQUIREMENT_INFORMATION"
    NO_APPLICABLE_CANDIDATE_FOUND = "NO_APPLICABLE_CANDIDATE_FOUND"


class MatchLevel(str, Enum):
    EXACT = "EXACT"
    CATEGORY = "CATEGORY"
    AMBIGUOUS = "AMBIGUOUS"
    MISMATCH = "MISMATCH"
    UNCERTAIN = "UNCERTAIN"
    COMPATIBLE = "COMPATIBLE"
    CONFLICT = "CONFLICT"
    UNCHECKED = "UNCHECKED"
    NOT_SPECIFIED = "NOT_SPECIFIED"


class ConflictSeverity(str, Enum):
    FATAL = "FATAL"           # Direct contradiction or scope exclusion -> NOT_APPLICABLE
    WARNING = "WARNING"       # Ambiguity, unverified edition, or partial parameter coverage
    INFORMATIONAL = "INFORMATIONAL" # Non-blocking advisory note


class ApplicabilityRun(Base, TimestampMixin):
    """
    Auditable execution record of an applicability assessment run.
    Links requirement/specification input, Phase 3 retrieval run, and engine/policy metadata.
    """
    __tablename__ = "applicability_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"), nullable=True, index=True
    )
    requirement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("spec_requirements.id", ondelete="CASCADE"), nullable=True, index=True
    )
    retrieval_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("retrieval_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    engine_version: Mapped[str] = mapped_column(String(32), default="v1.0", nullable=False)
    policy_version: Mapped[str] = mapped_column(String(32), default="2026.1", nullable=False)
    llm_model: Mapped[Optional[str]] = mapped_column(String(128), default="deterministic-grounded-v1", nullable=True)

    # Metric summaries for audit
    total_candidates_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applicable_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    possibly_applicable_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_applicable_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    abstained_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    requirement: Mapped[Optional["Requirement"]] = relationship("Requirement")
    specification: Mapped[Optional["ProcurementSpecification"]] = relationship("ProcurementSpecification")
    retrieval_run: Mapped[Optional["RetrievalRun"]] = relationship("RetrievalRun")
    assessments: Mapped[List["ApplicabilityAssessment"]] = relationship(
        "ApplicabilityAssessment", back_populates="run", cascade="all, delete-orphan", order_by="ApplicabilityAssessment.is_primary.desc()"
    )


class ApplicabilityAssessment(Base, TimestampMixin):
    """
    Detailed evidence-based applicability determination for a single candidate standard.
    Exposes transparent component evidence, positive reasons, negative conflicts, and missing information.
    """
    __tablename__ = "applicability_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("applicability_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("retrieval_candidates.id", ondelete="SET NULL"), nullable=True, index=True
    )
    standard_id: Mapped[int] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True
    )

    outcome: Mapped[ApplicabilityOutcome] = mapped_column(
        SQLEnum(ApplicabilityOutcome), default=ApplicabilityOutcome.INSUFFICIENT_EVIDENCE, nullable=False
    )
    abstention_reason: Mapped[AbstentionReason] = mapped_column(
        SQLEnum(AbstentionReason), default=AbstentionReason.NONE, nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    primary_designation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Aggregate applicability score: transparent multi-criteria evidence alignment index (0.0 to 1.0)
    # NOT a statistical probability or opaque confidence.
    applicability_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    summary_rationale: Mapped[str] = mapped_column(Text, nullable=False)

    # Component evidence metrics (scope_match, product_match, parameter_match, application_match, explicit_ref, etc.)
    component_evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Structured lists:
    # reasons: [{"title": "...", "description": "...", "is_positive": True}]
    reasons: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    # conflicts: [{"conflict_type": "...", "description": "...", "severity": "FATAL", "tender_claim": "...", "standard_fact": "..."}]
    conflicts: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    # missing_information: [{"field_name": "...", "why_it_matters": "...", "impact": "BLOCKING"}]
    missing_information: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Relationships
    run: Mapped["ApplicabilityRun"] = relationship("ApplicabilityRun", back_populates="assessments")
    candidate: Mapped[Optional["RetrievalCandidate"]] = relationship("RetrievalCandidate")
    standard: Mapped["IndianStandard"] = relationship("IndianStandard")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition")
    evidence_items: Mapped[List["AssessmentEvidence"]] = relationship(
        "AssessmentEvidence", back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentEvidence(Base, TimestampMixin):
    """
    Granular evidence backing an applicability decision.
    Points to verified standard scope text, clauses, parameters, or explicit tender citations.
    """
    __tablename__ = "assessment_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("applicability_assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(
        String(64), default="SCOPE_EXCERPT", nullable=False
    )
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    clause_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_clauses.id", ondelete="SET NULL"), nullable=True
    )
    clause_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_supporting: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    relevance_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    assessment: Mapped["ApplicabilityAssessment"] = relationship("ApplicabilityAssessment", back_populates="evidence_items")
    clause: Mapped[Optional["Clause"]] = relationship("Clause")
