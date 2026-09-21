"""
Unit and integration tests for Standards Dependency, Normative References & Compliance Intelligence (Phase 5).
"""

import json
from pathlib import Path
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.standard import IndianStandard, StandardEdition, StandardStatus
from app.models.clause import Clause
from app.models.reference import NormativeReference, ReferenceType, ReferenceSemantics, ProcurementImpact
from app.models.certification import CertificationRequirement, CertificationScheme, CertificationCurrentness
from app.models.applicability import ApplicabilityRun, ApplicabilityAssessment, ApplicabilityOutcome
from app.services.dependencies.engine import StandardsComplianceEngine
from app.services.dependencies.graph_builder import StandardsGraphBuilder
from app.services.dependencies.compliance_classifier import ComplianceClassifier


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "synthetic_dependency_fixtures.json"


@pytest.fixture
def seeded_dependency_db(db_session: Session):
    """Loads the synthetic dependency test fixtures into test DB session."""
    with open(FIXTURE_PATH, "r") as f:
        data = json.load(f)

    # 1. Standards and Clauses
    for std_data in data["standards"]:
        std = IndianStandard(
            standard_number=std_data["standard_number"],
            title=std_data["title"],
            status=StandardStatus(std_data["status"]),
            is_mandatory_qco=std_data.get("is_mandatory_qco", False),
            qco_reference=std_data.get("qco_reference"),
        )
        db_session.add(std)
        db_session.flush()

        ed = StandardEdition(
            standard_id=std.id,
            edition_number=1,
            year=std_data.get("year", 2020),
            is_current=True,
        )
        db_session.add(ed)
        db_session.flush()

        for c_data in std_data.get("clauses", []):
            cl = Clause(
                edition_id=ed.id,
                clause_number=c_data["clause_number"],
                content=c_data["content"],
            )
            db_session.add(cl)
        db_session.flush()

    # 2. References and Certifications
    for std_data in data["standards"]:
        src_std = db_session.query(IndianStandard).filter_by(standard_number=std_data["standard_number"]).first()
        
        for ref_data in std_data.get("references", []):
            target_std = db_session.query(IndianStandard).filter_by(standard_number=ref_data["target_standard_number"]).first()
            target_id = target_std.id if target_std else None

            source_clause_id = None
            if ref_data.get("referencing_clause") and src_std.editions:
                cl = db_session.query(Clause).filter(
                    Clause.edition_id == src_std.editions[0].id,
                    Clause.clause_number == ref_data["referencing_clause"]
                ).first()
                if cl:
                    source_clause_id = cl.id

            ref = NormativeReference(
                source_standard_id=src_std.id,
                target_standard_id=target_id,
                target_standard_number=ref_data["target_standard_number"],
                relationship_type=ReferenceType(ref_data.get("relationship_type", "NORMATIVE_REFERENCE")),
                reference_semantics=ReferenceSemantics(ref_data.get("reference_semantics", "UNKNOWN")),
                procurement_impact=ProcurementImpact(ref_data.get("procurement_impact", "UNKNOWN")),
                source_clause_id=source_clause_id,
                referencing_clause=ref_data.get("referencing_clause"),
                condition_text=ref_data.get("condition_text"),
                triggering_condition=ref_data.get("triggering_condition"),
                test_name=ref_data.get("test_name"),
                notes=ref_data.get("notes"),
            )
            db_session.add(ref)

        for cert_data in std_data.get("certifications", []):
            cert = CertificationRequirement(
                standard_id=src_std.id,
                scheme=CertificationScheme(cert_data.get("scheme", "ISI_MARK_SCHEME_I")),
                is_mandatory_qco=cert_data.get("is_mandatory_qco", False),
                qco_order_number=cert_data.get("qco_order_number"),
                notifying_ministry=cert_data.get("notifying_ministry"),
                currentness_status=CertificationCurrentness(cert_data.get("currentness_status", "CURRENTNESS_UNCERTAIN")),
                applicable_product_category=cert_data.get("applicable_product_category"),
                verification_source="Gazette Notification",
            )
            db_session.add(cert)

    db_session.commit()
    return db_session


