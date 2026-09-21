import json
import os
import pytest
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard, StandardEdition, Amendment
from app.models.clause import Clause
from app.models.reference import NormativeReference
from scripts.ingestion.validators import IngestStandard
from scripts.ingestion.resolvers import resolve_standard

@pytest.fixture
def test_standard_data():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "test_standard.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_ingestion_pipeline_success(db_session: Session, test_standard_data):
    # Validate
    validated = IngestStandard.model_validate(test_standard_data)
    
    # Resolve
    std = resolve_standard(db_session, validated)
    
    # Assert
    assert std.standard_number == "IS 1000"
    assert std.title == "Method of Test for Stuff"
    
    editions = std.editions
    assert len(editions) == 1
    ed = editions[0]
    assert ed.year == 2024
    
    clauses = ed.clauses
    assert len(clauses) == 3 # 1, 1.1, 2
    clause_numbers = {c.clause_number for c in clauses}
    assert clause_numbers == {"1", "1.1", "2"}
    
    amendments = std.amendments
    assert len(amendments) == 1
    assert amendments[0].amendment_number == 1
    
    refs = std.outgoing_references
    assert len(refs) == 2
    
    assert std.provenance_id is not None
    assert std.provenance.source_url == "https://bis.gov.in/test_standard"

def test_ingestion_deduplication(db_session: Session, test_standard_data):
    validated = IngestStandard.model_validate(test_standard_data)
    
    # Ingest once
    resolve_standard(db_session, validated)
    count_1 = db_session.query(IndianStandard).count()
    assert count_1 == 1
    
    # Ingest twice
    resolve_standard(db_session, validated)
    count_2 = db_session.query(IndianStandard).count()
    
    # Should not duplicate standard
    assert count_1 == count_2
    
    # Verify clauses are not duplicated
    clause_count = db_session.query(Clause).count()
    assert clause_count == 3
    
    # Verify references are not duplicated
    ref_count = db_session.query(NormativeReference).count()
    assert ref_count == 2
