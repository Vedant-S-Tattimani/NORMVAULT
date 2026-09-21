"""
Domain models for unstructured Document Intelligence and processing lifecycle.
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class DocumentProcessingState(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    EXTRACTING = "EXTRACTING"
    STRUCTURING = "STRUCTURING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED_VALIDATION = "FAILED_VALIDATION"
    FAILED_EXTRACTION = "FAILED_EXTRACTION"
    REQUIRES_OCR = "REQUIRES_OCR"

class Document(Base, TimestampMixin):
    """
    Represents an uploaded unstructured document (e.g. PDF, DOCX, TXT).
    """
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=False)
    
    upload_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    status: Mapped[DocumentProcessingState] = mapped_column(
        SQLEnum(DocumentProcessingState), default=DocumentProcessingState.UPLOADED, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    specifications: Mapped[List["ProcurementSpecification"]] = relationship(
        "ProcurementSpecification", back_populates="document", cascade="all, delete-orphan"
    )