def test_direct_normative_references(seeded_dependency_db: Session):
    """Verifies retrieval and classification of direct (depth 1) references."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=1)

    assert graph.root_standard_number == "IS 101"
    assert len(graph.direct_references) == 5
    assert len(graph.transitive_dependencies) == 0

    rel_types = {e.relationship_type for e in graph.direct_references}
    assert ReferenceType.TEST_METHOD in rel_types
    assert ReferenceType.SAFETY_REQUIREMENT in rel_types
    assert ReferenceType.INSTALLATION_PRACTICE in rel_types
    assert ReferenceType.ALLIED_PRODUCT in rel_types


def test_transitive_multi_hop_traversal(seeded_dependency_db: Session):
    """Verifies multi-hop traversal distinguishing depth 1 vs depth 2+."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=3)

    assert len(graph.direct_references) == 5
    # Transitive dependencies should contain IS 106 (from IS 102) and cycle back-edge to IS 101
    assert len(graph.transitive_dependencies) >= 1
    edge_to_106 = next((e for e in graph.transitive_dependencies if e.target_standard_number == "IS 106"), None)
    assert edge_to_106 is not None
    assert edge_to_106.depth == 2
    assert edge_to_106.source_standard_number == "IS 102"


def test_cycle_detection_and_prevention(seeded_dependency_db: Session):
    """Verifies that cycles like IS 101 -> IS 102 -> IS 106 -> IS 101 are detected without infinite recursion."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=4)

    assert graph.has_cycles is True
    assert len(graph.detected_cycles) > 0

    cycle_cycle = graph.detected_cycles[0]
    assert "IS 101" in cycle_cycle
    assert "IS 102" in cycle_cycle
    assert "IS 106" in cycle_cycle

    # Ensure back-edge has is_cycle=True
    cycle_edge = next((e for e in graph.edges if e.is_cycle), None)
    assert cycle_edge is not None
    assert cycle_edge.source_standard_number == "IS 106"
    assert cycle_edge.target_standard_number == "IS 101"


def test_max_depth_bounding(seeded_dependency_db: Session):
    """Verifies strict depth limiting."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()

    graph_depth_1 = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=1)
    assert max(e.depth for e in graph_depth_1.edges) == 1

    graph_depth_2 = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=2)
    assert max(e.depth for e in graph_depth_2.edges) == 2


def test_clause_level_evidence_traceability(seeded_dependency_db: Session):
    """Verifies that referencing clauses and excerpts are linked to dependency edges."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=1)

    test_edge = next(e for e in graph.edges if e.target_standard_number == "IS 102")
    assert test_edge.referencing_clause == "6.1"
    assert test_edge.clause_content is not None
    assert "Efficiency test shall be carried out" in test_edge.clause_content
    assert test_edge.reference_semantics == ReferenceSemantics.NORMATIVE
    assert test_edge.procurement_impact == ProcurementImpact.REQUIRED_TEST


def test_conditional_dependency_handling(seeded_dependency_db: Session):
    """Verifies preservation of conditional constraints."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=1)

    cond_edge = next(e for e in graph.edges if e.target_standard_number == "IS 105")
    assert cond_edge.reference_semantics == ReferenceSemantics.CONDITIONAL
    assert cond_edge.procurement_impact == ProcurementImpact.CONDITIONAL
    assert cond_edge.condition_text == "If the motor is installed in hazardous petrochemical zones"
    assert cond_edge.triggering_condition == "hazardous_zones"


def test_test_methods_service(seeded_dependency_db: Session):
    """Verifies discovery and extraction of test methods."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    tests = engine.get_test_methods(seeded_dependency_db, std.id)

    assert len(tests) >= 1
    test_102 = next(t for t in tests if t.target_standard_number == "IS 102")
    assert test_102.test_name == "Efficiency Determination Test"
    assert test_102.referencing_clause == "6.1"
    assert test_102.reference_semantics == ReferenceSemantics.NORMATIVE
    assert test_102.procurement_impact == ProcurementImpact.REQUIRED_TEST


def test_safety_and_installation_services(seeded_dependency_db: Session):
    """Verifies safety and installation practices extraction."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()

    safety = engine.get_safety_requirements(seeded_dependency_db, std.id)
    assert any(s.target_standard_number == "IS 103" for s in safety)

    installation = engine.get_installation_practices(seeded_dependency_db, std.id)
    assert any(i.target_standard_number == "IS 104" for i in installation)


