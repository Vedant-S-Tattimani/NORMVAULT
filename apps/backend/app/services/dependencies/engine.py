"""
Standards Dependency and Compliance Intelligence Engine.
Coordinates reference graph resolution, specialized intelligence streams (tests, safety, installation, allied),
and QCO statutory certification intelligence.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard
from app.models.reference import NormativeReference, ReferenceType, ReferenceSemantics, ProcurementImpact
from app.models.certification import CertificationRequirement, CertificationCurrentness
from app.models.applicability import ApplicabilityRun, ApplicabilityAssessment, ApplicabilityOutcome
from app.models.clause import Clause
from app.schemas.dependency import (
    DependencyEdge,
    StandardsDependencyGraph,
    TestMethodDependencyRead,
    SafetyRequirementDependencyRead,
    InstallationPracticeDependencyRead,
    AlliedProductDependencyRead,
    CertificationComplianceRead,
    ProcurementComplianceOverview,
)
from app.services.dependencies.graph_builder import StandardsGraphBuilder
from app.services.dependencies.compliance_classifier import ComplianceClassifier


class StandardsComplianceEngine:
    """
    Central service for analyzing standards dependencies, normative obligations,
    and statutory certification schemes.
    """

    def __init__(self, default_max_depth: int = 3):
        self.default_max_depth = default_max_depth

    def get_dependency_graph(
        self, db: Session, standard_id: int, max_depth: Optional[int] = None
    ) -> StandardsDependencyGraph:
        """Constructs a complete directed dependency graph for a standard."""
        depth = max_depth if max_depth is not None else self.default_max_depth
        builder = StandardsGraphBuilder(max_depth=depth)
        return builder.build_graph(db, standard_id)

    def get_dependencies_flat(
        self, db: Session, standard_id: int, max_depth: Optional[int] = None
    ) -> List[DependencyEdge]:
        """Returns all direct and transitive dependency edges as a flat list."""
        graph = self.get_dependency_graph(db, standard_id, max_depth)
        return graph.edges

    def get_test_methods(self, db: Session, standard_id: int) -> List[TestMethodDependencyRead]:
        """Discovers test method standards referenced by this standard."""
        graph = self.get_dependency_graph(db, standard_id, max_depth=2)
        results: List[TestMethodDependencyRead] = []

        for edge in graph.edges:
            if edge.relationship_type == ReferenceType.TEST_METHOD:
                # Find target title
                node = next((n for n in graph.nodes if n.standard_number == edge.target_standard_number), None)
                results.append(
                    TestMethodDependencyRead(
                        id=edge.id,
                        source_standard_number=edge.source_standard_number,
                        target_standard_number=edge.target_standard_number,
                        target_standard_title=node.title if node else None,
                        test_name=edge.test_name or "Standard Test Method",
                        referencing_clause=edge.referencing_clause,
                        clause_content=edge.clause_content,
                        reference_semantics=edge.reference_semantics,
                        procurement_impact=edge.procurement_impact,
                        condition_text=edge.condition_text,
                        depth=edge.depth,
                        provenance_id=edge.provenance_id,
                    )
                )
        return results

    def get_safety_requirements(self, db: Session, standard_id: int) -> List[SafetyRequirementDependencyRead]:
        """Discovers safety codes of practice referenced by this standard."""
        graph = self.get_dependency_graph(db, standard_id, max_depth=2)
        results: List[SafetyRequirementDependencyRead] = []

        for edge in graph.edges:
            if edge.relationship_type == ReferenceType.SAFETY_REQUIREMENT:
                node = next((n for n in graph.nodes if n.standard_number == edge.target_standard_number), None)
                results.append(
                    SafetyRequirementDependencyRead(
                        id=edge.id,
                        source_standard_number=edge.source_standard_number,
                        target_standard_number=edge.target_standard_number,
                        target_standard_title=node.title if node else None,
                        referencing_clause=edge.referencing_clause,
                        clause_content=edge.clause_content,
                        reference_semantics=edge.reference_semantics,
                        procurement_impact=edge.procurement_impact,
                        condition_text=edge.condition_text,
                        depth=edge.depth,
                        provenance_id=edge.provenance_id,
                    )
                )
        return results

    def get_installation_practices(self, db: Session, standard_id: int) -> List[InstallationPracticeDependencyRead]:
        """Discovers installation and laying codes of practice referenced by this standard."""
        graph = self.get_dependency_graph(db, standard_id, max_depth=2)
        results: List[InstallationPracticeDependencyRead] = []

        for edge in graph.edges:
            if edge.relationship_type == ReferenceType.INSTALLATION_PRACTICE:
                node = next((n for n in graph.nodes if n.standard_number == edge.target_standard_number), None)
                results.append(
                    InstallationPracticeDependencyRead(
                        id=edge.id,
                        source_standard_number=edge.source_standard_number,
                        target_standard_number=edge.target_standard_number,
                        target_standard_title=node.title if node else None,
                        referencing_clause=edge.referencing_clause,
                        clause_content=edge.clause_content,
                        reference_semantics=edge.reference_semantics,
                        procurement_impact=edge.procurement_impact,
                        condition_text=edge.condition_text,
                        depth=edge.depth,
                        provenance_id=edge.provenance_id,
                    )
                )
        return results

    def get_allied_products(self, db: Session, standard_id: int) -> List[AlliedProductDependencyRead]:
        """Discovers allied component and complementary material standards."""
        graph = self.get_dependency_graph(db, standard_id, max_depth=2)
        results: List[AlliedProductDependencyRead] = []

        for edge in graph.edges:
            if edge.relationship_type == ReferenceType.ALLIED_PRODUCT:
                node = next((n for n in graph.nodes if n.standard_number == edge.target_standard_number), None)
                results.append(
                    AlliedProductDependencyRead(
                        id=edge.id,
                        source_standard_number=edge.source_standard_number,
                        target_standard_number=edge.target_standard_number,
                        target_standard_title=node.title if node else None,
                        referencing_clause=edge.referencing_clause,
                        clause_content=edge.clause_content,
                        reference_semantics=edge.reference_semantics,
                        procurement_impact=edge.procurement_impact,
                        condition_text=edge.condition_text,
                        depth=edge.depth,
                        provenance_id=edge.provenance_id,
                    )
                )
        return results

    def get_certifications(self, db: Session, standard_id: int) -> List[CertificationComplianceRead]:
        """Retrieves verified BIS certification schemes and QCO records."""
        std = db.query(IndianStandard).filter(IndianStandard.id == standard_id).first()
        if not std:
            raise ValueError(f"Standard {standard_id} not found.")

        cert_records = db.query(CertificationRequirement).filter(CertificationRequirement.standard_id == standard_id).all()
        results: List[CertificationComplianceRead] = []

        for c in cert_records:
            results.append(
                CertificationComplianceRead(
                    id=c.id,
                    standard_id=c.standard_id,
                    standard_number=std.standard_number,
                    scheme=c.scheme,
                    is_mandatory_qco=c.is_mandatory_qco,
                    qco_order_number=c.qco_order_number,
                    notifying_ministry=c.notifying_ministry,
                    notification_date=c.notification_date,
                    enforcement_date=c.enforcement_date,
                    currentness_status=c.currentness_status,
                    applicable_product_category=c.applicable_product_category,
                    verification_source=c.verification_source,
                    scope_condition=c.scope_condition,
                    provenance_id=c.provenance_id,
                )
            )

        # Fallback: if standard itself has is_mandatory_qco=True and qco_reference, but no explicit CertificationRequirement record
        if not results and std.is_mandatory_qco:
            results.append(
                CertificationComplianceRead(
                    id=None,
                    standard_id=std.id,
                    standard_number=std.standard_number,
                    is_mandatory_qco=True,
                    qco_order_number=std.qco_reference,
                    currentness_status=CertificationCurrentness.VERIFIED_CURRENT,
                    verification_source="Standard Registry Flag",
                    provenance_id=std.provenance_id,
                )
            )

        return results

    def get_qcos(self, db: Session, standard_id: int) -> List[CertificationComplianceRead]:
        """Filters certification requirements down to statutory Quality Control Orders."""
        certs = self.get_certifications(db, standard_id)
        return [c for c in certs if c.is_mandatory_qco or c.qco_order_number]

    def get_compliance_overview(
        self, db: Session, standard_id: int, max_depth: Optional[int] = None
    ) -> ProcurementComplianceOverview:
        """Constructs a consolidated compliance, reference, and QCO overview."""
        std = db.query(IndianStandard).filter(IndianStandard.id == standard_id).first()
        if not std:
            raise ValueError(f"Standard {standard_id} not found.")

        graph = self.get_dependency_graph(db, standard_id, max_depth)
        test_methods = self.get_test_methods(db, standard_id)
        safety_reqs = self.get_safety_requirements(db, standard_id)
        install_practices = self.get_installation_practices(db, standard_id)
        allied_prods = self.get_allied_products(db, standard_id)
        certs = self.get_certifications(db, standard_id)

        has_qco = any(c.is_mandatory_qco for c in certs) or std.is_mandatory_qco
        qco_warning = None
        uncertain_certs = [c for c in certs if c.currentness_status == CertificationCurrentness.CURRENTNESS_UNCERTAIN]
        if uncertain_certs:
            qco_warning = "Some certification records have uncertain currentness status. Verify with latest BIS gazette notification."

        summary = (
            f"{std.standard_number} references {len(graph.direct_references)} direct standards and "
            f"{len(graph.transitive_dependencies)} transitive dependencies across {graph.total_nodes} total standards. "
            f"Mandatory QCO status: {'YES (Statutory Order Enforced)' if has_qco else 'NO (Voluntary/Non-QCO)'}."
        )

        return ProcurementComplianceOverview(
            standard_id=std.id,
            standard_number=std.standard_number,
            standard_title=std.title,
            graph=graph,
            test_methods=test_methods,
            safety_requirements=safety_reqs,
            installation_practices=install_practices,
            allied_products=allied_prods,
            certifications=certs,
            has_mandatory_qco=has_qco,
            qco_warning=qco_warning,
            summary=summary,
        )

    def get_applicability_run_compliance(self, db: Session, run_id: int) -> Dict[str, Any]:
        """Gathers compliance and dependency overviews across all applicable standards in a run."""
        run = db.query(ApplicabilityRun).filter(ApplicabilityRun.id == run_id).first()
        if not run:
            raise ValueError(f"ApplicabilityRun {run_id} not found.")

        assessments = (
            db.query(ApplicabilityAssessment)
            .filter(
                ApplicabilityAssessment.run_id == run_id,
                ApplicabilityAssessment.outcome.in_([
                    ApplicabilityOutcome.APPLICABLE,
                    ApplicabilityOutcome.POSSIBLY_APPLICABLE,
                ]),
            )
            .all()
        )

        standard_ids = list({a.standard_id for a in assessments})
        overviews: List[ProcurementComplianceOverview] = []

        for sid in standard_ids:
            try:
                overview = self.get_compliance_overview(db, sid)
                overviews.append(overview)
            except Exception:
                continue

        return {
            "run_id": run.id,
            "total_applicable_standards": len(standard_ids),
            "overviews": [o.model_dump() for o in overviews],
        }
