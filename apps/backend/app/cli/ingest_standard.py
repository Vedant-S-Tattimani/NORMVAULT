"""
CLI and Service Tool for Ingesting Structured BIS Standards into NORMVAULT.
Usage:
    python -m app.cli.ingest_standard --file path/to/standard.json
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from app.db.session import SessionLocal
from app.models.standard import (
    IndianStandard,
    StandardStatus,
    StandardEdition,
)
from app.models.clause import Clause
from app.models.reference import (
    NormativeReference,
    ReferenceType,
    ReferenceSemantics,
    ProcurementImpact,
)

def ingest_standard_payload(payload: Dict[str, Any], db=None) -> IndianStandard:
    """
    Idempotently ingests or updates a structured Indian Standard record in the database.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        std_num = payload["standard_number"].strip()
        title = payload["title"].strip()
        division = payload.get("division_code", "ETD")
        scope = payload.get("scope", "")
        is_qco = payload.get("is_mandatory_qco", False)
        qco_ref = payload.get("qco_reference", None)

        # Check if already exists
        std = db.query(IndianStandard).filter(IndianStandard.standard_number == std_num).first()
        if not std:
            std = IndianStandard(
                standard_number=std_num,
                title=title,
                division_code=division,
                scope=scope,
                status=StandardStatus.ACTIVE,
                is_mandatory_qco=is_qco,
                qco_reference=qco_ref,
            )
            db.add(std)
            db.flush()
        else:
            std.title = title
            std.division_code = division
            std.scope = scope
            std.is_mandatory_qco = is_qco
            std.qco_reference = qco_ref

        # Ingest edition if provided
        edition_data = payload.get("edition")
        edition_record = None
        if edition_data:
            ed_num = edition_data.get("edition_number", 1)
            ed_year = edition_data.get("year", 2024)
            edition_record = (
                db.query(StandardEdition)
                .filter(StandardEdition.standard_id == std.id, StandardEdition.edition_number == ed_num)
                .first()
            )
            if not edition_record:
                edition_record = StandardEdition(
                    standard_id=std.id,
                    edition_number=ed_num,
                    year=ed_year,
                    is_current=True,
                )
                db.add(edition_record)
                db.flush()

        # Ingest clauses
        clauses_data = payload.get("clauses", [])
        if edition_record and clauses_data:
            for c in clauses_data:
                c_num = c.get("clause_number", "").strip()
                c_title = c.get("title", "")
                c_text = c.get("text", "")
                
                existing_c = (
                    db.query(Clause)
                    .filter(Clause.edition_id == edition_record.id, Clause.clause_number == c_num)
                    .first()
                )
                if not existing_c:
                    new_c = Clause(
                        edition_id=edition_record.id,
                        clause_number=c_num,
                        title=c_title,
                        content=c_text,
                    )
                    db.add(new_c)

        # Ingest normative references
        refs_data = payload.get("normative_references", [])
        for ref_code in refs_data:
            target_std = db.query(IndianStandard).filter(IndianStandard.standard_number == ref_code).first()
            existing_ref = (
                db.query(NormativeReference)
                .filter(
                    NormativeReference.source_standard_id == std.id,
                    NormativeReference.target_standard_number == ref_code,
                )
                .first()
            )
            if not existing_ref:
                new_ref = NormativeReference(
                    source_standard_id=std.id,
                    target_standard_id=target_std.id if target_std else None,
                    target_standard_number=ref_code,
                    relationship_type=ReferenceType.NORMATIVE_REFERENCE,
                    reference_semantics=ReferenceSemantics.NORMATIVE,
                    procurement_impact=ProcurementImpact.REQUIRED_SPECIFICATION,
                )
                db.add(new_ref)

        db.commit()
        db.refresh(std)
        return std
    finally:
        if should_close:
            db.close()

def main():
    parser = argparse.ArgumentParser(description="Ingest structured BIS standard into NORMVAULT database")
    parser.add_argument("--file", required=True, help="Path to JSON file containing standard specification")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    std = ingest_standard_payload(payload)
    print(f"[SUCCESS] Successfully ingested standard '{std.standard_number}' (ID: {std.id}) - {std.title}")

if __name__ == "__main__":
    main()
