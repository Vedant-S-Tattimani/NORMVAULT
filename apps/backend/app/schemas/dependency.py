"""
Pydantic schemas for Standards Dependency, Normative References, and Compliance Intelligence (Phase 5).
Adheres strictly to the principle that 'referenced' does not equal 'mandatory'.
"""

from typing import List, Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from app.models.reference import ReferenceType, ReferenceSemantics, ProcurementImpact
from app.models.certification import CertificationScheme, CertificationCurrentness


class DependencyNode(BaseModel):
    """Represents a standard node in the dependency graph."""
    standard_id: Optional[int] = None
    standard_number: str
    title: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    is_mandatory_qco: bool = False
    depth: int = 1
    edition_year: Optional[int] = None
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DependencyEdge(BaseModel):
    """Represents a directed dependency edge from source standard to target standard."""
    id: Optional[int] = None
    source_standard_id: int
    source_standard_number: str
    target_standard_id: Optional[int] = None
    target_standard_number: str
    relationship_type: ReferenceType = ReferenceType.NORMATIVE_REFERENCE
    reference_semantics: ReferenceSemantics = ReferenceSemantics.UNKNOWN
    procurement_impact: ProcurementImpact = ProcurementImpact.UNKNOWN
    referencing_clause: Optional[str] = None
    source_clause_id: Optional[int] = None
    clause_content: Optional[str] = None
    condition_text: Optional[str] = None
    triggering_condition: Optional[str] = None
    test_name: Optional[str] = None
    depth: int = 1
    is_cycle: bool = False
    provenance_id: Optional[int] = None
    provenance_source: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StandardsDependencyGraph(BaseModel):
    """Complete directed graph representation of standards dependencies and compliance linkages."""
    root_standard_id: int
    root_standard_number: str
    root_standard_title: str
    max_depth_traversed: int = 3
    total_nodes: int = 0
    total_edges: int = 0
    has_cycles: bool = False
    detected_cycles: List[List[str]] = Field(default_factory=list)
    nodes: List[DependencyNode] = Field(default_factory=list)
    edges: List[DependencyEdge] = Field(default_factory=list)
    direct_references: List[DependencyEdge] = Field(default_factory=list)
    transitive_dependencies: List[DependencyEdge] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TestMethodDependencyRead(BaseModel):
    """Structured view of a test method referenced by a standard."""
    id: Optional[int] = None
    source_standard_number: str
    target_standard_number: str
    target_standard_title: Optional[str] = None
    test_name: Optional[str] = None
    referencing_clause: Optional[str] = None
    clause_content: Optional[str] = None
    reference_semantics: ReferenceSemantics = ReferenceSemantics.UNKNOWN
    procurement_impact: ProcurementImpact = ProcurementImpact.REQUIRED_TEST
    condition_text: Optional[str] = None
    depth: int = 1
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SafetyRequirementDependencyRead(BaseModel):
    """Structured view of a safety requirement or code of practice referenced by a standard."""
    id: Optional[int] = None
    source_standard_number: str
    target_standard_number: str
    target_standard_title: Optional[str] = None
    referencing_clause: Optional[str] = None
    clause_content: Optional[str] = None
    reference_semantics: ReferenceSemantics = ReferenceSemantics.UNKNOWN
    procurement_impact: ProcurementImpact = ProcurementImpact.REQUIRED_SAFETY_CONDITION
    condition_text: Optional[str] = None
    depth: int = 1
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class InstallationPracticeDependencyRead(BaseModel):
    """Structured view of an installation practice code referenced by a standard."""
    id: Optional[int] = None
    source_standard_number: str
    target_standard_number: str
    target_standard_title: Optional[str] = None
    referencing_clause: Optional[str] = None
    clause_content: Optional[str] = None
    reference_semantics: ReferenceSemantics = ReferenceSemantics.UNKNOWN
    procurement_impact: ProcurementImpact = ProcurementImpact.REQUIRED_INSTALLATION_CONDITION
    condition_text: Optional[str] = None
    depth: int = 1
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AlliedProductDependencyRead(BaseModel):
    """Structured view of an allied or complementary product standard."""
    id: Optional[int] = None
    source_standard_number: str
    target_standard_number: str
    target_standard_title: Optional[str] = None
    referencing_clause: Optional[str] = None
    clause_content: Optional[str] = None
    reference_semantics: ReferenceSemantics = ReferenceSemantics.UNKNOWN
    procurement_impact: ProcurementImpact = ProcurementImpact.REQUIRED_SPECIFICATION
    condition_text: Optional[str] = None
    depth: int = 1
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CertificationComplianceRead(BaseModel):
    """Verified BIS certification scheme or statutory Quality Control Order (QCO)."""
    id: Optional[int] = None
    standard_id: int
    standard_number: str
    scheme: CertificationScheme = CertificationScheme.ISI_MARK_SCHEME_I
    is_mandatory_qco: bool = False
    qco_order_number: Optional[str] = None
    notifying_ministry: Optional[str] = None
    notification_date: Optional[date] = None
    enforcement_date: Optional[date] = None
    currentness_status: CertificationCurrentness = CertificationCurrentness.CURRENTNESS_UNCERTAIN
    applicable_product_category: Optional[str] = None
    verification_source: Optional[str] = None
    scope_condition: Optional[str] = None
    provenance_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProcurementComplianceOverview(BaseModel):
    """Consolidated compliance, reference, and QCO overview for an applicable standard."""
    standard_id: int
    standard_number: str
    standard_title: str
    graph: StandardsDependencyGraph
    test_methods: List[TestMethodDependencyRead] = Field(default_factory=list)
    safety_requirements: List[SafetyRequirementDependencyRead] = Field(default_factory=list)
    installation_practices: List[InstallationPracticeDependencyRead] = Field(default_factory=list)
    allied_products: List[AlliedProductDependencyRead] = Field(default_factory=list)
    certifications: List[CertificationComplianceRead] = Field(default_factory=list)
    has_mandatory_qco: bool = False
    qco_warning: Optional[str] = None
    summary: str

    model_config = ConfigDict(from_attributes=True)
