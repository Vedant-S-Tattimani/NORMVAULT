"""
Unified Evidence Indexer (Phase 8).
Builds a backward-traceable Evidence Index linking all conclusions to original sources and provenance records.
"""

from datetime import datetime, timezone
import hashlib
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.schemas.intelligence import EvidenceIndexRead, EvidenceIndexItemRead
from app.models.requirement import Requirement
from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause
from app.models.provenance import ProvenanceRecord
from app.models.gap import SpecificationGap


class EvidenceIndexer:
    """
    Compiles an auditable, indexed registry of all evidence cited in an intelligence analysis.
    """

    @classmethod
    def build_evidence_index(
        cls,
        requirements: List[Requirement],
        standards: List[IndianStandard],
        editions: List[StandardEdition],
        clauses: List[Clause],
        gaps: List[SpecificationGap],
        provenance_records: Optional[List[ProvenanceRecord]] = None,
    ) -> EvidenceIndexRead:
        """
        Compiles all evidence items into a unified EvidenceIndexRead.
        """
        entries: List[EvidenceIndexItemRead] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Index Requirements Evidence
        for req in requirements:
            req_hash = hashlib.sha256((req.extracted_text or "").encode("utf-8")).hexdigest()
            entries.append(
                EvidenceIndexItemRead(
                    evidence_id=f"EVID-REQ-{req.id}",
                    source_type="TENDER_DOCUMENT",
                    source_url=None,
                    source_hash=req_hash,
                    provenance_id=None,
                    standard_id=None,
                    standard_code=None,
                    edition_id=None,
                    clause_id=None,
                    clause_number=req.clause_reference,
                    requirement_id=req.id,
                    document_offset=f"Clause {req.clause_reference}" if req.clause_reference else None,
                    verified_at=now_iso,
                    description=f"Extracted requirement: {req.extracted_text[:120]}...",
                )
            )

        # 2. Index Standards Evidence
        for std in standards:
            entries.append(
                EvidenceIndexItemRead(
                    evidence_id=f"EVID-STD-{std.id}",
                    source_type="INDIAN_STANDARD",
                    source_url=f"https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?Standard_Number={std.standard_number}",
                    source_hash=hashlib.sha256(f"{std.standard_number}:{std.title}".encode("utf-8")).hexdigest(),
                    provenance_id=None,
                    standard_id=std.id,
                    standard_code=std.standard_number,
                    edition_id=None,
                    clause_id=None,
                    clause_number=None,
                    requirement_id=None,
                    document_offset=None,
                    verified_at=now_iso,
                    description=f"Indian Standard: {std.standard_number} - {std.title}",
                )
            )

        # 3. Index Editions Evidence
        for ed in editions:
            entries.append(
                EvidenceIndexItemRead(
                    evidence_id=f"EVID-ED-{ed.id}",
                    source_type="STANDARD_EDITION",
                    source_url=None,
                    source_hash=hashlib.sha256(f"{ed.standard_id}:{ed.edition_number}:{ed.year}".encode("utf-8")).hexdigest(),
                    provenance_id=None,
                    standard_id=ed.standard_id,
                    standard_code=None,
                    edition_id=ed.id,
                    clause_id=None,
                    clause_number=None,
                    requirement_id=None,
                    document_offset=None,
                    verified_at=now_iso,
                    description=f"Edition {ed.edition_number} ({ed.year}) - Status: {ed.status}",
                )
            )

        # 4. Index Clauses Evidence
        for cl in clauses:
            cl_std_id = cl.edition.standard_id if getattr(cl, "edition", None) else getattr(cl, "standard_id", None)
            entries.append(
                EvidenceIndexItemRead(
                    evidence_id=f"EVID-CLS-{cl.id}",
                    source_type="CLAUSE",
                    source_url=None,
                    source_hash=hashlib.sha256((cl.content or "").encode("utf-8")).hexdigest(),
                    provenance_id=None,
                    standard_id=cl_std_id,
                    standard_code=None,
                    edition_id=cl.edition_id,
                    clause_id=cl.id,
                    clause_number=cl.clause_number,
                    requirement_id=None,
                    document_offset=f"Clause {cl.clause_number}",
                    verified_at=now_iso,
                    description=f"Clause {cl.clause_number}: {cl.title or (cl.content[:80] + '...') if cl.content else ''}",
                )
            )

        # 5. Index Gaps Evidence
        for gap in gaps:
            orig_text = getattr(gap, "current_value", None) or (gap.requirement.extracted_text if getattr(gap, "requirement", None) else "")
            target_std = (gap.standard.standard_number if getattr(gap, "standard", None) else None) or getattr(gap, "target_standard", None)
            target_clause = getattr(gap, "affected_clause", None) or getattr(gap, "target_clause", None)

            entries.append(
                EvidenceIndexItemRead(
                    evidence_id=f"EVID-GAP-{gap.id or 'INJ'}",
                    source_type="SPECIFICATION_GAP",
                    source_url=None,
                    source_hash=hashlib.sha256(f"{gap.gap_type}:{gap.title}:{orig_text}".encode("utf-8")).hexdigest(),
                    provenance_id=gap.provenance_id,
                    standard_id=gap.affected_standard_id,
                    standard_code=target_std,
                    edition_id=gap.affected_edition_id,
                    clause_id=None,
                    clause_number=target_clause,
                    requirement_id=gap.requirement_id,
                    document_offset=f"Clause {target_clause}" if target_clause else None,
                    verified_at=now_iso,
                    description=f"Gap {gap.gap_type.value if hasattr(gap.gap_type, 'value') else gap.gap_type}: {gap.title}",
                )
            )

        # 6. Index Provenance Records
        if provenance_records:
            for prov in provenance_records:
                entries.append(
                    EvidenceIndexItemRead(
                        evidence_id=f"EVID-PROV-{prov.id}",
                        source_type="PROVENANCE_RECORD",
                        source_url=prov.source_url,
                        source_hash=prov.source_hash,
                        provenance_id=prov.id,
                        standard_id=None,
                        standard_code=None,
                        edition_id=None,
                        clause_id=None,
                        clause_number=None,
                        requirement_id=None,
                        document_offset=None,
                        verified_at=prov.created_at.isoformat() if prov.created_at else now_iso,
                        description=f"Provenance from {prov.source_name}: {prov.source_type}",
                    )
                )

        return EvidenceIndexRead(
            total_entries=len(entries),
            entries=entries,
        )
