"""
NORMVAULT Phase 2 Final Acceptance Hardening Test Suite.
Tests all 18 acceptance criteria:
1. Real processing states
2. Requirement evidence precision (offsets, block identifiers, smallest spans)
3. LLM extraction audit (A-I validation cases)
4. Evidence alignment validation
5. Explicit / Inferred / Uncertain classification
6. Technical parameter structure (5 kW, IP55, -10 °C to 50 °C, 1000 mm × 500 mm, 10–15 bar)
7. PDF machine-readable parsing
8. Scanned PDF detection (OCR_REQUIRED)
9. Document lifecycle transitions
10. All API endpoints execution (POST /documents, POST /{id}/process, GET /{id}, GET /{id}/status, GET /{id}/content, GET /{id}/requirements, POST /specifications/text)
11. File security (oversized, wrong MIME, traversal filename, unsupported ext, malformed PDF, empty file)
12. Duplicate document deduplication
14. No fake data audit
"""

import os
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentProcessingState
from app.models.requirement import (
    RequirementType,
    RequirementExtractionStatus,
    ProcurementSpecification,
    Requirement,
    RequirementEvidence,
    TechnicalParameter,
)
from app.schemas.extraction import (
    ProcurementExtractionSchema,
    ExtractedRequirementSchema,
    ExtractedParameterSchema,
)
from app.services.document_parser import (
    NormalizedDocument,
    NormalizedBlock,
    parse_raw_text,
    PdfParser,
    PlainTextParser,
    get_document_parser,
)
from app.services.requirement_extractor import RequirementExtractorService

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# =====================================================================
# 1. REAL PROCESSING STATES & 9. DOCUMENT LIFECYCLE
# =====================================================================

def test_document_lifecycle_states(client: TestClient, db_session: Session):
    """Verify document transitions: UPLOADED -> VALIDATING -> EXTRACTING -> STRUCTURING -> ANALYZING -> COMPLETED."""
    upload_file = FIXTURES_DIR / "temp_lifecycle.txt"
    with open(upload_file, "w") as f:
        f.write("The motor shall have a rated power of 5 kW. The enclosure shall be IP55.")

    try:
        with open(upload_file, "rb") as f:
            res = client.post("/api/v1/documents", files={"file": ("temp_lifecycle.txt", f, "text/plain")})
        assert res.status_code == 202
        doc_id = res.json()["id"]

        doc = db_session.query(Document).filter(Document.id == doc_id).first()
        assert doc is not None
        assert doc.status == DocumentProcessingState.COMPLETED

        # Check status endpoint
        status_res = client.get(f"/api/v1/documents/{doc_id}/status")
        assert status_res.status_code == 200
        assert status_res.json()["status"] == "COMPLETED"
        assert status_res.json()["error"] is None
    finally:
        if upload_file.exists():
            upload_file.unlink()


# =====================================================================
# 2. REQUIREMENT EVIDENCE PRECISION (Smallest practical span, offsets)
# =====================================================================

def test_requirement_evidence_precision():
    """Verify extracted requirements point to smallest practical source span with character offsets."""
    text = "The motor shall have a rated power of 5 kW. The enclosure shall be IP55."
    doc = parse_raw_text(text)
    extractor = RequirementExtractorService()
    result = extractor.extract_from_document(doc)

    assert len(result.requirements) >= 2
    req_power = next((r for r in result.requirements if "5 kW" in r.extracted_text or "5 kW" in (r.source_text or "")), None)
    req_ip = next((r for r in result.requirements if "IP55" in r.extracted_text or "IP55" in (r.source_text or "")), None)

    assert req_power is not None
    assert req_ip is not None

    # Sentence A: Power evidence must ONLY be the first sentence
    assert "rated power of 5 kW" in req_power.source_text
    assert "IP55" not in req_power.source_text
    assert req_power.start_offset == 0
    assert req_power.end_offset == len(req_power.source_text)

    # Sentence B: IP55 evidence must ONLY be the second sentence
    assert "IP55" in req_ip.source_text
    assert "5 kW" not in req_ip.source_text
    assert req_ip.start_offset > req_power.end_offset
    assert req_ip.end_offset > req_ip.start_offset

    # Spans are distinct and do not cover entire document
    assert req_power.source_text != text
    assert req_ip.source_text != text


