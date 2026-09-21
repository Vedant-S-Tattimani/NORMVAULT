"""
Domain models for Indian Standards (BIS), Editions, and Amendments.
Distinguishes Standard identity from specific Editions and published Amendments.
"""

from enum import Enum
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Integer, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class StandardStatus(str, Enum):
    ACTIVE = "ACTIVE"
    AMENDED = "AMENDED"
    REVISED = "REVISED"
    WITHDRAWN = "WITHDRAWN"
    SUPERSEDED = "SUPERSEDED"


class EditionStatus(str, Enum):
    """Explicit verification status of a specific edition of an Indian Standard."""
    CURRENT = "CURRENT"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"
    DRAFT = "DRAFT"
    UNKNOWN = "UNKNOWN"


class IndianStandard(Base, TimestampMixin):
    """
    Represents the canonical identity of an Indian Standard published by BIS.
    E.g., 'IS 4984' remains constant even as editions and amendments evolve.
    """
    __tablename__ = "indian_standards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    standard_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    division_code: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[StandardStatus] = mapped_column(
        SQLEnum(StandardStatus), default=StandardStatus.ACTIVE, nullable=False
    )
    is_mandatory_qco: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    qco_reference: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    provenance_id: Mapped[Optional[int]] = mapped_column(ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    editions: Mapped[List["StandardEdition"]] = relationship(
        "StandardEdition", back_populates="standard", cascade="all, delete-orphan"
    )
    amendments: Mapped[List["Amendment"]] = relationship(
        "Amendment", back_populates="standard", cascade="all, delete-orphan"
    )
    outgoing_references: Mapped[List["NormativeReference"]] = relationship(
        "NormativeReference",
        foreign_keys="NormativeReference.source_standard_id",
        back_populates="source_standard",
        cascade="all, delete-orphan",
    )
    incoming_references: Mapped[List["NormativeReference"]] = relationship(
        "NormativeReference",
        foreign_keys="NormativeReference.target_standard_id",
        back_populates="target_standard",
    )
    certifications: Mapped[List["CertificationRequirement"]] = relationship(
        "CertificationRequirement", back_populates="standard", cascade="all, delete-orphan"
    )
    provenance: Mapped[Optional["ProvenanceRecord"]] = relationship("ProvenanceRecord")


class StandardEdition(Base, TimestampMixin):
    """
    Represents a specific revision/year edition of an Indian Standard.
    E.g., 'IS 4984: 2016' is an edition of 'IS 4984'.
    """
    __tablename__ = "standard_editions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False)
    edition_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    status: Mapped[EditionStatus] = mapped_column(
        SQLEnum(EditionStatus), default=EditionStatus.UNKNOWN, nullable=False
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    reaffirmation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    superseded_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    superseded_by_edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    superseded_by_standard_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    supersession_reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    supersession_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    withdrawal_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    withdrawal_reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    withdrawal_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provenance_id: Mapped[Optional[int]] = mapped_column(ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    standard: Mapped["IndianStandard"] = relationship("IndianStandard", back_populates="editions")
    clauses: Mapped[List["Clause"]] = relationship(
        "Clause", back_populates="edition", cascade="all, delete-orphan"
    )
    amendments: Mapped[List["Amendment"]] = relationship(
        "Amendment", back_populates="edition", cascade="all, delete-orphan"
    )
    superseded_by: Mapped[Optional["StandardEdition"]] = relationship(
        "StandardEdition", remote_side=[id]
    )
    provenance: Mapped[Optional["ProvenanceRecord"]] = relationship("ProvenanceRecord")


class Amendment(Base, TimestampMixin):
    """
    Represents an official amendment issued for a standard.
    Amendments modify specific clauses without issuing an entirely new edition.
    """
    __tablename__ = "standard_amendments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False)
    edition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True, index=True)
    amendment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    affected_clauses: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    old_clause_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_clause_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clause_impact_summary: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_effective: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    provenance_id: Mapped[Optional[int]] = mapped_column(ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    standard: Mapped["IndianStandard"] = relationship("IndianStandard", back_populates="amendments")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition", back_populates="amendments")
    provenance: Mapped[Optional["ProvenanceRecord"]] = relationship("ProvenanceRecord")
