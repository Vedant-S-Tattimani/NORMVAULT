import hashlib
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload, selectinload
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
from app.services.specification_service import persist_extracted_requirements

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

    persist_extracted_requirements(db, spec.id, doc.id, extraction_result.requirements)

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


@router.get("", summary="List All Procurement Specifications")
@router.get("/", summary="List All Procurement Specifications")
def list_specifications(db: Session = Depends(get_db)):
    specs = (
        db.query(ProcurementSpecification)
        .options(
            joinedload(ProcurementSpecification.document),
            selectinload(ProcurementSpecification.requirements),
        )
        .order_by(ProcurementSpecification.id.asc())
        .all()
    )
    results = []
    for s in specs:
        req_count = len(s.requirements)
        has_uncertain = any(
            (hasattr(r.extraction_status, "value") and r.extraction_status.value in ["UNCERTAIN", "UNRESOLVED"])
            or str(r.extraction_status) in ["UNCERTAIN", "UNRESOLVED"]
            for r in s.requirements
        )
        status_val = "ACTION_REQUIRED" if (has_uncertain or s.status == "ACTION_REQUIRED") else "READY_FOR_TENDER"
        if s.status == "AUDIT_READY":
            status_val = "AUDIT_READY"

        results.append({
            "id": s.id,
            "tender_reference": s.tender_reference or f"TENDER/NV/{s.id:04d}",
            "title": s.title,
            "issuing_organization": s.department or "Central Procurement Entity",
            "estimated_value_inr": None,
            "submission_deadline": None,
            "status": status_val,
            "file_name": s.document.filename if s.document else f"Spec_{s.id}.txt",
            "file_hash_sha256": s.document.file_hash if s.document else None,
            "total_requirements_count": req_count,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return results


@router.get("/{id}", summary="Get Procurement Specification by ID")
def get_specification(id: int, db: Session = Depends(get_db)):
    s = (
        db.query(ProcurementSpecification)
        .options(
            joinedload(ProcurementSpecification.document),
            selectinload(ProcurementSpecification.requirements),
        )
        .filter(ProcurementSpecification.id == id)
        .first()
    )
    if not s:
        raise HTTPException(status_code=404, detail=f"Specification with ID {id} not found.")

    req_count = len(s.requirements)
    return {
        "id": s.id,
        "tender_reference": s.tender_reference or f"TENDER/NV/{s.id:04d}",
        "title": s.title,
        "department": s.department,
        "target_product_name": s.target_product_name,
        "issuing_organization": s.department or "Central Procurement Entity",
        "status": s.status,
        "raw_content": s.raw_content,
        "file_name": s.document.filename if s.document else f"Spec_{s.id}.txt",
        "file_hash_sha256": s.document.file_hash if s.document else None,
        "total_requirements_count": req_count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


@router.get("/{id}/requirements", summary="List Requirements for Specification")
def get_specification_requirements(id: int, db: Session = Depends(get_db)):
    s = db.query(ProcurementSpecification).filter(ProcurementSpecification.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Specification with ID {id} not found.")

    reqs = (
        db.query(Requirement)
        .options(
            joinedload(Requirement.evidence),
            selectinload(Requirement.parameters),
        )
        .filter(Requirement.specification_id == s.id)
        .order_by(Requirement.id.asc())
        .all()
    )
    results = []
    for idx, r in enumerate(reqs, start=1):
        ev = r.evidence
        is_conflict = (
            (hasattr(r.extraction_status, "value") and r.extraction_status.value == "UNCERTAIN")
            or str(r.extraction_status) == "UNCERTAIN"
            or "conflict" in (r.extracted_text or "").lower()
        )
        
        type_val = r.requirement_type.value if hasattr(r.requirement_type, "value") else str(r.requirement_type)
        category_title = type_val.replace("_", " ").title()

        results.append({
            "id": r.id,
            "specification_id": s.id,
            "requirement_code": f"REQ-{idx:03d}",
            "title": r.clause_reference or f"Requirement {idx}: {category_title}",
            "category": category_title,
            "section_citation": ev.section_heading if (ev and ev.section_heading) else (r.clause_reference or "Section IV"),
            "page_number": ev.page_number if ev else 1,
            "verbatim_excerpt": r.extracted_text,
            "cryptographic_offset": f"sha256:{s.document.file_hash[:8] if (s.document and s.document.file_hash) else '4a8b1c'} [P.{ev.page_number if ev else 1}]",
            "has_conflict": is_conflict,
            "conflict_description": "Contradictory values or non-standard specification parameter detected in tender document." if is_conflict else None,
            "parameters": [
                {
                    "name": p.name,
                    "value": p.original_value or p.target_value or "",
                    "unit": p.unit,
                    "tolerance": p.tolerance,
                    "is_mandatory": True,
                }
                for p in r.parameters
            ],
        })

    return results


