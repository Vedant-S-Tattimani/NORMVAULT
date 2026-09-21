import hashlib
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from pydantic import BaseModel
from app.models.document import Document, DocumentProcessingState
from app.models.requirement import (
    ProcurementSpecification,
    Requirement,
    RequirementEvidence,
    TechnicalParameter,
)
from app.services.document_parser import parse_raw_text
from app.services.requirement_extractor import RequirementExtractorService

router = APIRouter()

class TextIntakeRequest(BaseModel):
    title: str
    department: str = ""
    tender_reference: str = ""
    target_product_name: str = ""
    raw_content: str

@router.post("/text", status_code=status.HTTP_200_OK)
def process_text_specification(req: TextIntakeRequest, db: Session = Depends(get_db)):
    if not req.raw_content.strip():
        raise HTTPException(status_code=400, detail="Empty specification content provided.")

    normalized_doc = parse_raw_text(req.raw_content)
    
    extractor = RequirementExtractorService()
    extraction_result = extractor.extract_from_document(normalized_doc)
    
    # Create backing Document record for provenance and consistent API retrieval
    content_bytes = req.raw_content.encode("utf-8")
    doc_hash = hashlib.sha256(content_bytes).hexdigest()
    
    doc = db.query(Document).filter(Document.file_hash == doc_hash).first()
    if not doc:
        doc = Document(
            filename=f"TextSpec_{req.title[:32].strip().replace(' ', '_')}.txt",
            mime_type="text/plain",
            file_size=len(content_bytes),
            file_hash=doc_hash,
            page_count=1,
            status=DocumentProcessingState.COMPLETED
        )
        db.add(doc)
        db.flush()

    spec = ProcurementSpecification(
        document_id=doc.id,
        title=req.title or extraction_result.title or "Specification Intake",
        department=req.department,
        tender_reference=req.tender_reference,
        target_product_name=req.target_product_name or extraction_result.target_product_name,
        raw_content=req.raw_content,
        source_format="TEXT",
        status="COMPLETED"
    )
    db.add(spec)
    db.flush()

    for req_data in extraction_result.requirements:
        db_req = Requirement(
            specification_id=spec.id,
            requirement_type=req_data.requirement_type,
            extraction_status=req_data.extraction_status,
            extracted_text=req_data.extracted_text,
        )
        db.add(db_req)
        db.flush()

        # Save Technical Parameters
        for p_data in req_data.parameters:
            param = TechnicalParameter(
                requirement_id=db_req.id,
                name=p_data.name,
                original_value=p_data.original_value or p_data.target_value or "",
                normalized_value=p_data.normalized_value or p_data.target_value or "",
                target_value=p_data.target_value or p_data.normalized_value or "",
                unit=p_data.unit,
                operator=p_data.operator,
                tolerance=p_data.tolerance,
                test_method_standard=p_data.test_method_standard,
            )
            db.add(param)
        
        # Save Evidence
        if req_data.source_text:
            evidence = RequirementEvidence(
                requirement_id=db_req.id,
                document_id=doc.id,
                page_number=req_data.page_number or 1,
                section_heading=req_data.section_heading,
                block_identifier=req_data.block_identifier,
                start_offset=req_data.start_offset,
                end_offset=req_data.end_offset,
                source_text=req_data.source_text,
            )
            db.add(evidence)
        
    db.commit()
    db.refresh(spec)

    req_list = []
    for r in db.query(Requirement).filter(Requirement.specification_id == spec.id).all():
        ev = r.evidence
        params = [
            {
                "id": p.id,
                "name": p.name,
                "original_value": p.original_value,
                "normalized_value": p.normalized_value,
                "target_value": p.target_value,
                "unit": p.unit,
                "operator": p.operator,
                "tolerance": p.tolerance,
                "test_method_standard": p.test_method_standard,
            }
            for p in r.parameters
        ]
        req_list.append({
            "id": r.id,
            "type": r.requirement_type.value if hasattr(r.requirement_type, "value") else str(r.requirement_type),
            "status": r.extraction_status.value if hasattr(r.extraction_status, "value") else str(r.extraction_status),
            "text": r.extracted_text,
            "parameters": params,
            "evidence": {
                "page": ev.page_number if ev else None,
                "section": ev.section_heading if ev else None,
                "block_identifier": ev.block_identifier if ev else None,
                "start_offset": ev.start_offset if ev else None,
                "end_offset": ev.end_offset if ev else None,
                "source_text": ev.source_text if ev else None,
            } if ev else None,
        })
    
    return {
        "id": spec.id,
        "document_id": doc.id,
        "status": spec.status,
        "requirements_count": len(extraction_result.requirements),
        "requirements": req_list,
    }

