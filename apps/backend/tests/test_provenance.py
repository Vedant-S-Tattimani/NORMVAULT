import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.provenance import ProvenanceRecord, SourceType
from app.models.standard import IndianStandard, StandardEdition, Amendment
from app.models.clause import Clause
from app.models.reference import NormativeReference, ReferenceType

def test_provenance_persists(db_session: Session):
    prov = ProvenanceRecord(
        source_type=SourceType.BIS_PORTAL,
        source_url="https://bis.gov.in/test",
        source_hash="abcd123",
        confidence_score=1.0,
        extraction_metadata={"method": "scrape"}
    )
    db_session.add(prov)
    db_session.commit()
    db_session.refresh(prov)
    
    assert prov.id is not None
    assert prov.source_type == SourceType.BIS_PORTAL
    assert prov.confidence_score == 1.0
    assert prov.extraction_metadata["method"] == "scrape"

def test_invalid_provenance(db_session: Session):
    with pytest.raises(IntegrityError):
        # Missing required source_type
        invalid_prov = ProvenanceRecord()
        db_session.add(invalid_prov)
        db_session.commit()
    db_session.rollback()

def test_provenance_relationships(db_session: Session):
    prov = ProvenanceRecord(source_type=SourceType.PDF_EXTRACTION)
    db_session.add(prov)
    db_session.commit()
    
    standard = IndianStandard(
        standard_number="IS 1234",
        title="Test Standard",
        provenance_id=prov.id
    )
    db_session.add(standard)
    db_session.commit()
    
    edition = StandardEdition(
        standard_id=standard.id,
        year=2024,
        provenance_id=prov.id
    )
    db_session.add(edition)
    db_session.commit()
    
    amendment = Amendment(
        standard_id=standard.id,
        amendment_number=1,
        summary="Test Amendment",
        provenance_id=prov.id
    )
    db_session.add(amendment)
    db_session.commit()
    
    clause = Clause(
        edition_id=edition.id,
        clause_number="1.0",
        content="Test content",
        provenance_id=prov.id
    )
    db_session.add(clause)
    db_session.commit()
    
    target_std = IndianStandard(
        standard_number="IS 9999",
        title="Target Std",
        provenance_id=prov.id
    )
    db_session.add(target_std)
    db_session.commit()

    reference = NormativeReference(
        source_standard_id=standard.id,
        target_standard_id=target_std.id,
        target_standard_number="IS 9999",
        relationship_type=ReferenceType.TEST_METHOD,
        provenance_id=prov.id
    )
    db_session.add(reference)
    db_session.commit()
    
    # Retrieve and verify relationships
    retrieved_std = db_session.query(IndianStandard).filter_by(standard_number="IS 1234").first()
    assert retrieved_std.provenance.source_type == SourceType.PDF_EXTRACTION
    
    retrieved_edition = db_session.query(StandardEdition).filter_by(year=2024).first()
    assert retrieved_edition.provenance.source_type == SourceType.PDF_EXTRACTION
    
    retrieved_amend = db_session.query(Amendment).filter_by(amendment_number=1).first()
    assert retrieved_amend.provenance.source_type == SourceType.PDF_EXTRACTION
    
    retrieved_clause = db_session.query(Clause).filter_by(clause_number="1.0").first()
    assert retrieved_clause.provenance.source_type == SourceType.PDF_EXTRACTION
    
    retrieved_ref = db_session.query(NormativeReference).filter_by(target_standard_number="IS 9999").first()
    assert retrieved_ref.provenance.source_type == SourceType.PDF_EXTRACTION
