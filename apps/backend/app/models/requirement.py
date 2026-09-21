"""
Domain models for Procurement Specifications, Extracted Requirements, and Parameters.
"""

from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class RequirementType(str, Enum):
    MATERIAL = "MATERIAL"
    DIMENSIONAL = "DIMENSIONAL"
    MECHANICAL = "MECHANICAL"
    CHEMICAL = "CHEMICAL"
    TESTING = "TESTING"
    SAFETY = "SAFETY"
    CERTIFICATION = "CERTIFICATION"
    PACKAGING_MARKING = "PACKAGING_MARKING"
    WORKMANSHIP = "WORKMANSHIP"


class RequirementExtractionStatus(str, Enum):
    EXPLICIT = "EXPLICIT"
    INFERRED = "INFERRED"
    UNCERTAIN = "UNCERTAIN"
    UNRESOLVED = "UNRESOLVED"


class ProcurementSpecification(Base, TimestampMixin):
    """
    Represents an ingested procurement tender, schedule of requirements, or technical spec.
    """
    __tablename__ = "procurement_specifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    tender_reference: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    target_product_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    source_format: Mapped[str] = mapped_column(String(32), default="TEXT", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False) # e.g. EXTRACTING, COMPLETED

    # Relationships
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="specifications")
    requirements: Mapped[List["Requirement"]] = relationship(
        "Requirement", back_populates="specification", cascade="all, delete-orphan"
    )
    analyses: Mapped[List["SpecificationAnalysis"]] = relationship(
        "SpecificationAnalysis", back_populates="specification", cascade="all, delete-orphan"
    )


class Requirement(Base, TimestampMixin):
    """
    An individual extracted technical clause or requirement from the specification.
    """
    __tablename__ = "spec_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[int] = mapped_column(
        ForeignKey("procurement_specifications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clause_reference: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    requirement_type: Mapped[RequirementType] = mapped_column(
        SQLEnum(RequirementType), default=RequirementType.MATERIAL, nullable=False
    )
    extraction_status: Mapped[RequirementExtractionStatus] = mapped_column(
        SQLEnum(RequirementExtractionStatus), default=RequirementExtractionStatus.EXPLICIT, nullable=False
    )
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    specification: Mapped["ProcurementSpecification"] = relationship(
        "ProcurementSpecification", back_populates="requirements"
    )
    parameters: Mapped[List["TechnicalParameter"]] = relationship(
        "TechnicalParameter", back_populates="requirement", cascade="all, delete-orphan"
    )
    evidence: Mapped[Optional["RequirementEvidence"]] = relationship(
        "RequirementEvidence", back_populates="requirement", uselist=False, cascade="all, delete-orphan"
    )


class RequirementEvidence(Base, TimestampMixin):
    """
    Evidence tracing a Requirement back to its specific location in a Document or text block.
    """
    __tablename__ = "requirement_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("spec_requirements.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_heading: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    block_identifier: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    start_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    requirement: Mapped["Requirement"] = relationship("Requirement", back_populates="evidence")


class TechnicalParameter(Base, TimestampMixin):
    """
    Atomic quantitative or qualitative parameter.
    E.g., Parameter: 'Density', Operator: '>=', Value: '940', Unit: 'kg/m3', Test: 'IS 2530'.
    Preserves original verbatim value, normalized value, unit, and operator/range.
    """
    __tablename__ = "technical_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("spec_requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    original_value: Mapped[str] = mapped_column(String(128), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(128), nullable=False)
    target_value: Mapped[str] = mapped_column(String(128), nullable=False)
    operator: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    tolerance: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    test_method_standard: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    requirement: Mapped["Requirement"] = relationship("Requirement", back_populates="parameters")

