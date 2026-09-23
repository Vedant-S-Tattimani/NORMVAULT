import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.models.document import Document, DocumentProcessingState
from app.models.requirement import (
    ProcurementSpecification,
    Requirement,
    RequirementEvidence,
    TechnicalParameter,
)
from app.services.document_parser import get_document_parser, hash_file, parse_raw_text
from app.services.requirement_extractor import RequirementExtractorService
from app.services.specification_service import persist_extracted_requirements

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
ALLOWED_MIMES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


def execute_document_pipeline(doc_id: int, file_path: str, mime_type: str, db: Optional[Session] = None):
    """
    Executes the real document processing lifecycle:
    UPLOADED -> VALIDATING -> EXTRACTING -> STRUCTURING -> ANALYZING -> COMPLETED
    Or FAILED_VALIDATION / FAILED_EXTRACTION / REQUIRES_OCR on error.
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            return

        # Step 1: VALIDATING
        document.status = DocumentProcessingState.VALIDATING
        db.commit()

        if not os.path.exists(file_path):
            document.status = DocumentProcessingState.FAILED_VALIDATION
            document.error_message = "File not found on storage."
            db.commit()
            return

        parser = get_document_parser(mime_type)
        try:
            normalized_doc = parser.parse(file_path, mime_type)
        except ValueError as ve:
            error_str = str(ve)
            if error_str == "OCR_REQUIRED":
                document.status = DocumentProcessingState.REQUIRES_OCR
                document.error_message = "OCR_REQUIRED"
                db.commit()
                return
            else:
                document.status = DocumentProcessingState.FAILED_VALIDATION
                document.error_message = f"Validation failed: {error_str}"
                db.commit()
                return

        document.page_count = normalized_doc.page_count

        # Step 2: EXTRACTING
        document.status = DocumentProcessingState.EXTRACTING
        db.commit()

        extractor = RequirementExtractorService()
        extraction_result = extractor.extract_from_document(normalized_doc)

        # Step 3: STRUCTURING
        document.status = DocumentProcessingState.STRUCTURING
        db.commit()

        # Delete any previous specifications/requirements for this document (e.g. on re-process)
        existing_specs = db.query(ProcurementSpecification).filter(
            ProcurementSpecification.document_id == document.id
        ).all()
        for s in existing_specs:
            db.delete(s)
        db.flush()

        spec = ProcurementSpecification(
            document_id=document.id,
            title=extraction_result.title or document.filename,
            target_product_name=extraction_result.target_product_name,
            raw_content=normalized_doc.full_text,
            source_format="DOCUMENT",
            status="STRUCTURING"
        )
        db.add(spec)
        db.flush()

        # Step 4: Save Requirements, Parameters, and Evidence
        persist_extracted_requirements(db, spec.id, document.id, extraction_result.requirements)

        # Step 5: ANALYZING (Consistency and validation checks)
        document.status = DocumentProcessingState.ANALYZING
        spec.status = "ANALYZING"
        db.commit()

        # Finalize
        spec.status = "COMPLETED"
        document.status = DocumentProcessingState.COMPLETED
        document.error_message = None
        db.commit()

    except Exception as e:
        db.rollback()
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            document.status = DocumentProcessingState.FAILED_EXTRACTION
            document.error_message = f"Extraction failed: {str(e)}"
            db.commit()
    finally:
        if own_session:
            db.close()


async def _handle_upload_core(file: UploadFile, background_tasks: BackgroundTasks, db: Session):
    # Security 1: Filename validation and sanitization
    import urllib.parse
    raw_filename = file.filename or ""
    unquoted = urllib.parse.unquote(raw_filename)
    # Reject null bytes both literal and url-encoded
    if "\x00" in raw_filename or "\x00" in unquoted or "%00" in raw_filename.lower():
        raise HTTPException(status_code=400, detail="Invalid filename characters.")
    
    clean_filename = os.path.basename(raw_filename.replace("\\", "/"))
    clean_filename = clean_filename.replace("..", "").strip()
    if not clean_filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    file_ext = os.path.splitext(clean_filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {file_ext}. Allowed: .pdf, .txt")

    # Security 2: Content-type MIME validation
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.content_type}. Allowed: application/pdf, text/plain")

    # Security 3: Safe storage with isolated unique filename to prevent path traversal
    safe_stored_name = f"{uuid.uuid4().hex}_{clean_filename}"
    temp_path = UPLOAD_DIR / safe_stored_name

    # Pre-check size if provided
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 25MB.")

    # Security 4: Stream read and size constraint check (Max 25MB)
    written_bytes = 0
    too_large = False
    try:
        with open(temp_path, "wb") as buffer:
            while chunk := await file.read(8192):
                written_bytes += len(chunk)
                if written_bytes > MAX_FILE_SIZE:
                    too_large = True
                    break
                buffer.write(chunk)
    except Exception as e:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to store file: {str(e)}")

    if too_large:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 25MB.")


    if written_bytes == 0:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    # Hash file for deduplication
    file_hash = hash_file(str(temp_path))

    # Duplicate check: return existing record if already processed
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        temp_path.unlink(missing_ok=True)
        return {"id": existing.id, "status": existing.status, "message": "Document already exists"}

    file_size = os.path.getsize(temp_path)

    doc = Document(
        filename=clean_filename,
        mime_type=file.content_type,
        file_size=file_size,
        file_hash=file_hash,
        status=DocumentProcessingState.UPLOADED
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(execute_document_pipeline, doc.id, str(temp_path), file.content_type)

    return {"id": doc.id, "status": doc.status}


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Document (Standard Endpoint)",
)
async def upload_document_standard(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await _handle_upload_core(file, background_tasks, db)


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Document (Legacy Alias)",
)
async def upload_document_legacy(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await _handle_upload_core(file, background_tasks, db)


@router.post("/{id}/process", summary="Trigger or re-trigger document processing")
def process_document(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Find the file in upload dir
    file_matches = list(UPLOAD_DIR.glob(f"*_{doc.filename}"))
    if not file_matches:
        # Fallback to direct filename match
        direct = UPLOAD_DIR / doc.filename
        if direct.exists():
            file_matches = [direct]

    if not file_matches:
        raise HTTPException(status_code=404, detail="Physical document file missing on server")

    file_path = str(file_matches[0])
    background_tasks.add_task(execute_document_pipeline, doc.id, file_path, doc.mime_type)
    return {"id": doc.id, "status": "PROCESSING_TRIGGERED"}


@router.get("/{id}", summary="Get Document Details")
def get_document(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "mime_type": doc.mime_type,
        "file_size": doc.file_size,
        "file_hash": doc.file_hash,
        "page_count": doc.page_count,
        "status": doc.status,
        "error_message": doc.error_message,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }


@router.get("/{id}/status", summary="Get Document Processing Status")
def get_document_status(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "status": doc.status,
        "error": doc.error_message,
        "page_count": doc.page_count,
    }


@router.get("/{id}/content", summary="Get Extracted Document Content and Blocks")
def get_document_content(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    spec = db.query(ProcurementSpecification).filter(ProcurementSpecification.document_id == id).first()
    raw_content = spec.raw_content if spec else ""

    # Check for original physical file to retain exact page numbers and block identifiers
    normalized = None
    file_matches = list(UPLOAD_DIR.glob(f"*_{doc.filename}"))
    if not file_matches:
        direct = UPLOAD_DIR / doc.filename
        if direct.exists():
            file_matches = [direct]

    if file_matches and os.path.exists(str(file_matches[0])):
        try:
            parser = get_document_parser(doc.mime_type)
            normalized = parser.parse(str(file_matches[0]), doc.mime_type)
        except Exception:
            normalized = None

    if normalized is None and raw_content:
        normalized = parse_raw_text(raw_content)

    blocks_data = [
        {
            "page_number": b.page_number,
            "section_heading": b.section_heading,
            "block_id": b.block_id,
            "start_offset": b.start_offset,
            "end_offset": b.end_offset,
            "text": b.text,
        }
        for b in (normalized.blocks if normalized else [])
    ]

    return {
        "id": doc.id,
        "filename": doc.filename,
        "page_count": doc.page_count or (normalized.page_count if normalized else 1),
        "raw_content": normalized.full_text if normalized else raw_content,
        "blocks": blocks_data,
    }


@router.get("/{id}/requirements", summary="Get Extracted Requirements and Precision Evidence")
def get_document_requirements(id: int, db: Session = Depends(get_db)):
    # Support lookup by document_id or specification_id
    spec = db.query(ProcurementSpecification).filter(
        (ProcurementSpecification.document_id == id) | (ProcurementSpecification.id == id)
    ).first()

    if not spec:
        # Check if doc exists
        doc = db.query(Document).filter(Document.id == id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"document_id": id, "specification_id": None, "title": doc.filename, "requirements": []}

    reqs = db.query(Requirement).filter(Requirement.specification_id == spec.id).all()
    results = []
    for r in reqs:
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
        results.append({
            "id": r.id,
            "type": r.requirement_type,
            "status": r.extraction_status,
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
        "document_id": spec.document_id,
        "specification_id": spec.id,
        "title": spec.title,
        "target_product_name": spec.target_product_name,
        "requirements": results,
    }