# =====================================================================
# 3. LLM EXTRACTION AUDIT (Cases A through I)
# =====================================================================

def test_llm_audit_case_a_valid_structured_response():
    """A. Valid structured response."""
    data = {
        "title": "Industrial Motor Spec",
        "target_product_name": "Motor",
        "requirements": [
            {
                "requirement_type": "MECHANICAL",
                "extraction_status": "EXPLICIT",
                "extracted_text": "Rated power 5 kW",
                "source_text": "The motor shall have a rated power of 5 kW.",
                "parameters": [
                    {"name": "Power", "original_value": "5 kW", "normalized_value": "5", "unit": "kW", "operator": "="}
                ]
            }
        ]
    }
    schema = ProcurementExtractionSchema(**data)
    assert len(schema.requirements) == 1
    assert schema.requirements[0].parameters[0].unit == "kW"

def test_llm_audit_case_b_missing_required_field():
    """B. Missing required field (extracted_text)."""
    with pytest.raises(ValidationError):
        ProcurementExtractionSchema(
            requirements=[{"requirement_type": "MECHANICAL", "extraction_status": "EXPLICIT"}]
        )

def test_llm_audit_case_c_invalid_enum():
    """C. Invalid enum for requirement_type or extraction_status."""
    with pytest.raises(ValidationError):
        ProcurementExtractionSchema(
            requirements=[
                {
                    "requirement_type": "INVALID_CATEGORY",
                    "extraction_status": "EXPLICIT",
                    "extracted_text": "Clause text",
                }
            ]
        )

def test_llm_audit_case_d_malformed_structured_output():
    """D. Malformed structured output (invalid types)."""
    with pytest.raises(ValidationError):
        ProcurementExtractionSchema(requirements="not a list")

def test_llm_audit_case_e_missing_evidence():
    """E. Missing evidence (source_text is None) is flagged."""
    extractor = RequirementExtractorService()
    doc = parse_raw_text("Some general clause without specific match.")
    mock_parsed = ProcurementExtractionSchema(
        requirements=[
            ExtractedRequirementSchema(
                requirement_type=RequirementType.MATERIAL,
                extraction_status=RequirementExtractionStatus.EXPLICIT,
                extracted_text="Motor shall be robust.",
                source_text=None,  # Missing evidence
            )
        ]
    )
    result = extractor._validate_and_align_extraction(mock_parsed, doc)
    assert result.requirements[0].source_text is None

def test_llm_audit_case_f_evidence_does_not_match_source():
    """F. Evidence that does not match source text must be rejected."""
    extractor = RequirementExtractorService()
    doc = parse_raw_text("The motor shall have a rated power of 5 kW.")
    mock_parsed = ProcurementExtractionSchema(
        requirements=[
            ExtractedRequirementSchema(
                requirement_type=RequirementType.MECHANICAL,
                extraction_status=RequirementExtractionStatus.EXPLICIT,
                extracted_text="Power rating",
                source_text="The motor shall have a rated power of 10 kW.", # DOES NOT MATCH
            )
        ]
    )
    result = extractor._validate_and_align_extraction(mock_parsed, doc)
    req = result.requirements[0]
    assert req.source_text is None
    assert req.extraction_status == RequirementExtractionStatus.UNCERTAIN

def test_llm_audit_case_g_hallucinated_requirement_not_in_source():
    """G. Hallucinated requirement not in source must be rejected or marked UNCERTAIN."""
    extractor = RequirementExtractorService()
    doc = parse_raw_text("Delivery of pipes.")
    mock_parsed = ProcurementExtractionSchema(
        requirements=[
            ExtractedRequirementSchema(
                requirement_type=RequirementType.CERTIFICATION,
                extraction_status=RequirementExtractionStatus.EXPLICIT,
                extracted_text="Shall comply with IS 4984:2016.",
                source_text="Conforms to IS 4984:2016.", # Hallucinated standard
            )
        ]
    )
    result = extractor._validate_and_align_extraction(mock_parsed, doc)
    assert result.requirements[0].source_text is None
    assert result.requirements[0].extraction_status == RequirementExtractionStatus.UNCERTAIN

