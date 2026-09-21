import pytest
from pydantic import ValidationError
from app.schemas.extraction import ProcurementExtractionSchema, ExtractedRequirementSchema, ExtractedParameterSchema
from app.models.requirement import RequirementType, RequirementExtractionStatus
from app.services.requirement_extractor import RequirementExtractorService
from app.services.document_parser import NormalizedDocument, NormalizedBlock

def test_valid_structured_response():
    data = {
        "title": "Test Doc",
        "target_product_name": "Motor",
        "requirements": [
            {
                "requirement_type": "MECHANICAL",
                "extraction_status": "EXPLICIT",
                "extracted_text": "Rated power 5 kW",
                "source_text": "The motor shall have a rated power of 5 kW.",
                "page_number": 1,
                "parameters": [
                    {
                        "name": "Power",
                        "target_value": "5",
                        "unit": "kW",
                        "operator": "="
                    }
                ]
            }
        ]
    }
    schema = ProcurementExtractionSchema(**data)
    assert schema.title == "Test Doc"
    assert len(schema.requirements) == 1
    assert schema.requirements[0].parameters[0].unit == "kW"


def test_missing_required_field():
    data = {
        "title": "Test Doc",
        "target_product_name": "Motor",
        "requirements": [
            {
                # Missing extracted_text
                "requirement_type": "MECHANICAL",
                "extraction_status": "EXPLICIT",
            }
        ]
    }
    with pytest.raises(ValidationError):
        ProcurementExtractionSchema(**data)


def test_invalid_enum():
    data = {
        "title": "Test Doc",
        "target_product_name": "Motor",
        "requirements": [
            {
                "requirement_type": "INVALID_TYPE",
                "extraction_status": "EXPLICIT",
                "extracted_text": "Rated power 5 kW",
            }
        ]
    }
    with pytest.raises(ValidationError):
        ProcurementExtractionSchema(**data)


def test_hallucinated_evidence_rejection():
    # If the LLM generates evidence that doesn't exist in the document, it should be rejected.
    extractor = RequirementExtractorService()
    
    doc = NormalizedDocument(
        full_text="The motor shall have a rated power of 5 kW.",
        blocks=[NormalizedBlock(page_number=1, text="The motor shall have a rated power of 5 kW.", section_heading=None)]
    )
    
    # Mocking the parsed LLM result that hallucinated source_text
    hallucinated_req = ExtractedRequirementSchema(
        requirement_type=RequirementType.MECHANICAL,
        extraction_status=RequirementExtractionStatus.EXPLICIT,
        extracted_text="Requires 10 kW.",
        source_text="The motor shall have a rated power of 10 kW." # Hallucination!
    )
    
    mock_parsed = ProcurementExtractionSchema(
        title="Test",
        target_product_name="Test",
        requirements=[hallucinated_req]
    )
    
    # Monkeypatch the extraction to return the hallucinated result so we can test the alignment filter
    extractor._fallback_extract = lambda doc: mock_parsed
    
    result = extractor.extract_from_document(doc)
    
    req = result.requirements[0]
    # Evidence should be stripped because it was hallucinated
    assert req.source_text is None
    # Explicit status should be downgraded to uncertain because evidence failed
    assert req.extraction_status == RequirementExtractionStatus.UNCERTAIN

