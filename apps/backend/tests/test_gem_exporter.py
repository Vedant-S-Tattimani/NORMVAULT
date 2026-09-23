"""
Unit tests for Government e-Marketplace (GeM) BOQ & Technical Compliance Exporter.
"""
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.models.requirement import ProcurementSpecification, Requirement, TechnicalParameter, RequirementType
from app.models.standard import IndianStandard, StandardStatus
from app.services.intelligence.package_builder import DecisionPackageBuilder


@pytest.fixture
def client():
    return TestClient(app)


def test_gem_boq_export_endpoints(client: TestClient, db_session):
    # Create test specification and requirement
    spec = ProcurementSpecification(
        title="Procurement of Energy Efficient 15kW Motors",
        department="NTPC Power Division",
        tender_reference="NTPC/GEM/2026/01",
        target_product_name="Three-Phase Induction Motor",
        raw_content="15kW IE3 energy efficient induction motors per IS 12615.",
        status="COMPLETED",
    )
    db_session.add(spec)
    db_session.flush()

    req = Requirement(
        specification_id=spec.id,
        clause_reference="Clause 4.1",
        extracted_text="Motor efficiency shall be class IE3 per IS 12615.",
        requirement_type=RequirementType.TESTING,
    )
    db_session.add(req)
    db_session.flush()

    param = TechnicalParameter(
        requirement_id=req.id,
        name="Efficiency Class",
        original_value="IE3",
        normalized_value="IE3",
        target_value="IE3",
        operator=">=",
        unit="",
        test_method_standard="IS 15999",
    )
    db_session.add(param)

    # Standard
    std = IndianStandard(
        standard_number="IS 12615",
        title="Three-Phase Induction Motors",
        status=StandardStatus.ACTIVE,
        is_mandatory_qco=True,
        qco_reference="DPIIT Order 2024",
    )
    db_session.add(std)
    db_session.commit()

    # Build decision package to create intelligence run
    builder = DecisionPackageBuilder()
    package = builder.build_decision_package(db=db_session, specification=spec, force_new_run=True)
    run_id = package.run.id

    # 1. Test JSON export format
    resp_json = client.get(f"/api/v1/intelligence/runs/{run_id}/export/gem?format=json")
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert data["gem_format_version"] == "GeM-BOQ-v4.0"
    assert "tender_metadata" in data
    assert "boq_parameters" in data
    assert "statutory_undertakings" in data
    assert len(data["statutory_undertakings"]) >= 3
    assert data["boq_parameters"][0]["parameter_name"] == "Efficiency Class"

    # 2. Test CSV export format
    resp_csv = client.get(f"/api/v1/intelligence/runs/{run_id}/export/gem?format=csv")
    assert resp_csv.status_code == 200
    assert resp_csv.headers["content-type"].startswith("text/csv")
    csv_text = resp_csv.text
    assert "GeM Technical BOQ Compliance Schedule" in csv_text
    assert "Item No,Product Category,Parameter Name" in csv_text