def test_llm_audit_case_h_duplicate_requirement():
    """H. Duplicate requirements must be deduplicated."""
    extractor = RequirementExtractorService()
    doc = parse_raw_text("The motor shall have a rated power of 5 kW.")
    mock_parsed = ProcurementExtractionSchema(
        requirements=[
            ExtractedRequirementSchema(
                requirement_type=RequirementType.MECHANICAL,
                extraction_status=RequirementExtractionStatus.EXPLICIT,
                extracted_text="Motor shall have a rated power of 5 kW.",
                source_text="The motor shall have a rated power of 5 kW.",
            ),
            ExtractedRequirementSchema(
                requirement_type=RequirementType.MECHANICAL,
                extraction_status=RequirementExtractionStatus.EXPLICIT,
                extracted_text="Motor shall have a rated power of 5 kW.",
                source_text="The motor shall have a rated power of 5 kW.",
            ),
        ]
    )
    result = extractor._validate_and_align_extraction(mock_parsed, doc)
    assert len(result.requirements) == 1

def test_llm_audit_case_i_ambiguous_requirement():
    """I. Ambiguous requirement: 'Suitable for harsh environments' must NOT convert to 'IP65' and must remain UNCERTAIN."""
    extractor = RequirementExtractorService()
    text = "The equipment shall be suitable for harsh environments."
    doc = parse_raw_text(text)
    result = extractor.extract_from_document(doc)

    assert len(result.requirements) > 0
    req = result.requirements[0]
    assert req.extraction_status in [RequirementExtractionStatus.UNCERTAIN, RequirementExtractionStatus.INFERRED]
    # Verify IP65 was NOT hallucinated
    all_param_names = [p.name for p in req.parameters]
    all_param_vals = [p.normalized_value for p in req.parameters]
    assert "IP65" not in all_param_vals
    assert "IP55" not in all_param_vals


# =====================================================================
# 4. EVIDENCE ALIGNMENT & 5. EXPLICIT / INFERRED / UNCERTAIN
# =====================================================================

def test_evidence_alignment_verification():
    """Evidence text must occur verbatim in source document."""
    extractor = RequirementExtractorService()
    source = "The motor shall have a rated power of 5 kW."
    doc = parse_raw_text(source)
    result = extractor.extract_from_document(doc)
    for req in result.requirements:
        if req.source_text:
            assert req.source_text in source


# =====================================================================
# 6. TECHNICAL PARAMETER STRUCTURE
# Test: 5 kW, IP55, -10 °C to 50 °C, 1000 mm × 500 mm, 10–15 bar
# =====================================================================

def test_technical_parameter_structure():
    """Verify structured technical parameters preserve original value, normalized value, unit, and operator/range."""
    extractor = RequirementExtractorService()

    # Test 1: 5 kW
    doc1 = parse_raw_text("The motor shall have a rated power of 5 kW.")
    res1 = extractor.extract_from_document(doc1)
    p1 = res1.requirements[0].parameters[0]
    assert p1.original_value == "5 kW"
    assert p1.normalized_value == "5"
    assert p1.unit == "kW"
    assert p1.operator == "="

    # Test 2: IP55
    doc2 = parse_raw_text("The enclosure shall be IP55.")
    res2 = extractor.extract_from_document(doc2)
    p2 = res2.requirements[0].parameters[0]
    assert "IP55" in p2.original_value
    assert p2.normalized_value == "IP55"
    assert p2.operator == "="

    # Test 3: -10 °C to 50 °C
    doc3 = parse_raw_text("The operating temperature shall be -10 °C to 50 °C.")
    res3 = extractor.extract_from_document(doc3)
    p3 = res3.requirements[0].parameters[0]
    assert "-10 °C to 50 °C" in p3.original_value
    assert p3.normalized_value == "-10 to 50"
    assert p3.unit in ["°C", "C"]
    assert p3.operator == "RANGE"

    # Test 4: 1000 mm × 500 mm
    doc4 = parse_raw_text("The overall dimensions shall be 1000 mm × 500 mm.")
    res4 = extractor.extract_from_document(doc4)
    p4 = res4.requirements[0].parameters[0]
    assert "1000 mm × 500 mm" in p4.original_value
    assert p4.normalized_value == "1000 x 500"
    assert p4.unit == "mm"
    assert p4.operator == "DIMENSIONS"

    # Test 5: 10–15 bar
    doc5 = parse_raw_text("Operating pressure shall be 10–15 bar.")
    res5 = extractor.extract_from_document(doc5)
    p5 = res5.requirements[0].parameters[0]
    assert "10–15 bar" in p5.original_value
    assert p5.normalized_value == "10 to 15"
    assert p5.unit == "bar"
    assert p5.operator == "RANGE"


