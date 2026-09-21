"""
Procurement Readiness and Specification Gap Assessment Service.
Coordinates ambiguity detection, conflict detection, completeness analysis,
normative dependency gaps, and standard coverage matrix generation.
"""

import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.gap import (
    GapType,
    GapSeverity,
    ReadinessState,
    CompletenessCategory,
    CoverageStatus,
    SpecificationGap,
    ProcurementReadinessAssessment,
)
from app.models.requirement import ProcurementSpecification, Requirement
from app.models.standard import IndianStandard, StandardEdition
from app.schemas.gap import (
    GapItemRead,
    CoverageMatrixItem,
    TraceabilityNode,
    RequirementGapAnalysisRead,
    SpecificationReadinessRead,
)
from app.services.gaps.ambiguity_detector import AmbiguityDetector
from app.services.gaps.conflict_detector import ConflictDetector
from app.services.gaps.completeness_analyzer import CompletenessAnalyzer
from app.services.gaps.dependency_gap_analyzer import DependencyGapAnalyzer
from app.services.gaps.traceability_builder import TraceabilityBuilder


SEVERITY_ORDER = {
    GapSeverity.CRITICAL: 0,
    GapSeverity.HIGH: 1,
    GapSeverity.MEDIUM: 2,
    GapSeverity.LOW: 3,
    GapSeverity.INFO: 4,
    GapSeverity.WARNING: 1,
    GapSeverity.INFORMATIONAL: 4,
}

GAP_TYPE_ORDER = {
    GapType.CONFLICTING_REQUIREMENTS: 0,
    GapType.MISSING_PARAMETER: 1,
    GapType.MISSING_CERTIFICATION_REQUIREMENT: 2,
    GapType.MISSING_SAFETY_REQUIREMENT: 3,
    GapType.MISSING_TEST_METHOD: 4,
    GapType.MISSING_ACCEPTANCE_CRITERION: 5,
    GapType.EDITION_INCONSISTENCY: 6,
    GapType.AMBIGUOUS_REQUIREMENT: 7,
    GapType.NON_MEASURABLE_REQUIREMENT: 8,
    GapType.MISSING_INSTALLATION_REQUIREMENT: 9,
    GapType.MISSING_INTERFACE_REQUIREMENT: 10,
    GapType.AMENDMENT_IMPACT_GAP: 11,
    GapType.UNVERIFIABLE_CLAIM: 12,
    GapType.UNRESOLVED_APPLICABILITY: 13,
}


