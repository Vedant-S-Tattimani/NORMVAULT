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
from app.models.document import Document, DocumentProcessingState
from app.models.requirement import (
    ProcurementSpecification,
    Requirement,
    RequirementEvidence,
    TechnicalParameter,
    RequirementType,
    RequirementExtractionStatus,
)
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
            with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            validated = IngestStandard(**data)
            std = resolve_standard(db, validated)
            print(f"Successfully seeded acceptance standard: {std.standard_number} (ID: {std.id})")

        # 2. Seed synthetic pool standards (motors, HDPE pipes, steel, cement)
        if SYNTHETIC_POOL_PATH.exists():
            with open(SYNTHETIC_POOL_PATH, "r", encoding="utf-8") as f:
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

        # 4. Seed Benchmark Procurement Specifications and Requirements
        doc1 = Document(
            filename="NTPC_Tender_Doc_SecIV.pdf",
            mime_type="application/pdf",
            file_size=1048576,
            file_hash="7f9a2b8e4c1d6f3a5e8b0c2d4f6a8b1c3e5d7f9a2b8e4c1d6f3a5e8b0c2d4f6a",
            page_count=24,
            status=DocumentProcessingState.COMPLETED
        )
        db.add(doc1)
        db.flush()

        spec1 = ProcurementSpecification(
            document_id=doc1.id,
            title="Supply of 3-Phase Induction Motors (15 kW)",
            department="NTPC Limited",
            tender_reference="NTPC/2025/ET-8819",
            target_product_name="Three-Phase Induction Motor 15 kW",
            raw_content="Motor shall be capable of delivering continuous rated output of 15 kW at 415V, 50Hz, 3-Phase with class F insulation and temperature rise limited to class B limits. Rated voltage 415V ± 10% (Section 4.2), while Appendix Table 2 notes 400V nominal for auxiliary drive systems. All motors shall conform to minimum Premium Efficiency Class IE3 in accordance with IS 12615. Efficiency testing shall be conducted per IS 15999 (Part 2/Sec 1).",
            source_format="DOCUMENT",
            status="COMPLETED"
        )
        db.add(spec1)
        db.flush()

        r1 = Requirement(
            specification_id=spec1.id,
            clause_reference="Section 4.2.1, Clause 3",
            requirement_type=RequirementType.MECHANICAL,
            extraction_status=RequirementExtractionStatus.EXPLICIT,
            extracted_text="Motor shall be capable of delivering continuous rated output of 15 kW at 415V, 50Hz, 3-Phase with class F insulation and temperature rise limited to class B limits."
        )
        db.add(r1)
        db.flush()
        db.add(TechnicalParameter(requirement_id=r1.id, name="nominal output", original_value="15 kW", normalized_value="15", target_value="15", unit="kW"))
        db.add(TechnicalParameter(requirement_id=r1.id, name="phase", original_value="3-Phase AC", normalized_value="3", target_value="3-Phase", unit=""))
        db.add(TechnicalParameter(requirement_id=r1.id, name="frequency", original_value="50 Hz ± 3%", normalized_value="50", target_value="50", unit="Hz", tolerance="± 3%"))
        db.add(TechnicalParameter(requirement_id=r1.id, name="duty cycle", original_value="S1 Continuous", normalized_value="S1", target_value="S1", unit=""))
        db.add(RequirementEvidence(requirement_id=r1.id, document_id=doc1.id, page_number=14, section_heading="Electrical Rating & Duty", block_identifier="SEC-4-CL-3", source_text="Motor shall be capable of delivering continuous rated output of 15 kW at 415V, 50Hz, 3-Phase with class F insulation."))

        r2 = Requirement(
            specification_id=spec1.id,
            clause_reference="Section 4.2 vs Appendix Table 2",
            requirement_type=RequirementType.TESTING,
            extraction_status=RequirementExtractionStatus.UNCERTAIN,
            extracted_text="Rated voltage 415V ± 10% (Section 4.2), while Appendix Table 2 notes 400V nominal for auxiliary drive systems."
        )
        db.add(r2)
        db.flush()
        db.add(TechnicalParameter(requirement_id=r2.id, name="rated voltage", original_value="415 V", normalized_value="415", target_value="415", unit="V", tolerance="± 10%"))
        db.add(TechnicalParameter(requirement_id=r2.id, name="appendix voltage", original_value="400 V", normalized_value="400", target_value="400", unit="V"))
        db.add(RequirementEvidence(requirement_id=r2.id, document_id=doc1.id, page_number=14, section_heading="Voltage Rating", block_identifier="SEC-4-CL-2", source_text="Rated voltage 415V ± 10% (Section 4.2), while Appendix Table 2 notes 400V nominal."))

        r3 = Requirement(
            specification_id=spec1.id,
            clause_reference="Section 4.3, Clause 1",
            requirement_type=RequirementType.TESTING,
            extraction_status=RequirementExtractionStatus.EXPLICIT,
            extracted_text="All motors shall conform to minimum Premium Efficiency Class IE3 in accordance with IS 12615. Efficiency testing shall be conducted per IS 15999 (Part 2/Sec 1)."
        )
        db.add(r3)
        db.flush()
        db.add(TechnicalParameter(requirement_id=r3.id, name="efficiency class", original_value="IE3 Premium", normalized_value="IE3", target_value="IE3", unit=""))
        db.add(TechnicalParameter(requirement_id=r3.id, name="test method", original_value="IS 15999 Part 2/Sec 1", normalized_value="IS 15999", target_value="IS 15999", unit=""))
        db.add(TechnicalParameter(requirement_id=r3.id, name="full load efficiency", original_value="≥ 92.1%", normalized_value="92.1", target_value="92.1", unit="%", operator=">="))
        db.add(RequirementEvidence(requirement_id=r3.id, document_id=doc1.id, page_number=15, section_heading="Efficiency & Testing", block_identifier="SEC-4-CL-1", source_text="All motors shall conform to minimum Premium Efficiency Class IE3 in accordance with IS 12615."))

        # Spec 2: Switchgear
        doc2 = Document(filename="NHPC_Switchgear_Spec_Rev2.pdf", mime_type="application/pdf", file_size=2097152, file_hash="a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0", page_count=38, status=DocumentProcessingState.COMPLETED)
        db.add(doc2)
        db.flush()
        spec2 = ProcurementSpecification(document_id=doc2.id, title="High-Voltage Switchgear & Vacuum Circuit Breakers 33kV", department="NHPC Limited", tender_reference="NHPC/HYDRO/P-402", target_product_name="Vacuum Circuit Breakers 33kV", raw_content="33kV outdoor vacuum circuit breakers with 25kA breaking capacity for 3 seconds.", source_format="DOCUMENT", status="COMPLETED")
        db.add(spec2)
        db.flush()
        r_sg = Requirement(specification_id=spec2.id, clause_reference="Section 3.1", requirement_type=RequirementType.SAFETY, extraction_status=RequirementExtractionStatus.EXPLICIT, extracted_text="33kV outdoor vacuum circuit breakers with 25kA breaking capacity for 3 seconds.")
        db.add(r_sg)

        # Spec 3: Distribution Transformers
        doc3 = Document(filename="BHEL_EDN_TRANS_2025.pdf", mime_type="application/pdf", file_size=1572864, file_hash="fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210", page_count=18, status=DocumentProcessingState.COMPLETED)
        db.add(doc3)
        db.flush()
        spec3 = ProcurementSpecification(document_id=doc3.id, title="11kV Distribution Transformers Dry Type 500 kVA", department="BHEL", tender_reference="BHEL-EDN/SPEC/TRANS-09", target_product_name="11kV Distribution Transformers 500 kVA", raw_content="11kV/433V distribution transformers conforming to IS 1180 (Part 1) Level 2 energy efficiency.", source_format="DOCUMENT", status="COMPLETED")
        db.add(spec3)
        db.flush()
        r_tr = Requirement(specification_id=spec3.id, clause_reference="Section 2.4", requirement_type=RequirementType.CERTIFICATION, extraction_status=RequirementExtractionStatus.EXPLICIT, extracted_text="11kV/433V distribution transformers conforming to IS 1180 (Part 1) Level 2 energy efficiency with mandatory BIS ISI mark.")
        db.add(r_tr)

        # Spec 4: Substation
        doc4 = Document(filename="PGCIL_GIS_400KV_SR2.pdf", mime_type="application/pdf", file_size=4194304, file_hash="123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0", page_count=64, status=DocumentProcessingState.COMPLETED)
        db.add(doc4)
        db.flush()
        spec4 = ProcurementSpecification(document_id=doc4.id, title="400kV Gas Insulated Substation Equipment", department="POWERGRID", tender_reference="POWERGRID/SR-II/SUB-22", target_product_name="Gas Insulated Substation 400kV", raw_content="400kV SF6 gas insulated substation switchgear equipment.", source_format="DOCUMENT", status="COMPLETED")
        db.add(spec4)
        db.flush()
        r_gis = Requirement(specification_id=spec4.id, clause_reference="Section 1.2", requirement_type=RequirementType.SAFETY, extraction_status=RequirementExtractionStatus.EXPLICIT, extracted_text="400kV SF6 gas insulated switchgear equipment tested per IEC/IS standards.")
        db.add(r_gis)

        db.commit()
        print(f"Successfully seeded 4 benchmark procurement specifications and requirements.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
