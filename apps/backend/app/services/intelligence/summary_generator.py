"""
Executive Summary and View Projection Generator (Phase 8).
Assembles deterministic executive summaries and view-specific projections.
"""

from typing import List, Dict, Any, Optional

from app.schemas.intelligence import (
    ExecutiveSummaryRead,
    PackageViewType,
    ProcurementDecisionPackageRead,
)
from app.models.requirement import ProcurementSpecification, Requirement
from app.models.gap import SpecificationGap, GapSeverity, GapType, ReadinessState


class SummaryGenerator:
    """
    Generates deterministic executive summaries and view projections of the decision package.
    """

    @classmethod
    def generate_executive_summary(
        cls,
        specification: ProcurementSpecification,
        requirements: List[Requirement],
        standards_findings: List[Dict[str, Any]],
        gaps: List[SpecificationGap],
        readiness_state: ReadinessState,
        readiness_rationale: str,
    ) -> ExecutiveSummaryRead:
        """
        Assembles a deterministic executive summary without arbitrary percentage scores.
        """
        # Find primary and alternative standards
        primary_std: Optional[str] = None
        alternative_stds: List[str] = []
        currentness_status = "CURRENTNESS_UNCERTAIN"

        for sf in standards_findings:
            outcome = sf.get("applicability_outcome")
            code = sf.get("standard_code", "")
            edition = sf.get("edition")
            full_ref = f"{code}:{edition}" if edition else code

            if outcome == "PRIMARY_RECOMMENDED_STANDARD":
                primary_std = full_ref
                currentness_status = sf.get("currentness", "CURRENTNESS_UNCERTAIN")
            elif outcome in ("ALTERNATIVE_CANDIDATE", "APPLICABLE"):
                alternative_stds.append(full_ref)

        applicable_count = (1 if primary_std else 0) + len(alternative_stds)

        critical_gaps = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        high_gaps = sum(1 for g in gaps if g.severity in (GapSeverity.HIGH, GapSeverity.WARNING))
        ambiguities = sum(1 for g in gaps if g.gap_type in (GapType.AMBIGUOUS_REQUIREMENT, GapType.NON_MEASURABLE_REQUIREMENT))

        # Build readable narrative
        narrative_parts = [
            f"Procurement specification '{specification.title or 'Specification'}' was evaluated across {len(requirements)} extracted requirements.",
        ]
        if primary_std:
            narrative_parts.append(f"Primary applicable standard: {primary_std} (Currentness: {currentness_status}).")
        else:
            narrative_parts.append("No primary applicable Indian Standard could be definitively certified.")

        if alternative_stds:
            narrative_parts.append(f"Alternative candidate standards: {', '.join(alternative_stds)}.")

        if critical_gaps > 0:
            narrative_parts.append(f"CRITICAL: {critical_gaps} blocking gap(s) detected requiring formal tender revision.")
        elif high_gaps > 0:
            narrative_parts.append(f"NOTICE: {high_gaps} high-priority technical gap(s) identified for tender addenda.")
        else:
            narrative_parts.append("Specification demonstrates high technical completeness.")

        narrative_parts.append(f"Procurement Readiness State: {readiness_state.value if hasattr(readiness_state, 'value') else readiness_state}.")

        return ExecutiveSummaryRead(
            procurement_title=specification.title or "Procurement Specification",
            specification_id=specification.id,
            requirements_count=len(requirements),
            standards_count=len(standards_findings),
            applicable_standards_count=applicable_count,
            primary_standard=primary_std,
            alternative_standards=alternative_stds,
            currentness_status=currentness_status,
            critical_gaps_count=critical_gaps,
            high_gaps_count=high_gaps,
            ambiguities_count=ambiguities,
            readiness_state=readiness_state.value if hasattr(readiness_state, "value") else str(readiness_state),
            summary_rationale=" ".join(narrative_parts),
        )

    @classmethod
    def project_view(
        cls,
        package: ProcurementDecisionPackageRead,
        view_type: PackageViewType,
    ) -> Dict[str, Any]:
        """
        Projects the decision package into a specific view format.
        """
        pkg_dict = package.model_dump()

        if view_type == PackageViewType.FULL_ANALYSIS:
            return pkg_dict

        elif view_type == PackageViewType.EXECUTIVE_SUMMARY:
            return {
                "run": pkg_dict["run"],
                "executive_summary": pkg_dict["executive_summary"],
                "primary_standard": pkg_dict["standards_summary"]["primary_standard"],
                "alternative_candidates": pkg_dict["standards_summary"]["alternative_candidates"],
                "readiness": pkg_dict["readiness"],
                "critical_actions": [a for a in pkg_dict["actions"] if a["priority"] == "BLOCKING"],
                "system_limitations": pkg_dict["system_limitations"],
            }

        elif view_type == PackageViewType.TECHNICAL_REVIEW:
            return {
                "run": pkg_dict["run"],
                "executive_summary": pkg_dict["executive_summary"],
                "standards_summary": pkg_dict["standards_summary"],
                "dependencies": pkg_dict["dependencies"],
                "gaps": pkg_dict["gaps"],
                "checklist": pkg_dict["checklist"],
                "system_limitations": pkg_dict["system_limitations"],
            }

        elif view_type == PackageViewType.REGULATORY_REVIEW:
            return {
                "run": pkg_dict["run"],
                "executive_summary": pkg_dict["executive_summary"],
                "edition_currentness": pkg_dict["edition_currentness"],
                "certification_qco": pkg_dict["certification_qco"],
                "regulatory_actions": [
                    a for a in pkg_dict["actions"]
                    if a["action_type"] in ("VERIFY_QCO", "VERIFY_CERTIFICATION", "VERIFY_CURRENTNESS", "VERIFY_STANDARD_EDITION")
                ],
                "system_limitations": pkg_dict["system_limitations"],
            }

        elif view_type == PackageViewType.TRACEABILITY_REPORT:
            return {
                "run": pkg_dict["run"],
                "traceability": pkg_dict["traceability"],
                "evidence_index": pkg_dict["evidence_index"],
                "system_limitations": pkg_dict["system_limitations"],
            }

        elif view_type == PackageViewType.CLARIFICATION_LIST:
            return {
                "run": pkg_dict["run"],
                "clarifications": pkg_dict["clarifications"],
                "actions": pkg_dict["actions"],
                "checklist": pkg_dict["checklist"],
                "system_limitations": pkg_dict["system_limitations"],
            }

        return pkg_dict
