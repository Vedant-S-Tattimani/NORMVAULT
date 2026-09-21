"""
Pydantic schemas for Standard Editions, Amendments, Currentness Evaluations, and Timeline History.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CurrentnessResolutionStatus(str, Enum):
    """System resolution state for an edition's legal and technical currentness."""
    CURRENT = "CURRENT"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"
    CURRENTNESS_UNCERTAIN = "CURRENTNESS_UNCERTAIN"
    EDITION_UNSPECIFIED = "EDITION_UNSPECIFIED"
    CONFLICTING_EDITION_REFERENCES = "CONFLICTING_EDITION_REFERENCES"


class CitationType(str, Enum):
    """Categorization of tender citation syntax."""
    EXPLICIT_WITH_YEAR_AND_AMENDMENT = "EXPLICIT_WITH_YEAR_AND_AMENDMENT"
    EXPLICIT_WITH_YEAR = "EXPLICIT_WITH_YEAR"
    UNSPECIFIED_YEAR = "UNSPECIFIED_YEAR"
    CONFLICTING = "CONFLICTING"


class AmendmentChainItem(BaseModel):
    """Individual amendment entry in the sequential modification chain of an edition."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    amendment_number: int
    title: Optional[str] = None
    issue_date: Optional[str] = None
    effective_date: Optional[str] = None
    summary: str
    affected_clauses: Optional[str] = None
    old_clause_text: Optional[str] = None
    new_clause_text: Optional[str] = None
    clause_impact_summary: Optional[str] = None
    is_effective: bool = True
    provenance_id: Optional[int] = None


class EditionRead(BaseModel):
    """Detailed metadata for a specific standard edition."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard_id: int
    edition_number: int
    year: int
    status: str
    is_current: bool
    reaffirmation_year: Optional[int] = None
    superseded_date: Optional[str] = None
    superseded_by_edition_id: Optional[int] = None
    superseded_by_standard_number: Optional[str] = None
    supersession_reason: Optional[str] = None
    supersession_evidence: Optional[str] = None
    withdrawal_date: Optional[str] = None
    withdrawal_reason: Optional[str] = None
    withdrawal_evidence: Optional[str] = None
    amendments: List[AmendmentChainItem] = []
    provenance_id: Optional[int] = None


class TenderCitationExtraction(BaseModel):
    """Result of parsing procurement tender text for standard numbers, editions, and amendments."""
    standard_number: str
    edition_year: Optional[int] = None
    amendment_number: Optional[int] = None
    raw_citation: str
    citation_type: CitationType
    source_clause_or_section: Optional[str] = None


class CurrentnessEvaluation(BaseModel):
    """Comprehensive evaluation of currentness, supersession, amendments, and procurement warning."""
    model_config = ConfigDict(from_attributes=True)

    status: CurrentnessResolutionStatus
    standard_number: str
    resolved_edition_year: Optional[int] = None
    cited_edition_year: Optional[int] = None
    cited_amendment_number: Optional[int] = None
    has_amendments: bool = False
    active_amendments_count: int = 0
    is_superseded: bool = False
    superseded_by: Optional[str] = None
    supersession_reason: Optional[str] = None
    is_withdrawn: bool = False
    withdrawal_reason: Optional[str] = None
    qco_edition_match: Optional[bool] = None
    qco_edition_mandate: Optional[int] = None
    technical_applicability: Optional[str] = None
    edition_applicability: str
    evidence_summary: str
    procurement_warning: Optional[str] = None
    provenance_id: Optional[int] = None


class StandardTimelineEvent(BaseModel):
    """Chronological event in the lifecycle of a standard family or edition."""
    year_or_date: str
    event_type: str  # PUBLICATION, AMENDMENT, REAFFIRMATION, SUPERSEDED, WITHDRAWN, QCO_ENFORCED
    title: str
    description: str
    evidence: str


class StandardHistoryRead(BaseModel):
    """Aggregated chronological lifecycle and timeline of a standard."""
    standard_number: str
    title: str
    timeline: List[StandardTimelineEvent] = []
    editions: List[EditionRead] = []
    total_amendments: int = 0
