"""
Checklist and Clarification Package Generator (Phase 8).
Generates deterministic tender review checklists and structured clarification question packages.
"""

from typing import List, Dict, Any, Optional

from app.schemas.intelligence import (
    ChecklistItemRead,
    TenderReviewChecklistRead,
    ClarificationQuestionRead,
    ClarificationPackageRead,
)
from app.models.requirement import Requirement
from app.models.gap import SpecificationGap, GapType


class ChecklistGenerator:
    """
    Generates deterministic checklists and structured clarification packages from analysis findings.
    """

    @classmethod
    def generate_checklist(
        cls,
        requirements: List[Requirement],
        gaps: List[SpecificationGap],
        standards_findings: Optional[List[Dict[str, Any]]] = None,
    ) -> TenderReviewChecklistRead:
        """
        Builds a deterministic tender review checklist where every item maps to an underlying record.
        """
        items: List[ChecklistItemRead] = []

        # 1. Product Identity Check
        has_product = any(
            req.extracted_text and any(term in req.extracted_text.lower() for term in ["motor", "pump", "cable", "transformer", "steel", "pipe"])
            for req in requirements
        )
        items.append(
            ChecklistItemRead(
                item_id="CHK-01-PRODUCT-IDENTITY",
                label="Product identity and category specified",
                is_verified=has_product,
                category="CORE_TECHNICAL",
                record_reference="Requirement.extracted_text",
            )
        )

        # 2. Rated Power / Capacity Check
        has_power = any(
            any(p.name and "power" in p.name.lower() or "kw" in (p.normalized_value or "").lower() for p in (req.parameters or []))
            for req in requirements
        )
        items.append(
            ChecklistItemRead(
                item_id="CHK-02-RATED-POWER",
                label="Rated power / capacity parameter defined",
                is_verified=has_power,
                category="CORE_TECHNICAL",
                record_reference="TechnicalParameter.name='power'",
            )
        )

        # 3. Voltage Check
        has_voltage = any(
            any(p.name and "voltage" in p.name.lower() or "v" in (p.normalized_value or "").lower() for p in (req.parameters or []))
            for req in requirements
        )
        items.append(
            ChecklistItemRead(
                item_id="CHK-03-RATED-VOLTAGE",
                label="Rated voltage and variation limits specified",
                is_verified=has_voltage,
                category="CORE_TECHNICAL",
                record_reference="TechnicalParameter.name='voltage'",
            )
        )

        # 4. Frequency Check
        has_freq = any(
            any(p.name and "frequency" in p.name.lower() or "hz" in (p.normalized_value or "").lower() for p in (req.parameters or []))
            for req in requirements
        )
        items.append(
            ChecklistItemRead(
                item_id="CHK-04-RATED-FREQUENCY",
                label="Rated frequency specified",
                is_verified=has_freq,
                category="CORE_TECHNICAL",
                record_reference="TechnicalParameter.name='frequency'",
            )
        )

        # 5. Efficiency Class Check
        has_efficiency = any(
            any("ie" in (p.normalized_value or "").lower() or "efficiency" in (p.name or "").lower() for p in (req.parameters or []))
            for req in requirements
        )
        items.append(
            ChecklistItemRead(
                item_id="CHK-05-EFFICIENCY-CLASS",
                label="Energy efficiency class / performance rating defined",
                is_verified=has_efficiency,
                category="PERFORMANCE",
                record_reference="TechnicalParameter.name='efficiency_class'",
            )
        )

        # 6. Ingress Protection (IP) Rating Check
        has_ip = any(
            any("ip" in (p.normalized_value or "").lower() for p in (req.parameters or []))
            for req in requirements
        )
        items.append(
            ChecklistItemRead(
                item_id="CHK-06-INGRESS-PROTECTION",
                label="Degree of ingress protection (IP rating) specified",
                is_verified=has_ip,
                category="ENVIRONMENTAL",
                record_reference="TechnicalParameter.name='ip_rating'",
            )
        )

        # 7. Test Method Standard Reference Check
        has_test_gap = any(g.gap_type == GapType.MISSING_TEST_METHOD for g in gaps)
        items.append(
            ChecklistItemRead(
                item_id="CHK-07-TEST-METHOD",
                label="Factory Acceptance Test (FAT) standards explicitly referenced",
                is_verified=not has_test_gap,
                category="TESTING",
                record_reference="SpecificationGap.gap_type='MISSING_TEST_METHOD'",
            )
        )

        # 8. Acceptance Criteria Check
        has_acc_gap = any(g.gap_type == GapType.MISSING_ACCEPTANCE_CRITERION for g in gaps)
        items.append(
            ChecklistItemRead(
                item_id="CHK-08-ACCEPTANCE-CRITERIA",
                label="Objective quantitative acceptance criteria and tolerances defined",
                is_verified=not has_acc_gap,
                category="TESTING",
                record_reference="SpecificationGap.gap_type='MISSING_ACCEPTANCE_CRITERION'",
            )
        )

        # 9. Applicable Standard Identification Check
        has_std = bool(standards_findings and any(sf.get("applicability_outcome") in ("PRIMARY_RECOMMENDED_STANDARD", "ALTERNATIVE_CANDIDATE", "APPLICABLE") for sf in standards_findings))
        items.append(
            ChecklistItemRead(
                item_id="CHK-09-APPLICABLE-STANDARD",
                label="Applicable Indian Standard definitively resolved",
                is_verified=has_std,
                category="STANDARDS",
                record_reference="ApplicabilityAssessment.outcome",
            )
        )

        # 10. Standard Edition Check
        has_edition = bool(standards_findings and any(sf.get("edition") for sf in standards_findings))
        items.append(
            ChecklistItemRead(
                item_id="CHK-10-STANDARD-EDITION",
                label="Specific standard edition and currentness verified",
                is_verified=has_edition,
                category="STANDARDS",
                record_reference="StandardEdition.edition_number",
            )
        )

        # 11. Statutory QCO Check
        qco_verified = not any(g.gap_type == GapType.MISSING_CERTIFICATION_REQUIREMENT for g in gaps)
        items.append(
            ChecklistItemRead(
                item_id="CHK-11-STATUTORY-QCO",
                label="Mandatory BIS QCO / ISI mark requirements incorporated",
                is_verified=qco_verified,
                category="REGULATORY",
                record_reference="CertificationRequirement.qco_name",
            )
        )

        return TenderReviewChecklistRead(items=items)

    @classmethod
    def generate_clarifications(
        cls,
        gaps: List[SpecificationGap],
    ) -> ClarificationPackageRead:
        """
        Builds structured clarification questions from gaps with reason and evidence.
        """
        questions: List[ClarificationQuestionRead] = []
        q_num = 1

        for gap in gaps:
            orig_text = getattr(gap, "current_value", None) or (gap.requirement.extracted_text if getattr(gap, "requirement", None) else "")
            target_std = (gap.standard.standard_number if getattr(gap, "standard", None) else None) or getattr(gap, "target_standard", None)
            target_clause = getattr(gap, "affected_clause", None) or getattr(gap, "target_clause", None)
            clarification = getattr(gap, "required_clarification", None) or getattr(gap, "clarification_prompt", None)

            if clarification:
                q_text = clarification
            elif gap.gap_type == GapType.AMBIGUOUS_REQUIREMENT:
                q_text = f"Please provide objective numerical parameters to replace subjective wording: '{orig_text}'."
            elif gap.gap_type == GapType.MISSING_PARAMETER:
                q_text = f"Please explicitly specify the required value for '{gap.title}'."
            elif gap.gap_type == GapType.CONFLICTING_REQUIREMENTS:
                q_text = f"Please reconcile contradictory requirements: '{orig_text}'."
            elif gap.gap_type == GapType.MISSING_TEST_METHOD:
                q_text = f"Please specify the referenced test method standard (e.g., {target_std or 'IS 15999'}) for Factory Acceptance Testing."
            elif gap.gap_type == GapType.MISSING_CERTIFICATION_REQUIREMENT:
                q_text = "Please confirm whether the tender mandates BIS Certification (ISI Mark) under the applicable Quality Control Order."
            else:
                q_text = f"Please clarify requirement: {gap.title}."

            questions.append(
                ClarificationQuestionRead(
                    question_number=q_num,
                    question_text=q_text,
                    reason=gap.description or "Clarification required to establish complete, testable procurement specifications.",
                    evidence_clause=target_clause,
                    affected_parameter=gap.title,
                )
            )
            q_num += 1

        return ClarificationPackageRead(questions=questions)
