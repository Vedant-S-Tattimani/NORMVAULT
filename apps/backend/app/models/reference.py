"""
Domain model for typed Normative References, Allied Standards, and Test Methods.
Serves as the foundation for the Standards Knowledge Graph.
"""

from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ReferenceType(str, Enum):
    NORMATIVE_REFERENCE = "NORMATIVE_REFERENCE"       # Essential normative document
    TEST_METHOD = "TEST_METHOD"                       # Specific test methodology (e.g. IS 2530)
    ALLIED_PRODUCT = "ALLIED_PRODUCT"                 # Associated or complementary product standard
    TERMINOLOGY = "TERMINOLOGY"                       # Standard defining terminology / symbols
    SAFETY_REQUIREMENT = "SAFETY_REQUIREMENT"         # Code of safety practice
    INSTALLATION_PRACTICE = "INSTALLATION_PRACTICE"   # Code of practice for laying/fitting (e.g. IS 7634)
    SAMPLING_CRITERIA = "SAMPLING_CRITERIA"           # Methods for sampling and inspection
    SUPERSEDES = "SUPERSEDES"                         # Replaces earlier standard


class ReferenceSemantics(str, Enum):
    """Semantic classification of a reference."""
    NORMATIVE = "NORMATIVE"       # Mandatory compliance requirement
    INFORMATIVE = "INFORMATIVE"   # Guidance or informative background only
    CONDITIONAL = "CONDITIONAL"   # Applies only under specific circumstances/configurations
    UNKNOWN = "UNKNOWN"           # Source data does not provide enough evidence to determine


class ProcurementImpact(str, Enum):
    """Impact of this dependency on procurement specifications and tender evaluation."""
    REQUIRED_SPECIFICATION = "REQUIRED_SPECIFICATION"
    REQUIRED_TEST = "REQUIRED_TEST"
    REQUIRED_SAFETY_CONDITION = "REQUIRED_SAFETY_CONDITION"
    REQUIRED_INSTALLATION_CONDITION = "REQUIRED_INSTALLATION_CONDITION"
    CERTIFICATION_REQUIREMENT = "CERTIFICATION_REQUIREMENT"
    INFORMATIONAL = "INFORMATIONAL"
    CONDITIONAL = "CONDITIONAL"
    UNKNOWN = "UNKNOWN"


class NormativeReference(Base, TimestampMixin):
    """
    Represents an explicit reference from one standard to another.
    Can link to a recognized standard in the DB or record an external standard number.
    """
    __tablename__ = "normative_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_standard_id: Mapped[int] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_standard_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_standard_number: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    relationship_type: Mapped[ReferenceType] = mapped_column(
        SQLEnum(ReferenceType), default=ReferenceType.NORMATIVE_REFERENCE, nullable=False
    )
    reference_semantics: Mapped[ReferenceSemantics] = mapped_column(
        SQLEnum(ReferenceSemantics), default=ReferenceSemantics.UNKNOWN, nullable=False
    )
    procurement_impact: Mapped[ProcurementImpact] = mapped_column(
        SQLEnum(ProcurementImpact), default=ProcurementImpact.UNKNOWN, nullable=False
    )
    source_clause_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_clauses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_edition_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    referencing_clause: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    condition_text: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    triggering_condition: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    test_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    provenance_id: Mapped[Optional[int]] = mapped_column(ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    source_standard: Mapped["IndianStandard"] = relationship(
        "IndianStandard",
        foreign_keys=[source_standard_id],
        back_populates="outgoing_references",
    )
    target_standard: Mapped[Optional["IndianStandard"]] = relationship(
        "IndianStandard",
        foreign_keys=[target_standard_id],
        back_populates="incoming_references",
    )
    source_edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition", foreign_keys=[source_edition_id])
    source_clause: Mapped[Optional["Clause"]] = relationship("Clause", foreign_keys=[source_clause_id])
    provenance: Mapped[Optional["ProvenanceRecord"]] = relationship("ProvenanceRecord")
