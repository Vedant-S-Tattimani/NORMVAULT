"""
Pydantic schemas for Standards, Editions, Amendments, and References.
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.standard import StandardStatus
from app.models.reference import ReferenceType
from app.models.certification import CertificationScheme


class AmendmentRead(BaseModel):
    id: int
    amendment_number: int
    issue_date: Optional[date] = None
    summary: str
    affected_clauses: Optional[str] = None
    is_effective: bool

    model_config = ConfigDict(from_attributes=True)


class StandardEditionRead(BaseModel):
    id: int
    edition_number: int
    year: int
    is_current: bool
    reaffirmation_year: Optional[int] = None
    superseded_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class NormativeReferenceRead(BaseModel):
    id: int
    source_standard_id: int
    target_standard_id: Optional[int] = None
    target_standard_number: str
    relationship_type: ReferenceType
    referencing_clause: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CertificationRequirementRead(BaseModel):
    id: int
    scheme: CertificationScheme
    is_mandatory_qco: bool
    qco_order_number: Optional[str] = None
    notifying_ministry: Optional[str] = None
    enforcement_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class IndianStandardRead(BaseModel):
    id: int
    standard_number: str
    title: str
    scope: Optional[str] = None
    division_code: Optional[str] = None
    department: Optional[str] = None
    status: StandardStatus
    is_mandatory_qco: bool
    qco_reference: Optional[str] = None
    editions: List[StandardEditionRead] = Field(default_factory=list)
    amendments: List[AmendmentRead] = Field(default_factory=list)
    outgoing_references: List[NormativeReferenceRead] = Field(default_factory=list)
    certifications: List[CertificationRequirementRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class StandardFilterParams(BaseModel):
    query: Optional[str] = None
    division: Optional[str] = None
    mandatory_only: bool = False
    status: Optional[StandardStatus] = None
