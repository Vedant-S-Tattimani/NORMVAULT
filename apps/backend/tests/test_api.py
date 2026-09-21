import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause

def test_api_empty_standards(client: TestClient):
    response = client.get("/api/v1/standards/")
    assert response.status_code == 200
    assert response.json() == []

def test_api_standards_endpoints(client: TestClient, db_session: Session):
    # Setup test data
    std = IndianStandard(standard_number="IS 1000", title="Test API Standard")
    db_session.add(std)
    db_session.commit()
    db_session.refresh(std)

    ed = StandardEdition(standard_id=std.id, year=2024, edition_number=1)
    db_session.add(ed)
    db_session.commit()
    db_session.refresh(ed)

    clause = Clause(edition_id=ed.id, clause_number="1.0", content="API Test")
    db_session.add(clause)
    db_session.commit()

    # Test list standards
    response = client.get("/api/v1/standards/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["standard_number"] == "IS 1000"

    # Test search standard
    response = client.get("/api/v1/standards/?q=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    response = client.get("/api/v1/standards/?q=nothing")
    assert response.status_code == 200
    assert response.json() == []

    # Test get standard by id
    response = client.get(f"/api/v1/standards/{std.id}")
    assert response.status_code == 200
    assert response.json()["standard_number"] == "IS 1000"

    # Test get edition
    response = client.get(f"/api/v1/editions/{ed.id}")
    assert response.status_code == 200
    assert response.json()["year"] == 2024

    # Test get clauses for edition
    response = client.get(f"/api/v1/editions/{ed.id}/clauses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["clause_number"] == "1.0"
