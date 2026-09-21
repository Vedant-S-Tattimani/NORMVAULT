"""
Procurement Review Action Generator (Phase 8).
Derives deterministic, evidence-backed review and clarification actions with explicit priority rules.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.intelligence import (
    ProcurementReviewAction,
    ActionType,
    ActionPriority,
    ProcurementIntelligenceRun,
)
from app.models.gap import SpecificationGap, GapType, GapSeverity


# Deterministic priority ordering: BLOCKING > HIGH > MEDIUM > LOW
PRIORITY_ORDER = {
    ActionPriority.BLOCKING: 0,
    ActionPriority.HIGH: 1,
    ActionPriority.MEDIUM: 2,
    ActionPriority.LOW: 3,
}

# Precedence mapping from Step 12
GAP_TO_ACTION_MAPPING = {
    # 1. Contradictory requirements (BLOCKING)
    GapType.CONFLICTING_REQUIREMENTS: (
        ActionType.RESOLVE_CONFLICT,
        ActionPriority.BLOCKING,
        "Conflicting specifications must be reconciled before tender publication.",
    ),
    # 2. Missing information affecting applicability (BLOCKING)
    GapType.UNRESOLVED_APPLICABILITY: (
        ActionType.REVIEW_UNCERTAIN_EVIDENCE,
        ActionPriority.BLOCKING,
        "Applicable standard cannot be determined due to missing core parameters.",
    ),
    # 3. Missing information affecting objective acceptance (HIGH)
    GapType.MISSING_ACCEPTANCE_CRITERION: (
        ActionType.SPECIFY_PARAMETER,
        ActionPriority.HIGH,
        "Acceptance criteria must be defined to ensure objective inspection and testing.",
    ),
    # 4. Unverified statutory/certification context (HIGH)
    GapType.MISSING_CERTIFICATION_REQUIREMENT: (
        ActionType.VERIFY_QCO,
        ActionPriority.HIGH,
        "Mandatory BIS certification or QCO compliance must be explicitly specified.",
    ),
    # 5. Superseded/withdrawn edition issues (HIGH)
    GapType.EDITION_INCONSISTENCY: (
        ActionType.VERIFY_STANDARD_EDITION,
        ActionPriority.HIGH,
        "Inconsistent or superseded standard editions cited across clauses must be harmonized.",
    ),
    # 6. Missing safety requirements (HIGH)
    GapType.MISSING_SAFETY_REQUIREMENT: (
        ActionType.VERIFY_SAFETY_REQUIREMENT,
        ActionPriority.HIGH,
        "Mandatory electrical/operational safety requirements must be incorporated.",
    ),
    # 7. Missing test methods (MEDIUM)
    GapType.MISSING_TEST_METHOD: (
        ActionType.VERIFY_TEST_METHOD,
        ActionPriority.MEDIUM,
        "Test method standard reference required for Factory Acceptance Testing (FAT).",
    ),
    # 8. Ambiguous terminology (MEDIUM)
    GapType.AMBIGUOUS_REQUIREMENT: (
        ActionType.CLARIFY_REQUIREMENT,
        ActionPriority.MEDIUM,
        "Subjective or non-measurable language should be replaced with quantifiable thresholds.",
    ),
    GapType.NON_MEASURABLE_REQUIREMENT: (
        ActionType.CLARIFY_REQUIREMENT,
        ActionPriority.MEDIUM,
        "Requirement lacks verifiable test parameters and tolerance bounds.",
    ),
    GapType.UNVERIFIABLE_CLAIM: (
        ActionType.CLARIFY_REQUIREMENT,
        ActionPriority.MEDIUM,
        "Unverifiable marketing or quality claim cannot be validated during inspection.",
    ),
    # 9. Lower-impact completeness issues (LOW)
    GapType.MISSING_INSTALLATION_REQUIREMENT: (
        ActionType.VERIFY_INSTALLATION_REQUIREMENT,
        ActionPriority.LOW,
        "Installation code of practice should be referenced for site commissioning.",
    ),
    GapType.MISSING_INTERFACE_REQUIREMENT: (
        ActionType.SPECIFY_PARAMETER,
        ActionPriority.LOW,
        "Allied product or mechanical interface dimensions should be specified.",
    ),
    GapType.AMENDMENT_IMPACT_GAP: (
        ActionType.REVIEW_AMENDMENT,
        ActionPriority.LOW,
        "Published amendment may affect technical or testing parameters.",
    ),
    GapType.MISSING_PARAMETER: (
        ActionType.SPECIFY_PARAMETER,
        ActionPriority.MEDIUM,
        "Missing technical parameter should be stated for specification completeness.",
    ),
}


class ActionGenerator:
    """
    Generates prioritized review actions from specification gaps and compliance findings.
    """

    @classmethod
    def generate_actions_for_run(
        cls,
        db: Session,
        run: ProcurementIntelligenceRun,
        gaps: List[SpecificationGap],
        standards_findings: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ProcurementReviewAction]:
        """
        Generates and persists ProcurementReviewAction items for the intelligence run.
        """
        actions: List[ProcurementReviewAction] = []

        # 1. Generate actions from gaps
        for gap in gaps:
            mapping = GAP_TO_ACTION_MAPPING.get(gap.gap_type)
            if mapping:
                action_type, priority, default_reason = mapping
            else:
                action_type = ActionType.CLARIFY_REQUIREMENT
                priority = ActionPriority.LOW
                default_reason = "Review required for specification completeness."

            # Upgrade priority to BLOCKING if gap severity is CRITICAL
            if gap.severity == GapSeverity.CRITICAL and priority != ActionPriority.BLOCKING:
                priority = ActionPriority.BLOCKING

            orig_text = getattr(gap, "current_value", None) or (gap.requirement.extracted_text if getattr(gap, "requirement", None) else "")
            target_std = (gap.standard.standard_number if getattr(gap, "standard", None) else None) or getattr(gap, "target_standard", None)
            target_clause = getattr(gap, "affected_clause", None) or getattr(gap, "target_clause", None)
            clarification = getattr(gap, "required_clarification", None) or getattr(gap, "clarification_prompt", None)

            action = ProcurementReviewAction(
                run_id=run.id,
                action_type=action_type,
                priority=priority,
                description=gap.title or gap.description or f"Review {gap.gap_type.value}",
                reason=gap.description or default_reason,
                suggested_action=clarification or "Review with technical committee and update tender text.",
                source_gap_id=gap.id,
                affected_requirement_id=gap.requirement_id,
                affected_standard_id=gap.affected_standard_id,
                evidence={
                    "gap_type": gap.gap_type.value if hasattr(gap.gap_type, "value") else str(gap.gap_type),
                    "severity": gap.severity.value if hasattr(gap.severity, "value") else str(gap.severity),
                    "original_text": orig_text,
                    "target_standard": target_std,
                    "target_clause": target_clause,
                },
            )
            actions.append(action)

        # 2. Generate actions from standards currentness or QCO findings
        if standards_findings:
            for sf in standards_findings:
                if sf.get("currentness") == "CURRENTNESS_UNCERTAIN":
                    actions.append(
                        ProcurementReviewAction(
                            run_id=run.id,
                            action_type=ActionType.VERIFY_CURRENTNESS,
                            priority=ActionPriority.HIGH,
                            description=f"Verify active status of {sf.get('standard_code')}",
                            reason="Indexed BIS currentness status could not be verified with high certainty.",
                            suggested_action="Consult official BIS portal (manakonline.in) to confirm standard edition is current.",
                            affected_standard_id=sf.get("standard_id"),
                            evidence={"standard_code": sf.get("standard_code"), "edition": sf.get("edition")},
                        )
                    )
                if sf.get("qco_status") == "CURRENTNESS_UNCERTAIN":
                    actions.append(
                        ProcurementReviewAction(
                            run_id=run.id,
                            action_type=ActionType.VERIFY_QCO,
                            priority=ActionPriority.HIGH,
                            description=f"Verify statutory QCO enforcement for {sf.get('standard_code')}",
                            reason="Quality Control Order Gazette notification could not be verified against latest gazette records.",
                            suggested_action="Verify gazette notification status with the notifying ministry prior to tender issuance.",
                            affected_standard_id=sf.get("standard_id"),
                            evidence={"standard_code": sf.get("standard_code"), "qco": sf.get("qco_name")},
                        )
                    )

        # 3. Sort deterministically by priority precedence
        actions.sort(key=lambda a: PRIORITY_ORDER.get(a.priority, 99))

        # 4. Persist
        for a in actions:
            db.add(a)
        db.commit()

        for a in actions:
            db.refresh(a)

        return actions
