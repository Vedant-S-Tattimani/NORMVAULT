"""
Tests for Multi-Bidder Comparative Evaluation Engine.
Validates side-by-side compliance scoring, parameter deviation flags, and statutory disqualification triggers.
"""
from fastapi.testclient import TestClient
from app.models.requirement import ProcurementSpecification, Requirement, TechnicalParameter, RequirementType
from app.models.standard import IndianStandard, StandardStatus


def test_comparative_evaluation_workflow(client: TestClient, db_session):
    # 1. Setup tender specification
    spec = ProcurementSpecification(
        title="Procurement of High-Efficiency Induction Motors",
        department="BHEL Haridwar Unit",
        tender_reference="BHEL/EM/2026/MOT-01",
        target_product_name="Three-Phase Induction Motor",
        raw_content="Tender requires 30kW induction motors compliant with IS 12615 IE3 efficiency class.",
        status="COMPLETED",
    )
    db_session.add(spec)
    db_session.flush()

    req = Requirement(
        specification_id=spec.id,
        clause_reference="Clause 3.2",
        extracted_text="Motor efficiency shall be class IE3 or better per IS 12615.",
        requirement_type=RequirementType.TESTING,
    )
    db_session.add(req)
    db_session.flush()

    param1 = TechnicalParameter(
        requirement_id=req.id,
        name="Efficiency Class",
        original_value="IE3",
        normalized_value="IE3",
        target_value="IE3",
        operator=">=",
    )
    param2 = TechnicalParameter(
        requirement_id=req.id,
        name="Efficiency Level (%)",
        original_value="93.6",
        normalized_value="93.6",
        target_value="93.6",
        operator=">=",
        unit="%",
    )
    db_session.add_all([param1, param2])

    # Add active standard with mandatory QCO and superseded historical standard
    std_active = IndianStandard(
        standard_number="IS 12615",
        title="Three-Phase Induction Motors",
        status=StandardStatus.ACTIVE,
        is_mandatory_qco=True,
        qco_reference="DPIIT Motors QCO 2024",
    )
    std_old = IndianStandard(
        standard_number="IS 325",
        title="Three-phase induction motors (superseded)",
        status=StandardStatus.SUPERSEDED,
        is_mandatory_qco=False,
    )
    db_session.add_all([std_active, std_old])
    db_session.commit()

    # 2. Prepare 3 competing bidder submissions
    payload = {
        "specification_id": spec.id,
        "bidders": [
            {
                "bidder_name": "Apex Electric Ltd",
                "bidder_id": "BIDDER-001",
                "offered_model": "UltraEff-30kW",
                "bis_license_valid": True,
                "bis_license_number": "CM/L-1234567",
                "parameters": [
                    {
                        "parameter_name": "Efficiency Class",
                        "offered_value": "IE4",  # Superior
                        "offered_standard": "IS 12615:2018",
                    },
                    {
                        "parameter_name": "Efficiency Level (%)",
                        "offered_value": "94.2",  # Above 93.6
                        "offered_standard": "IS 12615:2018",
                    },
                ],
            },
            {
                "bidder_name": "Heritage Motors Corp",
                "bidder_id": "BIDDER-002",
                "offered_model": "ClassicInd-30kW",
                "bis_license_valid": True,
                "parameters": [
                    {
                        "parameter_name": "Efficiency Class",
                        "offered_value": "IE1",  # Sub-standard
                        "offered_standard": "IS 325:1996",  # Superseded standard
                    },
                    {
                        "parameter_name": "Efficiency Level (%)",
                        "offered_value": "88.0",  # Below 93.6
                    },
                ],
            },
            {
                "bidder_name": "Unlicensed Power Co",
                "bidder_id": "BIDDER-003",
                "offered_model": "Budget-30kW",
                "bis_license_valid": False,  # Missing BIS license under mandatory QCO!
                "parameters": [
                    {
                        "parameter_name": "Efficiency Class",
                        "offered_value": "IE3",
                    },
                    {
                        "parameter_name": "Efficiency Level (%)",
                        "offered_value": "93.6",
                    },
                ],
            },
        ],
    }

    # 3. Post to comparative evaluation endpoint
    response = client.post("/api/v1/intelligence/comparative-evaluation", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["specification_id"] == spec.id
    assert data["total_bidders"] == 3
    assert data["qualified_bidders_count"] == 1
    assert data["disqualified_bidders_count"] == 2

    # Check winner (Apex Electric Ltd)
    winner = data["results"][0]
    assert winner["bidder_name"] == "Apex Electric Ltd"
    assert winner["is_technically_qualified"] is True
    assert winner["compliance_score_percent"] == 100.0
    assert len(winner["disqualification_reasons"]) == 0

    # Check disqualified bidders
    heritage = next(b for b in data["results"] if b["bidder_name"] == "Heritage Motors Corp")
    assert heritage["is_technically_qualified"] is False
    assert len(heritage["superseded_standards_used"]) > 0
    assert any("superseded" in r.lower() for r in heritage["disqualification_reasons"])

    unlicensed = next(b for b in data["results"] if b["bidder_name"] == "Unlicensed Power Co")
    assert unlicensed["is_technically_qualified"] is False
    assert any("BIS ISI Mark" in r for r in unlicensed["disqualification_reasons"])
