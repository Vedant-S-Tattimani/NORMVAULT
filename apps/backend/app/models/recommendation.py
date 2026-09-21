"""
Domain models for Specification Analyses, Recommendations, Evidence, and Gaps.
Supports auditable, explainable procurement intelligence.
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, Float, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


from app.models.gap import GapSeverity, SpecificationGap


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"


class SpecificationAnalysis(Base, TimestampMixin):
    """
    State and output container for a procurement specification analysis run.
    """
    __tablename__ = "specification_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[int] = mapped_column(
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    specification: Mapped["ProcurementSpecification"] = relationship(
        "ProcurementSpecification", back_populates="analyses"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="analysis", cascade="all, delete-orphan"
    )
    gaps: Mapped[List["SpecificationGap"]] = relationship(
        "SpecificationGap", back_populates="analysis", cascade="all, delete-orphan"
    )


class Recommendation(Base, TimestampMixin):
    """
    Recommended Indian Standard for the specification, with role and explainable score.
    """
    __tablename__ = "analysis_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("specification_analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    standard_id: Mapped[int] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(64), default="PRIMARY_PRODUCT", nullable=False)
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        SQLEnum(ConfidenceLevel), default=ConfidenceLevel.HIGH, nullable=False
    )
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    analysis: Mapped["SpecificationAnalysis"] = relationship("SpecificationAnalysis", back_populates="recommendations")
    standard: Mapped["IndianStandard"] = relationship("IndianStandard")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition")
    evidence: Mapped[List["RecommendationEvidence"]] = relationship(
        "RecommendationEvidence", back_populates="recommendation", cascade="all, delete-orphan"
    )


class RecommendationEvidence(Base, TimestampMixin):
    """
    Fine-grained evidence linking a recommendation to specific tender requirement text and standard clause.
    """
    __tablename__ = "recommendation_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_recommendations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requirement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("spec_requirements.id", ondelete="SET NULL"), nullable=True
    )
    clause_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_clauses.id", ondelete="SET NULL"), nullable=True
    )
    evidence_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="evidence")



