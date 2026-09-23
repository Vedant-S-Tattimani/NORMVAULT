"""
Schemas for Multi-Bidder Comparative Evaluation Engine.
Enables side-by-side compliance matrices, parameter scorecards, and statutory disqualification triggers.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class BidderParameterOffer(BaseModel):
    parameter_name: str = Field(..., description="Name of technical parameter (e.g., Efficiency Class)")
    offered_value: str = Field(..., description="Value offered by the bidder (e.g., IE3 or 94.5%)")
    offered_standard: Optional[str] = Field(None, description="Standard cited by bidder (e.g. IS 12615:2018)")
    test_certificate_ref: Optional[str] = Field(None, description="NABL/BIS Lab test report reference")


class BidderSubmission(BaseModel):
    bidder_name: str = Field(..., description="Legal company/bidder name (e.g. Bharat Heavy Electricals Ltd)")
    bidder_id: str = Field(..., description="Tenderer ID or PAN/GSTIN")
    offered_model: Optional[str] = Field(None, description="Make / Model name")
    bis_license_valid: bool = Field(True, description="Whether bidder holds active BIS ISI/CRS license")
    bis_license_number: Optional[str] = Field(None, description="BIS CML / Registration number")
    parameters: List[BidderParameterOffer] = Field(default_factory=list, description="Offered technical parameters")


class ComparativeEvaluationRequest(BaseModel):
    specification_id: int = Field(..., description="Tender specification ID to benchmark against")
    bidders: List[BidderSubmission] = Field(..., min_length=1, description="List of competing bidder submissions")


class ParameterComplianceDetail(BaseModel):
    parameter_name: str
    tender_specified_value: str
    offered_value: str
    status: str = Field(..., description="COMPLIANT, DEVIATION, NON_COMPLIANT, NOT_OFFERED")
    deviation_reason: Optional[str] = None


class BidderEvaluationResult(BaseModel):
    bidder_name: str
    bidder_id: str
    offered_model: Optional[str] = None
    compliance_score_percent: float = Field(..., ge=0.0, le=100.0)
    is_technically_qualified: bool
    disqualification_reasons: List[str] = Field(default_factory=list)
    superseded_standards_used: List[str] = Field(default_factory=list)
    parameter_evaluations: List[ParameterComplianceDetail] = Field(default_factory=list)


class ComparativeEvaluationResponse(BaseModel):
    specification_id: int
    tender_reference: str
    tender_title: str
    evaluated_at: str
    total_bidders: int
    qualified_bidders_count: int
    disqualified_bidders_count: int
    results: List[BidderEvaluationResult]
