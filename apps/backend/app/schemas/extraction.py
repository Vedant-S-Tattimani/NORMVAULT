from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.requirement import RequirementType, RequirementExtractionStatus

class ExtractedParameterSchema(BaseModel):
    name: str = Field(..., description="Name of the parameter, e.g. Rated Power")
    original_value: Optional[str] = Field(None, description="Original verbatim value as appeared in text, e.g. 5 kW, 10–15 bar")
    normalized_value: Optional[str] = Field(None, description="Normalized numeric or standard value, e.g. 5, 10 to 15")
    target_value: Optional[str] = Field(None, description="Target value for backwards compatibility")
    unit: Optional[str] = Field(None, description="Unit of measurement, e.g. kW, °C, mm, bar")
    operator: Optional[str] = Field(None, description="Operator or condition, e.g. =, >=, <=, RANGE")
    tolerance: Optional[str] = Field(None, description="Tolerance if mentioned, e.g. ±10%")
    test_method_standard: Optional[str] = Field(None, description="Any explicit test method or standard mentioned for this parameter")

    def model_post_init(self, __context):
        if self.target_value is None:
            self.target_value = self.normalized_value or self.original_value or ""
        if self.normalized_value is None:
            self.normalized_value = self.target_value or ""
        if self.original_value is None:
            self.original_value = self.target_value or ""

class ExtractedRequirementSchema(BaseModel):
    requirement_type: RequirementType = Field(..., description="Category of the requirement")
    extraction_status: RequirementExtractionStatus = Field(..., description="Whether explicitly stated or inferred")
    extracted_text: str = Field(..., description="A concise summary of the requirement")
    source_text: Optional[str] = Field(None, description="Verbatim text from the document serving as evidence")
    page_number: Optional[int] = Field(None, description="Page number where this requirement was found")
    section_heading: Optional[str] = Field(None, description="Section heading under which this requirement was found")
    block_identifier: Optional[str] = Field(None, description="Paragraph or block identifier")
    start_offset: Optional[int] = Field(None, description="Start character offset in source text")
    end_offset: Optional[int] = Field(None, description="End character offset in source text")
    parameters: List[ExtractedParameterSchema] = Field(default_factory=list, description="Any quantifiable or specific technical parameters")


class ProcurementExtractionSchema(BaseModel):
    title: Optional[str] = Field(None, description="Overall title of the procurement specification")
    target_product_name: Optional[str] = Field(None, description="The main product being procured")
    requirements: List[ExtractedRequirementSchema] = Field(default_factory=list, description="List of all extracted requirements")
