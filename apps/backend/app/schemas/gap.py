"""
Pydantic schemas for Procurement Specification Gap Analysis and Readiness Assessment.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.gap import (
    GapType,
    GapSeverity,
    ReadinessState,
    CompletenessCategory,
    CoverageStatus,
)


class GapItemRead(BaseModel):
    """Detailed view of an individual specification gap or ambiguity."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    specification_id: int
    requirement_id: Optional[int] = None
    gap_type: GapType
    severity: GapSeverity
    status: str = "DETECTED"
    title: str
    description: str
    why_it_matters: str
    required_clarification: str
    affected_parameter: Optional[str] = None
    current_value: Optional[str] = None
    expected_information: Optional[str] = None
    affected_standard_id: Optional[int] = None
    affected_standard_number: Optional[str] = None
    affected_edition_id: Optional[int] = None
    affected_clause: Optional[str] = None
    evidence_snippet: Optional[str] = None
    source: str = "STANDARD_SPECIFICATION"
    provenance_id: Optional[int] = None


class CoverageMatrixItem(BaseModel):
    """Single row in the Standard Coverage Matrix comparing tender to applicable standard."""
    model_config = ConfigDict(from_attributes=True)

    parameter_or_topic: str
    tender_value: Optional[str] = None
    standard_requirement: str
    coverage_status: CoverageStatus
    clause_reference: Optional[str] = None
    standard_number: Optional[str] = None
    evidence_snippet: Optional[str] = None
    why_it_matters: Optional[str] = None


class TraceabilityNode(BaseModel):
    """End-to-end traceability chain node linking tender requirement to standard, dependency, and gap."""
    model_config = ConfigDict(from_attributes=True)

    requirement_id: int
    requirement_text: str
    parameter_name: Optional[str] = None
    parameter_value: Optional[str] = None
    standard_number: Optional[str] = None
    edition_year: Optional[int] = None
    clause_reference: Optional[str] = None
    normative_dependency: Optional[str] = None
    coverage_status: CoverageStatus
    associated_gap_type: Optional[GapType] = None
    gap_description: Optional[str] = None


class RequirementGapAnalysisRead(BaseModel):
    """Analysis result of gaps identified within a single requirement clause."""
    model_config = ConfigDict(from_attributes=True)

    requirement_id: int
    requirement_text: str
    gaps: List[GapItemRead] = Field(default_factory=list)
    has_critical_gaps: bool = False
    gaps_count: int = 0


class SpecificationReadinessRead(BaseModel):
    """
    Comprehensive Readiness & Gap Assessment report for an entire procurement specification.
    Includes explainable completeness counts, categorized gaps, coverage matrix, and audit summary.
    """
    model_config = ConfigDict(from_attributes=True)

    specification_id: int
    specification_title: str
    readiness_state: ReadinessState
    completeness_category: CompletenessCategory

    total_expected_elements: int = 0
    elements_present: int = 0
    elements_missing: int = 0
    elements_ambiguous: int = 0
    elements_conflicting: int = 0

    critical_gaps_count: int = 0
    high_gaps_count: int = 0
    medium_gaps_count: int = 0
    low_gaps_count: int = 0
    info_gaps_count: int = 0
    total_gaps_count: int = 0

    summary_rationale: str
    gaps: List[GapItemRead] = Field(default_factory=list)
    coverage_matrix: List[CoverageMatrixItem] = Field(default_factory=list)
    traceability: List[TraceabilityNode] = Field(default_factory=list)
    execution_duration_ms: float = 0.0