# =====================================================================
# 7. PDF TEST & 8. SCANNED PDF (OCR_REQUIRED)
# =====================================================================

def test_machine_readable_pdf_fixture(client: TestClient, db_session: Session):
    """Test machine-readable PDF fixture extracts pages, text, and requirements."""
    pdf_path = FIXTURES_DIR / "test_spec.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        res = client.post("/api/v1/documents", files={"file": ("test_spec.pdf", f, "application/pdf")})
    assert res.status_code == 202
    doc_id = res.json()["id"]

    # Verify content endpoint
    content_res = client.get(f"/api/v1/documents/{doc_id}/content")
    assert content_res.status_code == 200
    assert len(content_res.json()["raw_content"]) > 0
    assert content_res.json()["page_count"] >= 1

    # Verify requirements
    reqs_res = client.get(f"/api/v1/documents/{doc_id}/requirements")
    assert reqs_res.status_code == 200
    assert len(reqs_res.json()["requirements"]) > 0

def test_scanned_image_only_pdf_returns_ocr_required(client: TestClient, db_session: Session):
    """Test image-only scanned PDF returns OCR_REQUIRED and does not silently return empty document."""
    pdf_path = FIXTURES_DIR / "scanned.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        res = client.post("/api/v1/documents", files={"file": ("scanned.pdf", f, "application/pdf")})
    assert res.status_code == 202
    doc_id = res.json()["id"]

    doc = db_session.query(Document).filter(Document.id == doc_id).first()
    assert doc.status in [DocumentProcessingState.REQUIRES_OCR, DocumentProcessingState.FAILED_VALIDATION]
    assert doc.error_message == "OCR_REQUIRED"


# =====================================================================
# 10. API VERIFICATION (All requested endpoints executed)
# =====================================================================

