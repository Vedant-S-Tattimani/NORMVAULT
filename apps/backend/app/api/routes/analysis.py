"""
Specification requirement extraction and analysis endpoints (Phase 2+).
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.analysis import SpecificationCreate

router = APIRouter()


@router.post(
    "/extract",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Extract Requirements from Specification",
    description="Extracts atomic technical parameters and clauses from tender specifications. Scheduled for Phase 2.",
)
def extract_requirements(payload: SpecificationCreate) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Requirement extraction and NLP pipeline will be activated in Phase 2.",
    )
