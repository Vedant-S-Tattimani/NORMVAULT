"""
Standards Indexing service over verified Standards Knowledge Foundation data.
Manages canonical text construction, content hashing, model versioning, and reindexing.
"""

from dataclasses import dataclass
import hashlib
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause
from app.models.reference import NormativeReference
from app.models.retrieval import StandardIndexEntry
from app.services.retrieval.embeddings import (
    EmbeddingProvider,
    get_embedding_provider,
    EmbeddingVersionMismatchError,
)
from app.services.retrieval.lexical import LexicalDocument, LexicalSearchEngine

logger = logging.getLogger(__name__)

INDEX_VERSION = "v1.0"


def construct_canonical_standard_text(standard: IndianStandard) -> str:
    """
    Construct the canonical text document representation of an Indian Standard.
    Hierarchy: Identity -> Title -> Scope -> Current Edition -> Clauses -> References.
    """
    lines: List[str] = [
        f"Standard Number: {standard.standard_number}",
        f"Title: {standard.title}",
        f"Status: {standard.status.value if hasattr(standard.status, 'value') else standard.status}",
    ]

    if standard.division_code:
        lines.append(f"Division: {standard.division_code}")
    if standard.department:
        lines.append(f"Department: {standard.department}")
    if standard.is_mandatory_qco:
        qco_info = f" (Ref: {standard.qco_reference})" if standard.qco_reference else ""
        lines.append(f"Mandatory Quality Control Order (QCO): YES{qco_info}")
    if standard.scope:
        lines.append(f"Scope: {standard.scope}")

    # Current edition details
    current_edition: Optional[StandardEdition] = None
    for ed in standard.editions:
        if ed.is_current:
            current_edition = ed
            break
    if not current_edition and standard.editions:
        current_edition = standard.editions[-1]

    if current_edition:
        lines.append(f"Current Edition: Year {current_edition.year} (Edition {current_edition.edition_number})")
        if current_edition.clauses:
            lines.append("Key Clauses:")
            # Cap clauses to prevent context explosion while preserving technical meat
            for c in current_edition.clauses[:15]:
                lines.append(f"- Clause {c.clause_number}: {c.content}")

    # Normative References
    if standard.outgoing_references:
        lines.append("Normative References:")
        for ref in standard.outgoing_references[:10]:
            target_num = ref.target_standard.standard_number if ref.target_standard else (ref.target_standard_number or "")
            rel = ref.relationship_type.value if hasattr(ref.relationship_type, 'value') else ref.relationship_type
            if target_num:
                lines.append(f"- Ref: {target_num} ({rel})")


    return "\n".join(lines)


@dataclass
class DenseIndexEntry:
    """In-memory dense index entry for fast vector search."""
    standard_id: int
    standard_number: str
    title: str
    scope: str
    edition_id: Optional[int]
    vector: List[float]
    metadata: Dict[str, Any]


