from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.reference import ReferenceType

class IngestClause(BaseModel):
    clause_number: str
    content: str
    children: List["IngestClause"] = []

class IngestAmendment(BaseModel):
    amendment_number: int
    summary: str
    is_effective: bool

class IngestEdition(BaseModel):
    edition_number: int
    year: int
    is_current: bool
    clauses: List[IngestClause] = []
    amendments: List[IngestAmendment] = []

class IngestReference(BaseModel):
    target_standard_number: str
    relationship_type: ReferenceType
    referencing_clause: Optional[str] = None

class IngestStandard(BaseModel):
    source_url: str
    source_hash: str
    standard_number: str
    title: str
    scope: Optional[str] = None
    division_code: Optional[str] = None
    status: str
    is_mandatory_qco: bool = False
    qco_reference: Optional[str] = None
    editions: List[IngestEdition] = []
    normative_references: List[IngestReference] = []

    model_config = ConfigDict(extra="ignore")
