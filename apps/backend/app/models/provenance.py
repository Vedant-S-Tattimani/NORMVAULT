"""
Domain model for Provenance tracking.
Ensures data honesty by tracking the origin of all knowledge graph entities.
"""

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class SourceType(str, Enum):
    BIS_PORTAL = "BIS_PORTAL"
    PDF_EXTRACTION = "PDF_EXTRACTION"
    MANUAL_ENTRY = "MANUAL_ENTRY"
    LLM_EXTRACTION = "LLM_EXTRACTION"


class ProvenanceRecord(Base, TimestampMixin):
    """
    Tracks the origin, confidence, and timestamp of ingested data.
    Every entity in the Standards Knowledge Graph must link back to a ProvenanceRecord.
    
    Semantics of `confidence_score`:
    - Phase 1 (Deterministic Ingestion from BIS Gazettes/DBs): Always exactly 1.0.
    - Phase 2 (LLM/NLP Extraction from Unstructured Text): Represents the extraction model's probability/confidence score (0.0 to 1.0).
    """
    __tablename__ = "provenance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_type: Mapped[SourceType] = mapped_column(
        SQLEnum(SourceType), nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    source_hash: Mapped[Optional[str]] = mapped_column(String(256), index=True, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    extraction_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