class StandardsIndexer:
    """
    Manages indexing, hashing, version validation, and vector storage for verified standards.
    """

    def __init__(self, provider: Optional[EmbeddingProvider] = None):
        self.provider = provider or get_embedding_provider()
        self.metadata = self.provider.get_model_metadata()

    def compute_content_hash(self, text: str) -> str:
        """Compute SHA-256 hash over canonical text."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def build_index_for_standard(
        self,
        db: Session,
        standard: IndianStandard,
        force: bool = False,
    ) -> Optional[StandardIndexEntry]:
        """Index or update an individual verified standard."""
        canonical_text = construct_canonical_standard_text(standard)
        c_hash = self.compute_content_hash(canonical_text)

        # Check existing entry
        existing = db.query(StandardIndexEntry).filter_by(standard_id=standard.id).first()

        # Check if already up-to-date
        if (
            existing
            and not force
            and existing.content_hash == c_hash
            and existing.embedding_model == self.metadata.model_name
            and existing.embedding_dimension == self.metadata.dimension
            and existing.index_version == INDEX_VERSION
        ):
            return existing

        # Generate embedding vector
        vector = self.provider.embed_text(canonical_text)

        # Edition resolution
        current_ed_id = None
        for ed in standard.editions:
            if ed.is_current:
                current_ed_id = ed.id
                break

        metadata_dict = {
            "status": standard.status.value if hasattr(standard.status, "value") else str(standard.status),
            "division_code": standard.division_code,
            "department": standard.department,
            "is_mandatory_qco": standard.is_mandatory_qco,
            "qco_reference": standard.qco_reference,
            "current_year": standard.editions[0].year if standard.editions else None,
        }

        if existing:
            existing.index_version = INDEX_VERSION
            existing.embedding_model = self.metadata.model_name
            existing.embedding_dimension = self.metadata.dimension
            existing.content_hash = c_hash
            existing.indexed_text = canonical_text
            existing.embedding_vector = vector
            existing.metadata_payload = metadata_dict
            existing.edition_id = current_ed_id
            db.flush()
            return existing
        else:
            entry = StandardIndexEntry(
                standard_id=standard.id,
                edition_id=current_ed_id,
                index_version=INDEX_VERSION,
                embedding_model=self.metadata.model_name,
                embedding_dimension=self.metadata.dimension,
                content_hash=c_hash,
                indexed_text=canonical_text,
                embedding_vector=vector,
                metadata_payload=metadata_dict,
            )
            db.add(entry)
            db.flush()
            return entry

    def rebuild_index(self, db: Session, force: bool = False) -> Tuple[int, int, float]:
        """
        Rebuild index entries for all verified standards currently in the database.
        Returns (indexed_count, failures_count, duration_ms).
        """
        t0 = time.time()
        standards = db.query(IndianStandard).all()
        indexed = 0
        failures = 0

        for std in standards:
            try:
                self.build_index_for_standard(db, std, force=force)
                indexed += 1
            except Exception as e:
                logger.error(f"Failed to index standard {std.standard_number}: {e}")
                failures += 1

        db.commit()
        duration_ms = (time.time() - t0) * 1000.0
        return indexed, failures, round(duration_ms, 2)

    def load_lexical_and_dense_indices(
        self,
        db: Session,
    ) -> Tuple[LexicalSearchEngine, List[DenseIndexEntry]]:
        """
        Load index entries from DB into searchable in-memory lexical and dense structures.
        """
        entries = db.query(StandardIndexEntry).all()
        lexical_engine = LexicalSearchEngine()
        lex_docs: List[LexicalDocument] = []
        dense_entries: List[DenseIndexEntry] = []

        for entry in entries:
            std = entry.standard
            if not std:
                continue

            # Check model consistency
            if (
                entry.embedding_model != self.metadata.model_name
                or entry.embedding_dimension != self.metadata.dimension
            ):
                raise EmbeddingVersionMismatchError(
                    f"Index entry for {std.standard_number} was created with "
                    f"model '{entry.embedding_model}' (dim {entry.embedding_dimension}), "
                    f"but active provider is '{self.metadata.model_name}' (dim {self.metadata.dimension}). "
                    f"Please rebuild the search index."
                )

            # Build LexicalDocument
            clauses_summary = ""
            for ed in std.editions:
                if ed.is_current:
                    clauses_summary = " ".join([c.content for c in ed.clauses[:10]])
                    break

            lex_docs.append(LexicalDocument(
                standard_id=std.id,
                standard_number=std.standard_number,
                title=std.title,
                scope=std.scope or "",
                clauses_text=clauses_summary,
                metadata=entry.metadata_payload or {},
            ))

            # Build DenseIndexEntry
            if entry.embedding_vector:
                dense_entries.append(DenseIndexEntry(
                    standard_id=std.id,
                    standard_number=std.standard_number,
                    title=std.title,
                    scope=std.scope or "",
                    edition_id=entry.edition_id,
                    vector=entry.embedding_vector,
                    metadata=entry.metadata_payload or {},
                ))

        lexical_engine.index_documents(lex_docs)
        return lexical_engine, dense_entries