def test_certification_and_qco_separation(seeded_dependency_db: Session):
    """Verifies that applicability does not invent mandatory certification, and QCOs are provenance-backed."""
    std_101 = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    std_102 = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 102").first()
    engine = StandardsComplianceEngine()

    # IS 101 has verified mandatory QCO
    qcos_101 = engine.get_qcos(seeded_dependency_db, std_101.id)
    assert len(qcos_101) == 1
    assert qcos_101[0].is_mandatory_qco is True
    assert qcos_101[0].qco_order_number == "S.O. 1234(E)"
    assert qcos_101[0].notifying_ministry == "Ministry of Heavy Industries"
    assert qcos_101[0].currentness_status == CertificationCurrentness.VERIFIED_CURRENT

    # IS 102 has NO mandatory QCO (voluntary/technical only)
    qcos_102 = engine.get_qcos(seeded_dependency_db, std_102.id)
    assert len(qcos_102) == 0


def test_currentness_uncertainty_handling(seeded_dependency_db: Session):
    """Verifies that outdated or unverified certification records are marked CURRENTNESS_UNCERTAIN."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 107_UNCERTAIN").first()
    engine = StandardsComplianceEngine()
    certs = engine.get_certifications(seeded_dependency_db, std.id)

    assert len(certs) == 1
    assert certs[0].currentness_status == CertificationCurrentness.CURRENTNESS_UNCERTAIN

    overview = engine.get_compliance_overview(seeded_dependency_db, std.id)
    assert overview.qco_warning is not None
    assert "uncertain currentness status" in overview.qco_warning


def test_unindexed_target_standard_handling(seeded_dependency_db: Session):
    """Verifies that references to standards not in the database do not crash the graph."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    engine = StandardsComplianceEngine()
    graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=1)

    unindexed_node = next((n for n in graph.nodes if n.standard_number == "IS 999_UNINDEXED"), None)
    assert unindexed_node is not None
    assert unindexed_node.standard_id is None


def test_api_standards_dependency_endpoints(client: TestClient, seeded_dependency_db: Session):
    """Integration test for API routes under /api/v1/standards/{id}."""
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()

    # 1. GET dependencies flat
    res = client.get(f"/api/v1/standards/{std.id}/dependencies")
    assert res.status_code == 200
    assert len(res.json()) >= 5

    # 2. GET graph
    res = client.get(f"/api/v1/standards/{std.id}/dependencies/graph?max_depth=3")
    assert res.status_code == 200
    data = res.json()
    assert data["has_cycles"] is True
    assert len(data["nodes"]) >= 5

    # 3. GET test-methods
    res = client.get(f"/api/v1/standards/{std.id}/test-methods")
    assert res.status_code == 200
    assert any(t["target_standard_number"] == "IS 102" for t in res.json())

    # 4. GET safety-requirements
    res = client.get(f"/api/v1/standards/{std.id}/safety-requirements")
    assert res.status_code == 200
    assert any(s["target_standard_number"] == "IS 103" for s in res.json())

    # 5. GET installation-practices
    res = client.get(f"/api/v1/standards/{std.id}/installation-practices")
    assert res.status_code == 200
    assert any(i["target_standard_number"] == "IS 104" for i in res.json())

    # 6. GET certification
    res = client.get(f"/api/v1/standards/{std.id}/certification")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 7. GET qcos
    res = client.get(f"/api/v1/standards/{std.id}/qcos")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 8. GET compliance-overview
    res = client.get(f"/api/v1/standards/{std.id}/compliance-overview")
    assert res.status_code == 200
    overview = res.json()
    assert overview["has_mandatory_qco"] is True
    assert "IS 101" in overview["summary"]
