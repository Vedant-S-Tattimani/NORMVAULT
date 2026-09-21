"""
Domain model for individual standard Clauses and text fragments.
"""

from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Clause(Base, TimestampMixin):
    """
    Represents an atomic clause or sub-clause within a standard edition.
    E.g., Clause 4.2 'Raw Material' in IS 4984:2016.
    """
    __tablename__ = "standard_clauses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    edition_id: Mapped[int] = mapped_column(ForeignKey("standard_editions.id", ondelete="CASCADE"), nullable=False)
    clause_number: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_normative: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_clause_id: Mapped[Optional[int]] = mapped_column(ForeignKey("standard_clauses.id", ondelete="CASCADE"), nullable=True)
    provenance_id: Mapped[Optional[int]] = mapped_column(ForeignKey("provenance_records.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    edition: Mapped["StandardEdition"] = relationship("StandardEdition", back_populates="clauses")
    parent: Mapped[Optional["Clause"]] = relationship("Clause", remote_side=[id], back_populates="children")
    children: Mapped[List["Clause"]] = relationship("Clause", back_populates="parent", cascade="all, delete-orphan")
    provenance: Mapped[Optional["ProvenanceRecord"]] = relationship("ProvenanceRecord")
