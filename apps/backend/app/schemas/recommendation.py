"""
Pydantic schemas for Recommendations, Evidence Snippets, and Specification Gaps.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.recommendation import ConfidenceLevel, GapSeverity
from app.schemas.standard import IndianStandardRead, StandardEditionRead


class RecommendationEvidenceRead(BaseModel):
    id: int
    requirement_id: Optional[int] = None
    clause_id: Optional[int] = None
    evidence_snippet: str
    match_score: float

    model_config = ConfigDict(from_attributes=True)


class RecommendationRead(BaseModel):
    id: int
    analysis_id: int
    standard_id: int
    edition_id: Optional[int] = None
    is_primary: bool
    role: str
    confidence: ConfidenceLevel
    relevance_score: float
    rationale: str
    standard: Optional[IndianStandardRead] = None
    edition: Optional[StandardEditionRead] = None
    evidence: List[RecommendationEvidenceRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SpecificationGapRead(BaseModel):
    id: int
    analysis_id: int
    severity: GapSeverity
    title: str
    description: str
    remediation_recommendation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SpecificationAnalysisRead(BaseModel):
    id: int
    specification_id: int
    status: str
    summary: Optional[str] = None
    created_at: datetime
    recommendations: List[RecommendationRead] = Field(default_factory=list)
    gaps: List[SpecificationGapRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
