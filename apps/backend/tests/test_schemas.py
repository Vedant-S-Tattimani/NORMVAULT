"""
Unit tests validating Pydantic schemas and boundary input validation.
"""

import pytest
from pydantic import ValidationError
from app.schemas.analysis import SpecificationCreate, TechnicalParameterBase
from app.models.standard import StandardStatus
from app.models.requirement import RequirementType


def test_specification_create_valid():
    spec = SpecificationCreate(
        title="Procurement of HDPE Pipes for Municipal Water Supply",
        department="State Water Supply & Sewerage Board",
        tender_reference="NIT-2026-WTR-049",
        target_product_name="High Density Polyethylene (HDPE) Pipes",
        raw_content="Supply of PE-100 grade HDPE pipes conforming to relevant Indian Standards.",
    )
    assert spec.title.startswith("Procurement")
    assert spec.target_product_name == "High Density Polyethylene (HDPE) Pipes"


def test_specification_create_rejects_empty_content():
    with pytest.raises(ValidationError):
        SpecificationCreate(
            title="Short",
            raw_content="tiny",  # Less than min_length=10
        )


def test_technical_parameter_validation():
    param = TechnicalParameterBase(
        name="Melt Flow Rate (MFR)",
        operator="<=",
        target_value="1.10",
        unit="g/10 min",
        test_method_standard="IS 2530",
    )
    assert param.name == "Melt Flow Rate (MFR)"
    assert param.target_value == "1.10"
