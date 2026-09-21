import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause

def test_clause_hierarchy(db_session: Session):
    standard = IndianStandard(standard_number="IS 111", title="Test")
    db_session.add(standard)
    db_session.commit()
    
    edition = StandardEdition(standard_id=standard.id, year=2024)
    db_session.add(edition)
    db_session.commit()
    
    # Create top level clause 4
    clause_4 = Clause(edition_id=edition.id, clause_number="4", content="Top level", depth=0)
    db_session.add(clause_4)
    db_session.commit()
    
    # Create child clause 4.1
    clause_4_1 = Clause(edition_id=edition.id, clause_number="4.1", content="Child", parent_clause_id=clause_4.id, depth=1)
    db_session.add(clause_4_1)
    db_session.commit()
    
    # Create sub-children 4.1.1 and 4.1.2
    clause_4_1_1 = Clause(edition_id=edition.id, clause_number="4.1.1", content="Sub-child 1", parent_clause_id=clause_4_1.id, depth=2)
    clause_4_1_2 = Clause(edition_id=edition.id, clause_number="4.1.2", content="Sub-child 2", parent_clause_id=clause_4_1.id, depth=2)
    db_session.add_all([clause_4_1_1, clause_4_1_2])
    db_session.commit()
    
    # Retrieve and verify
    retrieved_4 = db_session.query(Clause).filter_by(clause_number="4").first()
    assert len(retrieved_4.children) == 1
    assert retrieved_4.children[0].clause_number == "4.1"
    
    retrieved_4_1 = db_session.query(Clause).filter_by(clause_number="4.1").first()
    assert retrieved_4_1.parent.clause_number == "4"
    assert len(retrieved_4_1.children) == 2
    
    sub_clause_numbers = {c.clause_number for c in retrieved_4_1.children}
    assert sub_clause_numbers == {"4.1.1", "4.1.2"}

def test_invalid_hierarchy(db_session: Session):
    standard = IndianStandard(standard_number="IS 222", title="Test")
    db_session.add(standard)
    db_session.commit()
    edition = StandardEdition(standard_id=standard.id, year=2024)
    db_session.add(edition)
    db_session.commit()
    
    clause_a = Clause(edition_id=edition.id, clause_number="A", content="A")
    db_session.add(clause_a)
    db_session.commit()
    
    # Enforce cycle (which might not be natively prevented by SQLite, but we can check we can set it and then maybe write application logic to prevent it, or test we don't accidentally get infinite loops).
    # Since SQLite doesn't prevent cycles automatically in self-referencing FKs unless we write triggers, we just verify the FK constraint failure if the parent doesn't exist.
    
    with pytest.raises(IntegrityError):
        invalid_clause = Clause(edition_id=edition.id, clause_number="B", content="B", parent_clause_id=9999)
        db_session.add(invalid_clause)
        db_session.commit()
    db_session.rollback()
