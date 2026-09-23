"""
Domain models for Procurement Specification Gap Analysis and Compliance Readiness.
Tracks identified gaps, ambiguities, contradictions, missing parameters, test methods, safety requirements,
and overall specification readiness assessments.
"""

from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.recommendation import SpecificationAnalysis
    from app.models.requirement import ProcurementSpecification, Requirement
    from app.models.standard import IndianStandard, StandardEdition


class GapType(str, Enum):
    MISSING_PARAMETER = "MISSING_PARAMETER"
    AMBIGUOUS_REQUIREMENT = "AMBIGUOUS_REQUIREMENT"
    CONFLICTING_REQUIREMENTS = "CONFLICTING_REQUIREMENTS"
    NON_MEASURABLE_REQUIREMENT = "NON_MEASURABLE_REQUIREMENT"
    MISSING_ACCEPTANCE_CRITERION = "MISSING_ACCEPTANCE_CRITERION"
    MISSING_TEST_METHOD = "MISSING_TEST_METHOD"
    MISSING_SAFETY_REQUIREMENT = "MISSING_SAFETY_REQUIREMENT"
    MISSING_INSTALLATION_REQUIREMENT = "MISSING_INSTALLATION_REQUIREMENT"
    MISSING_NORMATIVE_REFERENCE = "MISSING_NORMATIVE_REFERENCE"
    MISSING_CERTIFICATION_REQUIREMENT = "MISSING_CERTIFICATION_REQUIREMENT"
    MISSING_INTERFACE_REQUIREMENT = "MISSING_INTERFACE_REQUIREMENT"
    EDITION_INCONSISTENCY = "EDITION_INCONSISTENCY"
    AMENDMENT_IMPACT_GAP = "AMENDMENT_IMPACT_GAP"
    UNVERIFIABLE_CLAIM = "UNVERIFIABLE_CLAIM"
    UNRESOLVED_APPLICABILITY = "UNRESOLVED_APPLICABILITY"


class GapSeverity(str, Enum):
    CRITICAL = "CRITICAL"  # Contradictions, missing parameters required for applicability/acceptance, mandatory QCO violation
    HIGH = "HIGH"          # Missing test methods, missing mandatory safety requirements, superseded edition
    MEDIUM = "MEDIUM"      # Ambiguous requirements, missing acceptance criterion, missing installation code
    LOW = "LOW"            # Allied product interface gap, unindexed amendment impact
    INFO = "INFO"          # Advisory or informative completeness gap
    # Backward compatibility with Phase 0
    WARNING = "WARNING"
    INFORMATIONAL = "INFORMATIONAL"


class ReadinessState(str, Enum):
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    TECHNICAL_GAPS_PRESENT = "TECHNICAL_GAPS_PRESENT"
    CRITICAL_INFORMATION_MISSING = "CRITICAL_INFORMATION_MISSING"
    UNRESOLVED_STANDARD_CONTEXT = "UNRESOLVED_STANDARD_CONTEXT"


class CompletenessCategory(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    PARTIALLY_COMPLETE = "PARTIALLY_COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    UNRESOLVED = "UNRESOLVED"


class CoverageStatus(str, Enum):
    COVERED = "COVERED"
    MISSING = "MISSING"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    REVIEW = "REVIEW"


class SpecificationGap(Base, TimestampMixin):
    """
    Represents an individual technical gap, ambiguity, contradiction, or missing requirement
    identified within a procurement specification.
    """
    __tablename__ = "specification_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"), nullable=True, index=True
    )
    requirement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("spec_requirements.id", ondelete="CASCADE"), nullable=True, index=True
    )
    gap_type: Mapped[GapType] = mapped_column(
        SQLEnum(GapType), default=GapType.MISSING_PARAMETER, nullable=False, index=True
    )
    severity: Mapped[GapSeverity] = mapped_column(
        SQLEnum(GapSeverity), default=GapSeverity.MEDIUM, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="DETECTED", nullable=False) # DETECTED, RESOLVED, WAIVED

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_clarification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remediation_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Phase 0 compat

    affected_parameter: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    current_value: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    expected_information: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    affected_standard_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="SET NULL"), nullable=True
    )
    affected_edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True
    )
    affected_clause: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    evidence_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="STANDARD_SPECIFICATION", nullable=False)
    provenance_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    specification: Mapped[Optional["ProcurementSpecification"]] = relationship("ProcurementSpecification")
    requirement: Mapped[Optional["Requirement"]] = relationship("Requirement")
    standard: Mapped[Optional["IndianStandard"]] = relationship("IndianStandard")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition")


class ProcurementReadinessAssessment(Base, TimestampMixin):
    """
    Aggregated readiness assessment evaluating whether a procurement specification is
    sufficiently complete, unambiguous, and aligned with applicable standards for tender publication.
    """
    __tablename__ = "procurement_readiness_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[int] = mapped_column(
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    readiness_state: Mapped[ReadinessState] = mapped_column(
        SQLEnum(ReadinessState), nullable=False, index=True
    )
    completeness_category: Mapped[CompletenessCategory] = mapped_column(
        SQLEnum(CompletenessCategory), nullable=False
    )

    total_expected_elements: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    elements_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    elements_missing: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    elements_ambiguous: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    elements_conflicting: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    critical_gaps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_gaps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_gaps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_gaps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    summary_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    specification: Mapped["ProcurementSpecification"] = relationship("ProcurementSpecification")