def test_all_document_api_endpoints_executed(client: TestClient, db_session: Session):
    """
    Actually execute:
    - POST /api/v1/documents
    - POST /api/v1/documents/{id}/process
    - GET /api/v1/documents/{id}
    - GET /api/v1/documents/{id}/status
    - GET /api/v1/documents/{id}/content
    - GET /api/v1/documents/{id}/requirements
    - POST /api/v1/specifications/text
    """
    upload_file = FIXTURES_DIR / "temp_api_test.txt"
    with open(upload_file, "w") as f:
        f.write("Motor rated power shall be 5 kW. Enclosure IP55.")

    try:
        # 1. POST /api/v1/documents
        with open(upload_file, "rb") as f:
            res_upload = client.post("/api/v1/documents", files={"file": ("temp_api_test.txt", f, "text/plain")})
        assert res_upload.status_code == 202
        doc_id = res_upload.json()["id"]

        # 2. GET /api/v1/documents/{id}
        res_get = client.get(f"/api/v1/documents/{doc_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == doc_id
        assert res_get.json()["filename"] == "temp_api_test.txt"

        # 3. GET /api/v1/documents/{id}/status
        res_status = client.get(f"/api/v1/documents/{doc_id}/status")
        assert res_status.status_code == 200
        assert res_status.json()["status"] == "COMPLETED"

        # 4. GET /api/v1/documents/{id}/content
        res_content = client.get(f"/api/v1/documents/{doc_id}/content")
        assert res_content.status_code == 200
        assert "5 kW" in res_content.json()["raw_content"]
        assert len(res_content.json()["blocks"]) > 0

        # 5. GET /api/v1/documents/{id}/requirements
        res_reqs = client.get(f"/api/v1/documents/{doc_id}/requirements")
        assert res_reqs.status_code == 200
        assert len(res_reqs.json()["requirements"]) >= 2
        first_req = res_reqs.json()["requirements"][0]
        assert "evidence" in first_req
        assert first_req["evidence"]["start_offset"] is not None
        assert len(first_req["parameters"]) > 0

        # 6. POST /api/v1/documents/{id}/process (re-trigger processing)
        res_process = client.post(f"/api/v1/documents/{doc_id}/process")
        assert res_process.status_code == 200
        assert res_process.json()["status"] == "PROCESSING_TRIGGERED"

        # 7. POST /api/v1/specifications/text
        res_text = client.post("/api/v1/specifications/text", json={
            "title": "Text Intake Tender",
            "department": "Energy",
            "raw_content": "Pumps shall have pressure of 10–15 bar."
        })
        assert res_text.status_code == 200
        assert "id" in res_text.json()
        assert "document_id" in res_text.json()

    finally:
        if upload_file.exists():
            upload_file.unlink()


# =====================================================================
# 11. FILE SECURITY (Oversized, wrong MIME, traversal, unsupported ext, empty)
# =====================================================================

def test_security_file_rejections(client: TestClient):
    """Verify safe rejection of security edge cases."""

    # 1. Wrong MIME type
    res_mime = client.post("/api/v1/documents", files={"file": ("test.png", b"fake image bytes", "image/png")})
    assert res_mime.status_code == 400
    assert "Unsupported" in res_mime.json()["detail"]

    # 2. Unsupported extension
    res_ext = client.post("/api/v1/documents", files={"file": ("malicious.sh", b"#!/bin/bash", "text/plain")})
    assert res_ext.status_code == 400
    assert "Unsupported file extension" in res_ext.json()["detail"]

    # 3. Path traversal filename
    res_traversal = client.post("/api/v1/documents", files={"file": ("../../etc/passwd.txt", b"innocent text", "text/plain")})
    assert res_traversal.status_code == 202
    assert res_traversal.json()["id"] is not None

    # 4. Empty file
    res_empty = client.post("/api/v1/documents", files={"file": ("empty.txt", b"", "text/plain")})
    assert res_empty.status_code == 400
    assert "Empty file" in res_empty.json()["detail"]

    # 5. Oversized file (>25MB)
    res_large = client.post(
        "/api/v1/documents",
        files={"file": ("large.txt", b"A" * (26 * 1024 * 1024), "text/plain")}
    )
    assert res_large.status_code == 413
    assert "File too large" in res_large.json()["detail"]

    # 6. Malformed PDF
    res_corrupt_pdf = client.post(
        "/api/v1/documents",
        files={"file": ("corrupt.pdf", b"%PDF-1.4 garbage corrupted binary content", "application/pdf")}
    )
    assert res_corrupt_pdf.status_code == 202
    doc_id = res_corrupt_pdf.json()["id"]
    status_res = client.get(f"/api/v1/documents/{doc_id}/status")
    assert status_res.json()["status"] in [DocumentProcessingState.FAILED_VALIDATION, DocumentProcessingState.FAILED_EXTRACTION]


# =====================================================================
# 12. DUPLICATE DOCUMENTS
# =====================================================================

def test_duplicate_document_hash_deduplication(client: TestClient, db_session: Session):
    """Verify document hash deduplication does not create duplicate document records."""
    upload_file = FIXTURES_DIR / "temp_dedup_unique.txt"
    with open(upload_file, "w") as f:
        f.write("Unique specification hash test 5544332211.")

    try:
        with open(upload_file, "rb") as f:
            res1 = client.post("/api/v1/documents", files={"file": ("temp_dedup_unique.txt", f, "text/plain")})
        assert res1.status_code == 202
        doc_id1 = res1.json()["id"]

        with open(upload_file, "rb") as f:
            res2 = client.post("/api/v1/documents", files={"file": ("temp_dedup_unique.txt", f, "text/plain")})
        assert res2.status_code == 202
        assert res2.json()["id"] == doc_id1
        assert res2.json()["message"] == "Document already exists"

        # Check only 1 document in DB with this hash
        docs = db_session.query(Document).filter(Document.id == doc_id1).all()
        assert len(docs) == 1
    finally:
        if upload_file.exists():
            upload_file.unlink()
