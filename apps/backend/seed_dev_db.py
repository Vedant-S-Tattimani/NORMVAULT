import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from scripts.ingestion.resolvers import resolve_standard
from scripts.ingestion.validators import IngestStandard

# Ensure all models are imported for metadata
from app.models.standard import IndianStandard, StandardEdition, StandardStatus, EditionStatus, Amendment
from app.models.clause import Clause
from app.models.reference import NormativeReference, ReferenceType, ReferenceSemantics, ProcurementImpact
from app.models.certification import CertificationRequirement, CertificationScheme, CertificationCurrentness
from app.models.provenance import ProvenanceRecord, SourceType
from app.models.document import Document
from app.models.requirement import ProcurementSpecification, Requirement, RequirementEvidence, TechnicalParameter
from app.models.retrieval import StandardIndexEntry, RetrievalRun, RetrievalCandidate, RetrievalEvidence
from app.services.retrieval.indexer import StandardsIndexer

FIXTURE_PATH = Path("tests/fixtures/acceptance_fixture.json").resolve()
SYNTHETIC_POOL_PATH = Path("tests/fixtures/synthetic_standards_pool.json").resolve()

def seed_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Seed acceptance fixture
        if FIXTURE_PATH.exists():
            with open(FIXTURE_PATH, "r") as f:
                data = json.load(f)
            validated = IngestStandard(**data)
            std = resolve_standard(db, validated)
            print(f"Successfully seeded acceptance standard: {std.standard_number} (ID: {std.id})")

        # 2. Seed synthetic pool standards (motors, HDPE pipes, steel, cement)
        if SYNTHETIC_POOL_PATH.exists():
            with open(SYNTHETIC_POOL_PATH, "r") as f:
                pool_data = json.load(f)
            
            prov = ProvenanceRecord(
                source_type=SourceType.BIS_PORTAL,
                source_url="https://www.services.bis.gov.in/standards",
                source_hash="dev_seed_pool",
                confidence_score=1.0,
                extraction_metadata={"source": "dev_seed"},
            )
            db.add(prov)
            db.flush()

            for item in pool_data.get("standards", []):
                # Avoid duplicate
                existing = db.query(IndianStandard).filter_by(standard_number=item["standard_number"]).first()
                if existing:
                    continue

                std = IndianStandard(
                    standard_number=item["standard_number"],
                    title=item["title"],
                    scope=item.get("scope"),
                    division_code=item.get("division_code"),
                    status=StandardStatus(item["status"]),
                    is_mandatory_qco=item.get("is_mandatory_qco", False),
                    qco_reference=item.get("qco_reference"),
                    provenance_id=prov.id,
                )
                db.add(std)
                db.flush()

                # Determine edition status and metadata
                std_num = item["standard_number"]
                year = item.get("year", 2020)
                ed_status = EditionStatus.CURRENT
                is_curr = True
                superseded_by_std = None
                supersession_reason = None
                withdrawal_reason = None

                if std_num == "IS 325":
                    year = 1996
                    ed_status = EditionStatus.SUPERSEDED
                    is_curr = False
                    superseded_by_std = "IS 12615:2018"
                    supersession_reason = "Superseded by IS 12615 for line operated energy efficient induction motors"
                elif std_num == "IS 996":
                    year = 1979
                    ed_status = EditionStatus.WITHDRAWN
                    is_curr = False
                    withdrawal_reason = "Withdrawn by Bureau of Indian Standards Sectional Committee"
                elif std_num == "IS 12615":
                    year = 2018
                    ed_status = EditionStatus.CURRENT
                    is_curr = True

                ed = StandardEdition(
                    standard_id=std.id,
                    edition_number=1,
                    year=year,
                    status=ed_status,
                    is_current=is_curr,
                    superseded_by_standard_number=superseded_by_std,
                    supersession_reason=supersession_reason,
                    withdrawal_reason=withdrawal_reason,
                    provenance_id=prov.id,
                )
                db.add(ed)
                db.flush()

                # Seed amendments for IS 12615
                if std_num == "IS 12615":
                    amd1 = Amendment(
                        standard_id=std.id,
                        edition_id=ed.id,
                        amendment_number=1,
                        title="Amendment 1: Efficiency Tolerances",
                        summary="Revision of efficiency test tolerance values in Clause 7.1",
                        affected_clauses="Clause 7.1",
                        old_clause_text="Tolerance on efficiency shall be -15% of (100 - Efficiency).",
                        new_clause_text="Tolerance on efficiency shall be -10% of (100 - Efficiency) for motors >= 0.75 kW.",
                        clause_impact_summary="Tightened efficiency measurement tolerance for IE3 class.",
                        is_effective=True,
                        provenance_id=prov.id,
                    )
                    amd2 = Amendment(
                        standard_id=std.id,
                        edition_id=ed.id,
                        amendment_number=2,
                        title="Amendment 2: Terminal Box Marking",
                        summary="Update to terminal box marking and earthing lug specifications",
                        affected_clauses="Clause 8.3",
                        old_clause_text=None,
                        new_clause_text=None,
                        clause_impact_summary="Clause impact not indexed.",
                        is_effective=True,
                        provenance_id=prov.id,
                    )
                    db.add(amd1)
                    db.add(amd2)

                for c_data in item.get("clauses", []):
                    cl = Clause(
                        edition_id=ed.id,
                        clause_number=c_data["clause_number"],
                        content=c_data["content"],
                        provenance_id=prov.id,
                    )
                    db.add(cl)
                print(f"Successfully seeded standard: {std.standard_number} (ID: {std.id}) - {std.title[:40]}")

            db.commit()

            # Second pass: Seed Normative References & Certification Requirements
            for item in pool_data.get("standards", []):
                src_std = db.query(IndianStandard).filter_by(standard_number=item["standard_number"]).first()
                if not src_std:
                    continue

                # References
                for ref_data in item.get("references", []):
                    target_std = db.query(IndianStandard).filter_by(standard_number=ref_data["target_standard_number"]).first()
                    target_id = target_std.id if target_std else None

                    # Locate source clause if referencing_clause provided
                    source_clause_id = None
                    if ref_data.get("referencing_clause") and src_std.editions:
                        cl = db.query(Clause).filter(
                            Clause.edition_id == src_std.editions[0].id,
                            Clause.clause_number == ref_data["referencing_clause"]
                        ).first()
                        if cl:
                            source_clause_id = cl.id

                    target_ed_year = None
                    if ref_data.get("target_standard_number") == "IS 15999":
                        target_ed_year = 2014

                    ref = NormativeReference(
                        source_standard_id=src_std.id,
                        source_edition_id=src_std.editions[0].id if src_std.editions else None,
                        target_standard_id=target_id,
                        target_standard_number=ref_data["target_standard_number"],
                        target_edition_year=target_ed_year,
                        relationship_type=ReferenceType(ref_data.get("relationship_type", "NORMATIVE_REFERENCE")),
                        reference_semantics=ReferenceSemantics(ref_data.get("reference_semantics", "UNKNOWN")),
                        procurement_impact=ProcurementImpact(ref_data.get("procurement_impact", "UNKNOWN")),
                        source_clause_id=source_clause_id,
                        referencing_clause=ref_data.get("referencing_clause"),
                        condition_text=ref_data.get("condition_text"),
                        triggering_condition=ref_data.get("triggering_condition"),
                        test_name=ref_data.get("test_name"),
                        notes=ref_data.get("notes"),
                        provenance_id=prov.id,
                    )
                    db.add(ref)

                # Certifications
                for cert_data in item.get("certifications", []):
                    cert = CertificationRequirement(
                        standard_id=src_std.id,
                        edition_id=src_std.editions[0].id if src_std.editions else None,
                        edition_year=src_std.editions[0].year if src_std.editions else None,
                        scheme=CertificationScheme(cert_data.get("scheme", "ISI_MARK_SCHEME_I")),
                        is_mandatory_qco=cert_data.get("is_mandatory_qco", False),
                        qco_order_number=cert_data.get("qco_order_number"),
                        notifying_ministry=cert_data.get("notifying_ministry"),
                        currentness_status=CertificationCurrentness(cert_data.get("currentness_status", "CURRENTNESS_UNCERTAIN")),
                        applicable_product_category=cert_data.get("applicable_product_category"),
                        verification_source="Gazette Order Verified",
                        provenance_id=prov.id,
                    )
                    db.add(cert)

            db.commit()

        # 3. Build Search Index
        indexer = StandardsIndexer()
        indexed, failures, duration_ms = indexer.rebuild_index(db, force=True)
        print(f"Search index built: {indexed} standards indexed in {duration_ms:.1f}ms with {failures} failures.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
