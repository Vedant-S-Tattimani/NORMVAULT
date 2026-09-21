"""
SQLAlchemy domain models for Procurement Intelligence Runs and Review Actions (Phase 8).
"""

from datetime import datetime
import enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ActionPriority(str, enum.Enum):
    """
    Deterministic priority for procurement review actions.
    """
    BLOCKING = "BLOCKING"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ActionType(str, enum.Enum):
    """
    Specific categories of procurement review actions.
    """
    CLARIFY_REQUIREMENT = "CLARIFY_REQUIREMENT"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"
    SPECIFY_PARAMETER = "SPECIFY_PARAMETER"
    VERIFY_STANDARD_EDITION = "VERIFY_STANDARD_EDITION"
    VERIFY_CURRENTNESS = "VERIFY_CURRENTNESS"
    REVIEW_AMENDMENT = "REVIEW_AMENDMENT"
    VERIFY_TEST_METHOD = "VERIFY_TEST_METHOD"
    VERIFY_SAFETY_REQUIREMENT = "VERIFY_SAFETY_REQUIREMENT"
    VERIFY_INSTALLATION_REQUIREMENT = "VERIFY_INSTALLATION_REQUIREMENT"
    VERIFY_CERTIFICATION = "VERIFY_CERTIFICATION"
    VERIFY_QCO = "VERIFY_QCO"
    REVIEW_UNCERTAIN_EVIDENCE = "REVIEW_UNCERTAIN_EVIDENCE"


class PackageViewType(str, enum.Enum):
    """
    Supported export and projection views of the decision package.
    """
    FULL_ANALYSIS = "FULL_ANALYSIS"
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
    TECHNICAL_REVIEW = "TECHNICAL_REVIEW"
    REGULATORY_REVIEW = "REGULATORY_REVIEW"
    TRACEABILITY_REPORT = "TRACEABILITY_REPORT"
    CLARIFICATION_LIST = "CLARIFICATION_LIST"


class ProcurementIntelligenceRun(Base):
    """
    Represents an immutable, reproducible intelligence analysis run for a procurement specification.
    """
    __tablename__ = "procurement_intelligence_runs"

    id = Column(Integer, primary_key=True, index=True)
    specification_id = Column(
        Integer,
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    engine_version = Column(String(32), default="8.0.0", nullable=False)
    model_version = Column(String(32), default="deterministic-v1.0", nullable=False)
    status = Column(String(32), default="COMPLETED", nullable=False, index=True)
    
    # Quantitative summary counters
    requirements_count = Column(Integer, default=0, nullable=False)
    standards_count = Column(Integer, default=0, nullable=False)
    applicable_count = Column(Integer, default=0, nullable=False)
    possible_count = Column(Integer, default=0, nullable=False)
    not_applicable_count = Column(Integer, default=0, nullable=False)
    insufficient_evidence_count = Column(Integer, default=0, nullable=False)
    gap_count = Column(Integer, default=0, nullable=False)
    critical_gap_count = Column(Integer, default=0, nullable=False)
    high_gap_count = Column(Integer, default=0, nullable=False)
    
    # State machine and status
    readiness_state = Column(String(64), nullable=False)
    overall_status = Column(String(64), default="ANALYSIS_COMPLETE", nullable=False)
    
    # Auditability & Idempotency
    input_hash = Column(String(64), nullable=True, index=True)
    run_metadata = Column(JSON, nullable=True)

    # Relationships
    specification = relationship("ProcurementSpecification", backref="intelligence_runs")
    actions = relationship(
        "ProcurementReviewAction",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="ProcurementReviewAction.id",
    )

    def __repr__(self) -> str:
        return f"<ProcurementIntelligenceRun(id={self.id}, spec_id={self.specification_id}, status={self.status})>"


class ProcurementReviewAction(Base):
    """
    Evidence-backed review and clarification action items derived from the intelligence package.
    """
    __tablename__ = "procurement_review_actions"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(
        Integer,
        ForeignKey("procurement_intelligence_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)
    priority = Column(SQLEnum(ActionPriority), nullable=False, index=True)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=True)
    
    source_gap_id = Column(
        Integer,
        ForeignKey("specification_gaps.id", ondelete="SET NULL"),
        nullable=True,
    )
    affected_requirement_id = Column(
        Integer,
        ForeignKey("spec_requirements.id", ondelete="SET NULL"),
        nullable=True,
    )
    affected_standard_id = Column(
        Integer,
        ForeignKey("indian_standards.id", ondelete="SET NULL"),
        nullable=True,
    )
    evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    run = relationship("ProcurementIntelligenceRun", back_populates="actions")
    source_gap = relationship("SpecificationGap")
    affected_requirement = relationship("Requirement")
    affected_standard = relationship("IndianStandard")

    def __repr__(self) -> str:
        return f"<ProcurementReviewAction(id={self.id}, type={self.action_type}, priority={self.priority})>"
