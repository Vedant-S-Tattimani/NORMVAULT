"""
Aggregated domain models for NORMVAULT.
"""

from app.models.standard import IndianStandard, StandardEdition, Amendment, StandardStatus, EditionStatus
from app.models.provenance import ProvenanceRecord, SourceType
from app.models.clause import Clause
from app.models.reference import NormativeReference, ReferenceType, ReferenceSemantics, ProcurementImpact
from app.models.product import ProductCategory, Product
from app.models.requirement import (
    ProcurementSpecification,
    Requirement,
    TechnicalParameter,
    RequirementType,
    RequirementExtractionStatus,
    RequirementEvidence,
)
from app.models.document import Document, DocumentProcessingState
from app.models.certification import CertificationRequirement, CertificationScheme, CertificationCurrentness
from app.models.gap import (
    SpecificationGap,
    GapType,
    GapSeverity,
    ReadinessState,
    CompletenessCategory,
    CoverageStatus,
    ProcurementReadinessAssessment,
)
from app.models.recommendation import (
    SpecificationAnalysis,
    Recommendation,
    RecommendationEvidence,
    ConfidenceLevel,
)
from app.models.retrieval import (
    StandardIndexEntry,
    RetrievalRun,
    RetrievalCandidate,
    RetrievalEvidence,
    RetrievalRunStatus,
    EvidenceType,
)
from app.models.applicability import (
    ApplicabilityOutcome,
    AbstentionReason,
    MatchLevel,
    ConflictSeverity,
    ApplicabilityRun,
    ApplicabilityAssessment,
    AssessmentEvidence,
)
from app.models.intelligence import (
    ProcurementIntelligenceRun,
    ProcurementReviewAction,
    ActionPriority,
    ActionType,
    PackageViewType,
)

__all__ = [
    "ProvenanceRecord",
    "SourceType",
    "IndianStandard",
    "StandardEdition",
    "Amendment",
    "StandardStatus",
    "EditionStatus",
    "Clause",
    "NormativeReference",
    "ReferenceType",
    "ReferenceSemantics",
    "ProcurementImpact",
    "ProductCategory",
    "Product",
    "ProcurementSpecification",
    "Requirement",
    "TechnicalParameter",
    "RequirementType",
    "RequirementExtractionStatus",
    "RequirementEvidence",
    "Document",
    "DocumentProcessingState",
    "CertificationRequirement",
    "CertificationScheme",
    "CertificationCurrentness",
    "SpecificationAnalysis",
    "Recommendation",
    "RecommendationEvidence",
    "SpecificationGap",
    "GapType",
    "GapSeverity",
    "ReadinessState",
    "CompletenessCategory",
    "CoverageStatus",
    "ProcurementReadinessAssessment",
    "ConfidenceLevel",
    "StandardIndexEntry",
    "RetrievalRun",
    "RetrievalCandidate",
    "RetrievalEvidence",
    "RetrievalRunStatus",
    "EvidenceType",
    "ApplicabilityOutcome",
    "AbstentionReason",
    "MatchLevel",
    "ConflictSeverity",
    "ApplicabilityRun",
    "ApplicabilityAssessment",
    "AssessmentEvidence",
    "ProcurementIntelligenceRun",
    "ProcurementReviewAction",
    "ActionPriority",
    "ActionType",
    "PackageViewType",
]
