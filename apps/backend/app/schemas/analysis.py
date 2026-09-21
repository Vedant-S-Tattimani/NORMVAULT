"""
Pydantic schemas for Procurement Specification Ingestion and Requirement Extraction.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.requirement import RequirementType


class TechnicalParameterBase(BaseModel):
    name: str = Field(..., description="Parameter name, e.g. 'Tensile Strength'")
    operator: Optional[str] = Field(None, description="Comparison operator, e.g. '>='")
    target_value: str = Field(..., description="Expected value or range")
    unit: Optional[str] = Field(None, description="Physical unit, e.g. 'MPa'")
    tolerance: Optional[str] = None
    test_method_standard: Optional[str] = None


class TechnicalParameterRead(TechnicalParameterBase):
    id: int
    requirement_id: int

    model_config = ConfigDict(from_attributes=True)


class RequirementRead(BaseModel):
    id: int
    clause_reference: Optional[str] = None
    requirement_type: RequirementType
    extracted_text: str
    normalized_summary: Optional[str] = None
    parameters: List[TechnicalParameterRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SpecificationCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=512, description="Tender or specification title")
    department: Optional[str] = Field(None, max_length=256, description="Procuring authority or department")
    tender_reference: Optional[str] = Field(None, max_length=128, description="Tender/GeM identification number")
    target_product_name: Optional[str] = Field(None, max_length=256, description="Target item or service name")
    raw_content: str = Field(..., min_length=10, description="Full text or pasted technical schedule")


class SpecificationRead(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    tender_reference: Optional[str] = None
    target_product_name: Optional[str] = None
    source_format: str
    created_at: datetime
    requirements: List[RequirementRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
