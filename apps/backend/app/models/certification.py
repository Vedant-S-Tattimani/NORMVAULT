"""
Domain models for BIS Certification schemes and mandatory Quality Control Orders (QCO).
"""

from enum import Enum
from typing import Optional
from datetime import date
from sqlalchemy import String, Boolean, Date, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class CertificationScheme(str, Enum):
    ISI_MARK_SCHEME_I = "ISI_MARK_SCHEME_I"       # Standard Product Certification
    CRS_SCHEME_II = "CRS_SCHEME_II"               # Compulsory Registration Scheme (Electronics/IT)
    HALLMARKING_SCHEME_IV = "HALLMARKING_SCHEME_IV"# Precious metals
    ECO_MARK = "ECO_MARK"                         # Environmental labeling
    VOLUNTARY = "VOLUNTARY"                       # Non-mandatory voluntary compliance


class CertificationCurrentness(str, Enum):
    """Evaluation of whether the certification / QCO record is verified active or uncertain."""
    VERIFIED_CURRENT = "VERIFIED_CURRENT"           # Verified by gazette notice and active date
    CURRENTNESS_UNCERTAIN = "CURRENTNESS_UNCERTAIN" # Current status cannot be determined with confidence
    SUPERSEDED = "SUPERSEDED"                       # Replaced by newer order
    WITHDRAWN = "WITHDRAWN"                         # Revoked or rescinded order


class CertificationRequirement(Base, TimestampMixin):
    """
    Specifies statutory or certification requirements governing a standard.
    Crucial for government procurement compliance (e.g. GeM tenders).
    """
    __tablename__ = "certification_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(
        ForeignKey("indian_standards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheme: Mapped[CertificationScheme] = mapped_column(
        SQLEnum(CertificationScheme), default=CertificationScheme.ISI_MARK_SCHEME_I, nullable=False
    )
    is_mandatory_qco: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    qco_order_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    notifying_ministry: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    notification_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    enforcement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    currentness_status: Mapped[CertificationCurrentness] = mapped_column(
        SQLEnum(CertificationCurrentness), default=CertificationCurrentness.CURRENTNESS_UNCERTAIN, nullable=False
    )
    applicable_product_category: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    edition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("standard_editions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    edition_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verification_source: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    scope_condition: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    provenance_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    standard: Mapped["IndianStandard"] = relationship("IndianStandard", back_populates="certifications")
    edition: Mapped[Optional["StandardEdition"]] = relationship("StandardEdition")
    provenance: Mapped[Optional["ProvenanceRecord"]] = relationship("ProvenanceRecord")
