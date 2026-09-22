"""
Service functions for Procurement Specification persistence and lifecycle management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, TechnicalParameter, RequirementEvidence
from app.schemas.extraction import ExtractedRequirementSchema


def persist_extracted_requirements(
    db: Session,
    specification_id: int,
    document_id: Optional[int],
    requirements: List[ExtractedRequirementSchema],
) -> List[Requirement]:
    """
    Consolidated persistence helper for saving extracted requirements, technical parameters,
    and precision document evidence.
    """
    persisted_reqs: List[Requirement] = []
    for req_data in requirements:
        db_req = Requirement(
            specification_id=specification_id,
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

        # Save Precision Evidence
        if req_data.source_text:
            evidence = RequirementEvidence(
                requirement_id=db_req.id,
                document_id=document_id,
                page_number=req_data.page_number or 1,
                section_heading=req_data.section_heading,
                block_identifier=req_data.block_identifier,
                start_offset=req_data.start_offset,
                end_offset=req_data.end_offset,
                source_text=req_data.source_text,
            )
            db.add(evidence)

        persisted_reqs.append(db_req)

    return persisted_reqs
