import pytest
import os
import sys
import json
from pathlib import Path

# Add root dir to sys path for importing scripts
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.standard import IndianStandard, StandardEdition, Amendment
from app.models.clause import Clause
from app.models.reference import NormativeReference
from app.models.provenance import ProvenanceRecord
from scripts.ingestion.resolvers import resolve_standard
from scripts.ingestion.validators import IngestStandard

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "acceptance_fixture.json")

def load_fixture() -> dict:
    with open(FIXTURE_PATH, "r") as f:
        return json.load(f)

def ingest_fixture(db_session: Session) -> int:
    data = load_fixture()
    validated_data = IngestStandard(**data)
    std = resolve_standard(db_session, validated_data)
    db_session.commit()
    return std.id

def test_acceptance_ingestion_and_counts(db_session: Session):
    # 1. Test Ingestion and Counts
    std_id = ingest_fixture(db_session)
    
    assert db_session.query(IndianStandard).count() == 1
    assert db_session.query(StandardEdition).count() == 1
    assert db_session.query(Amendment).count() == 1
    assert db_session.query(ProvenanceRecord).count() == 1
    assert db_session.query(Clause).count() == 4
    assert db_session.query(NormativeReference).count() == 2

    # 2. Test Idempotency (Deduplication)
    std_id_2 = ingest_fixture(db_session)
    assert std_id == std_id_2
    
    # Counts should remain exactly the same (except provenance creates a new record per ingestion event)
    assert db_session.query(IndianStandard).count() == 1
    assert db_session.query(StandardEdition).count() == 1
    assert db_session.query(Amendment).count() == 1
    assert db_session.query(Clause).count() == 4
    assert db_session.query(NormativeReference).count() == 2

def test_acceptance_invalid_record_validation():
    # 3. Test Invalid Record Validation
    data = load_fixture()
    # Remove mandatory standard_number
    del data["standard_number"]
    
    with pytest.raises(ValidationError):
        IngestStandard(**data)

def test_acceptance_provenance(db_session: Session):
    # 4. Test Provenance persistence and retrieval
    ingest_fixture(db_session)
    prov = db_session.query(ProvenanceRecord).order_by(ProvenanceRecord.id.desc()).first()
    assert prov.confidence_score == 1.0
    assert prov.source_url == "https://www.services.bis.gov.in/acceptance-test-gazette.pdf"

    std = db_session.query(IndianStandard).first()
    assert std.provenance_id == prov.id

def test_acceptance_clause_hierarchy(db_session: Session):
    # 5. Test Clause Hierarchy Persistence
    ingest_fixture(db_session)
    clauses = db_session.query(Clause).all()
    
    # Map clause_number to Clause object
    c_map = {c.clause_number: c for c in clauses}
    
    c4 = c_map["4"]
    c4_1 = c_map["4.1"]
    c4_1_1 = c_map["4.1.1"]
    c4_1_2 = c_map["4.1.2"]
    
    assert c4.depth == 0
    assert c4.parent_clause_id is None
    
    assert c4_1.depth == 1
    assert c4_1.parent_clause_id == c4.id
    
    assert c4_1_1.depth == 2
    assert c4_1_1.parent_clause_id == c4_1.id
    
    assert c4_1_2.depth == 2
    assert c4_1_2.parent_clause_id == c4_1.id

def test_acceptance_reference_relationships(db_session: Session):
    # 6. Test Reference Relationships (2 distinct types)
    ingest_fixture(db_session)
    refs = db_session.query(NormativeReference).all()
    assert len(refs) == 2
    
    types = {r.relationship_type.value for r in refs}
    assert "NORMATIVE_REFERENCE" in types
    assert "ALLIED_PRODUCT" in types

def test_acceptance_http_endpoints(client: TestClient, db_session: Session):
    # 7. Test HTTP Endpoints
    std_id = ingest_fixture(db_session)
    std = db_session.query(IndianStandard).filter(IndianStandard.id == std_id).first()
    ed_id = std.editions[0].id
    
    # GET /api/v1/standards/
    r = client.get("/api/v1/standards/")
    assert r.status_code == 200
    assert len(r.json()) == 1
    
    # GET /api/v1/standards/{id}
    r = client.get(f"/api/v1/standards/{std_id}")
    assert r.status_code == 200
    assert r.json()["standard_number"] == "IS 9999:2026"
    
    # GET /api/v1/standards/{id}/editions
    r = client.get(f"/api/v1/standards/{std_id}/editions")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["year"] == 2026
    
    # GET /api/v1/standards/{id}/references
    # NOTE: The endpoint retrieves references via the editions.
    # Our resolver saves references at the Standard level, but in NORMVAULT they are attached to editions. Wait...
    # Wait, the resolver does `NormativeReference(source_standard_id=std.id)`!
    # Ah, let's fix the endpoint or the resolver!
    
    r = client.get(f"/api/v1/standards/{std_id}/references")
    assert r.status_code == 200
    assert len(r.json()) == 2
    
    # GET /api/v1/editions/{id}
    r = client.get(f"/api/v1/editions/{ed_id}")
    assert r.status_code == 200
    
    # GET /api/v1/editions/{id}/amendments
    r = client.get(f"/api/v1/editions/{ed_id}/amendments")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["amendment_number"] == 1
    
    # GET /api/v1/editions/{id}/clauses
    r = client.get(f"/api/v1/editions/{ed_id}/clauses")
    assert r.status_code == 200
    assert len(r.json()) == 4
    
    # Test deterministic search
    r = client.get("/api/v1/standards/?q=9999")
    assert r.status_code == 200
    assert len(r.json()) == 1
    
    r = client.get("/api/v1/standards/?q=nonexistent")
    assert r.status_code == 200
    assert len(r.json()) == 0
