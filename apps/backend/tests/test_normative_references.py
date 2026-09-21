import pytest
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard
from app.models.reference import NormativeReference, ReferenceType

def test_normative_references_types(db_session: Session):
    std_a = IndianStandard(standard_number="IS A", title="Standard A")
    std_b = IndianStandard(standard_number="IS B", title="Standard B")
    std_c = IndianStandard(standard_number="IS C", title="Standard C")
    
    db_session.add_all([std_a, std_b, std_c])
    db_session.commit()
    
    ref_b = NormativeReference(
        source_standard_id=std_a.id,
        target_standard_id=std_b.id,
        target_standard_number="IS B",
        relationship_type=ReferenceType.NORMATIVE_REFERENCE
    )
    
    ref_c = NormativeReference(
        source_standard_id=std_a.id,
        target_standard_id=std_c.id,
        target_standard_number="IS C",
        relationship_type=ReferenceType.TEST_METHOD
    )
    
    db_session.add_all([ref_b, ref_c])
    db_session.commit()
    
    # Retrieve and verify
    retrieved_a = db_session.query(IndianStandard).filter_by(standard_number="IS A").first()
    
    refs = retrieved_a.outgoing_references
    assert len(refs) == 2
    
    types = {r.relationship_type for r in refs}
    assert types == {ReferenceType.NORMATIVE_REFERENCE, ReferenceType.TEST_METHOD}
    
    ref_to_b = next(r for r in refs if r.target_standard_number == "IS B")
    assert ref_to_b.relationship_type == ReferenceType.NORMATIVE_REFERENCE
    assert ref_to_b.target_standard_id == std_b.id
    
    ref_to_c = next(r for r in refs if r.target_standard_number == "IS C")
    assert ref_to_c.relationship_type == ReferenceType.TEST_METHOD
    assert ref_to_c.target_standard_id == std_c.id

def test_missing_target_standard(db_session: Session):
    std_d = IndianStandard(standard_number="IS D", title="Standard D")
    db_session.add(std_d)
    db_session.commit()
    
    # It is valid to have a target_standard_number without an ID if the target standard isn't imported yet
    ref_unlinked = NormativeReference(
        source_standard_id=std_d.id,
        target_standard_number="IS E_UNKNOWN",
        relationship_type=ReferenceType.ALLIED_PRODUCT
    )
    db_session.add(ref_unlinked)
    db_session.commit()
    
    refs = db_session.query(NormativeReference).filter_by(target_standard_number="IS E_UNKNOWN").all()
    assert len(refs) == 1
    assert refs[0].target_standard_id is None
