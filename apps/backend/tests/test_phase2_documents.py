import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentProcessingState
from app.models.requirement import ProcurementSpecification, Requirement

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_text_specification_intake(client: TestClient, db_session: Session):
    test_payload = {
        "title": "Supply of Industrial Motors",
        "department": "Energy Board",
        "tender_reference": "TEND-1234",
        "target_product_name": "Motor",
        "raw_content": "The motor shall have a rated power of 5 kW. The enclosure shall be IP55."
    }
    
    response = client.post("/api/v1/specifications/text", json=test_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["status"] == "COMPLETED"
    
    spec_id = data["id"]
    spec = db_session.query(ProcurementSpecification).filter(ProcurementSpecification.id == spec_id).first()
    assert spec is not None
    assert spec.title == "Supply of Industrial Motors"
    
    reqs = db_session.query(Requirement).filter(Requirement.specification_id == spec_id).all()
    assert len(reqs) >= 2
    
    req_texts = [r.extracted_text for r in reqs]
    assert any("5 kW" in t for t in req_texts)
    assert any("IP55" in t for t in req_texts)

def test_document_upload_mock(client: TestClient, db_session: Session):
    upload_file_path = FIXTURES_DIR / "temp_test_upload.txt"
    with open(upload_file_path, "w") as f:
        f.write("Supply industrial motors with IP55 rating.")
        
    try:
        with open(upload_file_path, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test_upload.txt", f, "text/plain")}
            )
        assert response.status_code == 202
        data = response.json()
        assert "id" in data
        doc_id = data["id"]
        
        doc = db_session.query(Document).filter(Document.id == doc_id).first()
        assert doc is not None
        assert doc.status == DocumentProcessingState.COMPLETED
        
        spec = db_session.query(ProcurementSpecification).filter(ProcurementSpecification.document_id == doc_id).first()
        assert spec is not None
        
        reqs = db_session.query(Requirement).filter(Requirement.specification_id == spec.id).all()
        assert len(reqs) > 0
    finally:
        if upload_file_path.exists():
            upload_file_path.unlink()

def test_document_upload_duplicate(client: TestClient, db_session: Session):
    upload_file_path = FIXTURES_DIR / "temp_dup.txt"
    with open(upload_file_path, "w") as f:
        f.write("Duplicate test file unique string 987654.")

    try:
        with open(upload_file_path, "rb") as f:
            res1 = client.post("/api/v1/documents/upload", files={"file": ("temp_dup.txt", f, "text/plain")})
        assert res1.status_code == 202
        doc_id = res1.json()["id"]

        # Upload again
        with open(upload_file_path, "rb") as f:
            res2 = client.post("/api/v1/documents/upload", files={"file": ("temp_dup.txt", f, "text/plain")})
        assert res2.status_code == 202
        assert res2.json()["id"] == doc_id
        assert res2.json()["message"] == "Document already exists"
    finally:
        if upload_file_path.exists():
            upload_file_path.unlink()

def test_invalid_mime_type(client: TestClient):
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_upload.csv", b"a,b,c", "text/csv")}
    )
    assert res.status_code == 400
    assert "Unsupported" in res.json()["detail"]

def test_empty_file(client: TestClient):
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")}
    )
    assert res.status_code == 400
    assert "Empty file" in res.json()["detail"]

def test_pdf_parsing(client: TestClient, db_session: Session):
    pdf_path = FIXTURES_DIR / "test_spec.pdf"
    assert pdf_path.exists(), f"Missing fixture at {pdf_path}"
    
    with open(pdf_path, "rb") as f:
        res = client.post("/api/v1/documents/upload", files={"file": ("test_spec.pdf", f, "application/pdf")})
    assert res.status_code == 202
    doc_id = res.json()["id"]
    
    doc = db_session.query(Document).filter(Document.id == doc_id).first()
    assert doc.status == DocumentProcessingState.COMPLETED, f"Status: {doc.status}, Error: {doc.error_message}"
    spec = db_session.query(ProcurementSpecification).filter(ProcurementSpecification.document_id == doc_id).first()
    assert spec is not None
    reqs = db_session.query(Requirement).filter(Requirement.specification_id == spec.id).all()
    assert len(reqs) > 0

def test_scanned_pdf_rejection(client: TestClient, db_session: Session):
    pdf_path = FIXTURES_DIR / "scanned.pdf"
    assert pdf_path.exists(), f"Missing fixture at {pdf_path}"
    
    with open(pdf_path, "rb") as f:
        res = client.post("/api/v1/documents/upload", files={"file": ("scanned.pdf", f, "application/pdf")})
    assert res.status_code == 202
    doc_id = res.json()["id"]
    
    doc = db_session.query(Document).filter(Document.id == doc_id).first()
    assert doc.status in [DocumentProcessingState.REQUIRES_OCR, DocumentProcessingState.FAILED_VALIDATION]
    assert doc.error_message == "OCR_REQUIRED"