class ProcurementReadinessService:
    """
    Main orchestrator for procurement specification gap and readiness assessment.
    """

    def __init__(self):
        self.ambiguity_detector = AmbiguityDetector()
        self.conflict_detector = ConflictDetector()
        self.completeness_analyzer = CompletenessAnalyzer()
        self.dependency_gap_analyzer = DependencyGapAnalyzer()
        self.traceability_builder = TraceabilityBuilder()

    def evaluate_requirement(
        self,
        requirement: Requirement,
    ) -> RequirementGapAnalysisRead:
        """
        Evaluates an individual requirement for ambiguities, vague wording, or non-measurable claims.
        """
        gaps = self.ambiguity_detector.detect_ambiguities(
            text=requirement.extracted_text,
            requirement_id=requirement.id,
            specification_id=requirement.specification_id,
            parameters_count=len(requirement.parameters) if requirement.parameters else 0,
        )

        has_critical = any(g.severity == GapSeverity.CRITICAL for g in gaps)
        gap_items = [
            GapItemRead(
                id=g.id,
                specification_id=requirement.specification_id,
                requirement_id=requirement.id,
                gap_type=g.gap_type,
                severity=g.severity,
                status=g.status,
                title=g.title,
                description=g.description,
                why_it_matters=g.why_it_matters or "",
                required_clarification=g.required_clarification or "",
                affected_parameter=g.affected_parameter,
                current_value=g.current_value,
                expected_information=g.expected_information,
                evidence_snippet=g.evidence_snippet,
                source=g.source,
            )
            for g in gaps
        ]

        return RequirementGapAnalysisRead(
            requirement_id=requirement.id,
            requirement_text=requirement.extracted_text,
            gaps=gap_items,
            has_critical_gaps=has_critical,
            gaps_count=len(gap_items),
        )

    def evaluate_specification(
        self,
        specification: ProcurementSpecification,
        applicable_standard: Optional[IndianStandard] = None,
        applicable_edition: Optional[StandardEdition] = None,
        db: Optional[Session] = None,
    ) -> SpecificationReadinessRead:
        """
        Runs comprehensive procurement gap and readiness assessment across the entire specification.
        """
        start_time = time.perf_counter()
        requirements = specification.requirements or []
        all_gaps: List[SpecificationGap] = []

        # 1. PRINCIPLED ABSTENTION: If no requirements exist or standard context is completely unresolvable
        if not requirements:
            duration = (time.perf_counter() - start_time) * 1000.0
            return SpecificationReadinessRead(
                specification_id=specification.id,
                specification_title=specification.title or "Specification",
                readiness_state=ReadinessState.UNRESOLVED_STANDARD_CONTEXT,
                completeness_category=CompletenessCategory.UNRESOLVED,
                total_expected_elements=0,
                elements_present=0,
                elements_missing=0,
                elements_ambiguous=0,
                elements_conflicting=0,
                critical_gaps_count=0,
                high_gaps_count=0,
                medium_gaps_count=0,
                low_gaps_count=0,
                info_gaps_count=0,
                total_gaps_count=0,
                summary_rationale="No requirements extracted from specification. Cannot perform gap analysis.",
                gaps=[],
                coverage_matrix=[],
                traceability=[],
                execution_duration_ms=round(duration, 2),
            )

        # 2. Ambiguity Detection per requirement
        for req in requirements:
            param_cnt = len(req.parameters) if req.parameters else 0
            amb_gaps = self.ambiguity_detector.detect_ambiguities(
                text=req.extracted_text,
                requirement_id=req.id,
                specification_id=specification.id,
                parameters_count=param_cnt,
            )
            all_gaps.extend(amb_gaps)

        # 3. Conflict Detection (parameters and edition inconsistencies)
        param_conflicts = self.conflict_detector.detect_parameter_conflicts(
            specification_id=specification.id,
            requirements=requirements,
        )
        all_gaps.extend(param_conflicts)

        edition_conflicts = self.conflict_detector.detect_edition_inconsistencies(
            specification_id=specification.id,
            requirements=requirements,
        )
        all_gaps.extend(edition_conflicts)

        # 4. Completeness Analysis against baseline
        comp_gaps, comp_metrics = self.completeness_analyzer.analyze_completeness(
            specification_id=specification.id,
            requirements=requirements,
            applicable_standard=applicable_standard,
            applicable_edition=applicable_edition,
        )
        all_gaps.extend(comp_gaps)

        # 5. Dependency Gaps (Test methods, safety, installation, allied products, QCO, amendments)
        dep_gaps = self.dependency_gap_analyzer.analyze_dependency_gaps(
            specification_id=specification.id,
            requirements=requirements,
            applicable_standard=applicable_standard,
            applicable_edition=applicable_edition,
            db=db,
        )
        all_gaps.extend(dep_gaps)

        # 6. Prioritize Gaps deterministically
        def gap_sort_key(g: SpecificationGap):
            s_val = SEVERITY_ORDER.get(g.severity, 99)
            t_val = GAP_TYPE_ORDER.get(g.gap_type, 99)
            return (s_val, t_val)

        all_gaps.sort(key=gap_sort_key)

        # 7. Calculate Counts
        critical_count = sum(1 for g in all_gaps if g.severity == GapSeverity.CRITICAL)
        high_count = sum(1 for g in all_gaps if g.severity in (GapSeverity.HIGH, GapSeverity.WARNING))
        medium_count = sum(1 for g in all_gaps if g.severity == GapSeverity.MEDIUM)
        low_count = sum(1 for g in all_gaps if g.severity == GapSeverity.LOW)
        info_count = sum(1 for g in all_gaps if g.severity in (GapSeverity.INFO, GapSeverity.INFORMATIONAL))

        elements_ambiguous = sum(1 for g in all_gaps if g.gap_type in (GapType.AMBIGUOUS_REQUIREMENT, GapType.NON_MEASURABLE_REQUIREMENT))
        elements_conflicting = sum(1 for g in all_gaps if g.gap_type in (GapType.CONFLICTING_REQUIREMENTS, GapType.EDITION_INCONSISTENCY))

        # 8. Determine Readiness State
        if not applicable_standard and comp_metrics.get("completeness_category") == CompletenessCategory.UNRESOLVED:
            readiness_state = ReadinessState.UNRESOLVED_STANDARD_CONTEXT
            summary_rationale = (
                "Applicable Indian Standard context could not be resolved from specification clauses. "
                "Standards recommendation required before completeness gap assessment."
            )
        elif critical_count > 0:
            readiness_state = ReadinessState.CRITICAL_INFORMATION_MISSING
            reasons = []
            if elements_conflicting > 0:
                reasons.append(f"{elements_conflicting} direct contradiction(s)")
            if any(g.gap_type == GapType.MISSING_CERTIFICATION_REQUIREMENT for g in all_gaps):
                reasons.append("Mandatory statutory QCO omission")
            if any(g.gap_type == GapType.MISSING_PARAMETER and g.severity == GapSeverity.CRITICAL for g in all_gaps):
                reasons.append("Missing primary applicability parameter(s)")
            reasons_str = ", ".join(reasons) if reasons else "Critical specification gaps present"
            summary_rationale = (
                f"Specification contains {critical_count} CRITICAL gap(s) ({reasons_str}). "
                "Tender document cannot be published without formal clarification."
            )
        elif high_count > 0:
            readiness_state = ReadinessState.TECHNICAL_GAPS_PRESENT
            summary_rationale = (
                f"Specification has {high_count} HIGH-severity technical gap(s) "
                "(e.g., missing test method standard or safety provisions). Technical clarification required."
            )
        elif medium_count > 0:
            readiness_state = ReadinessState.NEEDS_CLARIFICATION
            summary_rationale = (
                f"Specification contains {medium_count} MEDIUM-severity gap(s) "
                "(ambiguous phrasing or unquantified requirements). Clarification recommended."
            )
        else:
            readiness_state = ReadinessState.READY_FOR_REVIEW
            summary_rationale = (
                "Specification is technically complete, measurable, and aligned with the applicable Indian Standard. "
                "Ready for pre-tender review."
            )

        # 9. Build Standard Coverage Matrix & Traceability Graph
        coverage_matrix = self.traceability_builder.build_coverage_matrix(
            specification_id=specification.id,
            requirements=requirements,
            gaps=all_gaps,
            applicable_standard=applicable_standard,
            applicable_edition=applicable_edition,
        )
        traceability = self.traceability_builder.build_traceability_graph(
            specification_id=specification.id,
            requirements=requirements,
            gaps=all_gaps,
            applicable_standard=applicable_standard,
            applicable_edition=applicable_edition,
        )

        duration = (time.perf_counter() - start_time) * 1000.0

        # 10. Persist to DB if session provided
        if db:
            # Upsert Readiness Assessment
            existing_assessment = (
                db.query(ProcurementReadinessAssessment)
                .filter(ProcurementReadinessAssessment.specification_id == specification.id)
                .first()
            )
            if not existing_assessment:
                existing_assessment = ProcurementReadinessAssessment(specification_id=specification.id)
                db.add(existing_assessment)

            existing_assessment.readiness_state = readiness_state
            existing_assessment.completeness_category = comp_metrics.get("completeness_category", CompletenessCategory.PARTIALLY_COMPLETE)
            existing_assessment.total_expected_elements = comp_metrics.get("total_expected_elements", len(coverage_matrix))
            existing_assessment.elements_present = comp_metrics.get("elements_present", 0)
            existing_assessment.elements_missing = comp_metrics.get("elements_missing", 0)
            existing_assessment.elements_ambiguous = elements_ambiguous
            existing_assessment.elements_conflicting = elements_conflicting
            existing_assessment.critical_gaps_count = critical_count
            existing_assessment.high_gaps_count = high_count
            existing_assessment.medium_gaps_count = medium_count
            existing_assessment.low_gaps_count = low_count
            existing_assessment.summary_rationale = summary_rationale
            existing_assessment.execution_duration_ms = round(duration, 2)

            # Persist gaps (delete prior detected gaps for this spec to prevent duplicates)
            db.query(SpecificationGap).filter(SpecificationGap.specification_id == specification.id).delete()
            for g in all_gaps:
                db.add(g)
            db.commit()

        # 11. Format Output Pydantic Schema
        gap_reads = [
            GapItemRead(
                id=g.id,
                specification_id=specification.id,
                requirement_id=g.requirement_id,
                gap_type=g.gap_type,
                severity=g.severity,
                status=g.status,
                title=g.title,
                description=g.description,
                why_it_matters=g.why_it_matters or "",
                required_clarification=g.required_clarification or "",
                affected_parameter=g.affected_parameter,
                current_value=g.current_value,
                expected_information=g.expected_information,
                affected_standard_id=g.affected_standard_id,
                affected_standard_number=applicable_standard.standard_number if applicable_standard else None,
                affected_edition_id=g.affected_edition_id,
                affected_clause=g.affected_clause,
                evidence_snippet=g.evidence_snippet,
                source=g.source,
            )
            for g in all_gaps
        ]

        return SpecificationReadinessRead(
            specification_id=specification.id,
            specification_title=specification.title or "Specification",
            readiness_state=readiness_state,
            completeness_category=comp_metrics.get("completeness_category", CompletenessCategory.PARTIALLY_COMPLETE),
            total_expected_elements=comp_metrics.get("total_expected_elements", len(coverage_matrix)),
            elements_present=comp_metrics.get("elements_present", 0),
            elements_missing=comp_metrics.get("elements_missing", 0),
            elements_ambiguous=elements_ambiguous,
            elements_conflicting=elements_conflicting,
            critical_gaps_count=critical_count,
            high_gaps_count=high_count,
            medium_gaps_count=medium_count,
            low_gaps_count=low_count,
            info_gaps_count=info_count,
            total_gaps_count=len(all_gaps),
            summary_rationale=summary_rationale,
            gaps=gap_reads,
            coverage_matrix=coverage_matrix,
            traceability=traceability,
            execution_duration_ms=round(duration, 2),
        )
