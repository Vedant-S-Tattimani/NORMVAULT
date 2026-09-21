"""
Phase 2 Final Acceptance Test Suite Extension.
Tests multi-page PDF boundaries, FAILED_EXTRACTION transitions, null-byte injection,
and strict evidence span isolation across sections.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentProcessingState
from app.models.requirement import RequirementType, RequirementExtractionStatus
from app.schemas.extraction import ProcurementExtractionSchema, ExtractedRequirementSchema
from app.services.document_parser import PdfParser, parse_raw_text
from app.services.requirement_extractor import RequirementExtractorService

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_multipage_pdf_page_boundaries(client: TestClient, db_session: Session):
    """
    Criterion 7: Multi-page PDF parsing verification.
    Verifies page boundaries, page numbers (page 1 vs page 2), block IDs, and distinct evidence spans.
    """
    pdf_path = FIXTURES_DIR / "multipage_spec.pdf"
    assert pdf_path.exists(), "multipage_spec.pdf must exist"

    with open(pdf_path, "rb") as f:
        res = client.post("/api/v1/documents", files={"file": ("multipage_spec.pdf", f, "application/pdf")})
    assert res.status_code == 202
    doc_id = res.json()["id"]

    # 1. Content endpoint verification
    content_res = client.get(f"/api/v1/documents/{doc_id}/content")
    assert content_res.status_code == 200
    content_data = content_res.json()
    assert content_data["page_count"] == 2
    assert len(content_data["blocks"]) >= 2
    assert content_data["blocks"][0]["page_number"] == 1
    assert content_data["blocks"][1]["page_number"] == 2

    # 2. Requirements endpoint verification
    reqs_res = client.get(f"/api/v1/documents/{doc_id}/requirements")
    assert reqs_res.status_code == 200
    reqs = reqs_res.json()["requirements"]
    assert len(reqs) >= 2

    # Verify Page 1 requirement
    req_p1 = next((r for r in reqs if "5 kW" in r["text"] or "5 kW" in (r.get("evidence", {}) or {}).get("source_text", "")), None)
    assert req_p1 is not None
    assert req_p1["evidence"] is not None
    assert req_p1["evidence"]["page"] == 1
    assert "p1" in req_p1["evidence"]["block_identifier"]

    # Verify Page 2 requirement
    req_p2 = next((r for r in reqs if "IP55" in r["text"] or "IP55" in (r.get("evidence", {}) or {}).get("source_text", "")), None)
    assert req_p2 is not None
    assert req_p2["evidence"] is not None
    assert req_p2["evidence"]["page"] == 2
    assert "p2" in req_p2["evidence"]["block_identifier"]

    # Spans must not cross page boundaries or overlap
    assert req_p1["evidence"]["start_offset"] < req_p1["evidence"]["end_offset"]
    assert req_p2["evidence"]["start_offset"] > req_p1["evidence"]["end_offset"]


def test_failed_extraction_lifecycle_transition(client: TestClient, db_session: Session):
    """
    Criterion 9: Verify FAILED_EXTRACTION state transition when extraction raises an unexpected error.
    """
    upload_file = FIXTURES_DIR / "temp_fail_extract.txt"
    with open(upload_file, "w") as f:
        f.write("Some text to extract.")

    try:
        # We simulate extraction failure by creating a document and calling pipeline with corrupted extractor
        from app.api.routes.documents import execute_document_pipeline
        doc = Document(
            filename="temp_fail_extract.txt",
            mime_type="text/plain",
            file_size=21,
            file_hash="mock_fail_hash_12345",
            status=DocumentProcessingState.UPLOADED,
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)

        # Monkeypatch extractor to raise error
        import app.api.routes.documents as docs_module
        orig_extractor_cls = docs_module.RequirementExtractorService

        class BuggyExtractor:
            def extract_from_document(self, *args, **kwargs):
                raise RuntimeError("Simulated internal NLP engine failure.")

        docs_module.RequirementExtractorService = BuggyExtractor
        try:
            execute_document_pipeline(doc.id, str(upload_file), "text/plain", db=db_session)
        finally:
            docs_module.RequirementExtractorService = orig_extractor_cls

        db_session.refresh(doc)
        assert doc.status == DocumentProcessingState.FAILED_EXTRACTION
        assert "Extraction failed" in (doc.error_message or "")

        # Verify via status endpoint
        res = client.get(f"/api/v1/documents/{doc.id}/status")
        assert res.status_code == 200
        assert res.json()["status"] == "FAILED_EXTRACTION"
        assert "Extraction failed" in res.json()["error"]
    finally:
        if upload_file.exists():
            upload_file.unlink()


def test_null_byte_filename_rejection(client: TestClient):
    """
    Criterion 11: Malicious filename with null byte is safely rejected.
    """
    res = client.post(
        "/api/v1/documents",
        files={"file": ("malicious\x00name.txt", b"Test payload", "text/plain")}
    )
    assert res.status_code == 400
    assert "Invalid filename" in res.json()["detail"]


def test_smallest_practical_span_multi_sentence_paragraph():
    """
    Criterion 2: In a paragraph with 3 sentences, each requirement evidence points
    EXACTLY to its own sentence and NOT the entire paragraph.
    """
    para = (
        "Section 3.1 Equipment Specifications. "
        "The pump casing shall withstand a hydrostatic test pressure of 24 bar. "
        "The impeller shall be dynamically balanced to grade 6.3. "
        "All exposed fasteners shall be grade 316 stainless steel."
    )
    doc = parse_raw_text(para)
    extractor = RequirementExtractorService()
    result = extractor.extract_from_document(doc)

    assert len(result.requirements) >= 2
    for req in result.requirements:
        if req.source_text:
            # Must be strictly shorter than the whole paragraph
            assert len(req.source_text) < len(para)
            assert req.source_text in para
            assert req.start_offset is not None
            assert req.end_offset is not None
            assert para[req.start_offset:req.end_offset] == req.source_text
