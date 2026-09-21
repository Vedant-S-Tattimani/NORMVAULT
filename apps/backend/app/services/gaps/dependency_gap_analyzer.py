"""
Dependency and Compliance Gap Analyzer.
Interrogates Phase 5 normative reference graphs and Phase 6 currentness evaluations to detect
missing test methods (FAT), safety requirements, installation practices, allied product interfaces,
and statutory Quality Control Order (QCO) certification gaps.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.gap import GapType, GapSeverity, SpecificationGap
from app.models.requirement import Requirement
from app.models.standard import IndianStandard, StandardEdition, StandardStatus, EditionStatus
from app.models.reference import ReferenceType, ProcurementImpact
from app.models.certification import CertificationRequirement, CertificationCurrentness


class DependencyGapAnalyzer:
    """
    Evaluates normative dependencies (test methods, safety, installation, allied products)
    and statutory certification mandates to discover specification gaps.
    """

    def analyze_dependency_gaps(
        self,
        specification_id: int,
        requirements: List[Requirement],
        applicable_standard: Optional[IndianStandard] = None,
        applicable_edition: Optional[StandardEdition] = None,
        db: Optional[Session] = None,
    ) -> List[SpecificationGap]:
        """
        Discovers dependency and compliance gaps for the specification.
        """
        gaps: List[SpecificationGap] = []
        if not applicable_standard:
            return gaps

        combined_text = " ".join(r.extracted_text.lower() for r in requirements)
        std_num = applicable_standard.standard_number.upper()

        # 1. TEST METHOD DEPENDENCY GAP
        # Check if test method standard is mentioned (e.g., IS 15999 or IS/IEC 60034-2-1 for motors)
        has_test_method_citation = (
            "15999" in combined_text
            or "test method" in combined_text
            or "60034-2" in combined_text
            or "routine test" in combined_text
            or "type test" in combined_text
            or "factory acceptance" in combined_text
            or "fat" in combined_text
        )

        # Check if efficiency is specified without test method standard
        has_efficiency_requirement = (
            "ie2" in combined_text
            or "ie3" in combined_text
            or "ie4" in combined_text
            or "efficiency" in combined_text
        )

        if "12615" in std_num or "325" in std_num:
            if not ("15999" in combined_text or "60034-2" in combined_text):
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        gap_type=GapType.MISSING_TEST_METHOD,
                        severity=GapSeverity.HIGH,
                        status="DETECTED",
                        title="Missing Test Method Standard: IS 15999 (Summation of Losses)",
                        description=(
                            "The procurement specification defines performance/efficiency requirements but omits the "
                            "mandatory test method standard IS 15999 (Methods for Determining Losses and Efficiency from Tests)."
                        ),
                        why_it_matters=(
                            "Without specifying IS 15999 as the measurement methodology, efficiency values and loss guarantees "
                            "cannot be objectively verified during Factory Acceptance Tests (FAT) or third-party laboratory audits."
                        ),
                        required_clarification=(
                            "Incorporate IS 15999 (Part 1/Part 2) as the mandatory testing and loss measurement standard for FAT inspection."
                        ),
                        affected_parameter="Test Methodology Standard",
                        expected_information="IS 15999-1 / IS/IEC 60034-2-1",
                        affected_standard_id=applicable_standard.id,
                        affected_edition_id=applicable_edition.id if applicable_edition else None,
                        affected_clause="IS 12615 Cl. 8 / IS 15999",
                        source="DEPENDENCY_GAP_ANALYZER",
                    )
                )

            # Check for missing acceptance criteria / tolerances
            has_tolerance_clause = (
                "tolerance" in combined_text
                or "permissible variation" in combined_text
                or "acceptance criteria" in combined_text
                or "margin" in combined_text
            )
            if has_efficiency_requirement and not has_tolerance_clause:
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        gap_type=GapType.MISSING_ACCEPTANCE_CRITERION,
                        severity=GapSeverity.MEDIUM,
                        status="DETECTED",
                        title="Missing Acceptance Criteria & Test Tolerances for Efficiency",
                        description=(
                            "The specification mandates efficiency values without referencing standard tolerance allowances "
                            "or acceptance criteria per IS/IEC 60034-1 / IS 12615."
                        ),
                        why_it_matters=(
                            "Indian and international standards provide explicit numerical tolerance bands for test results "
                            "(e.g., -15% of [1 - η] for efficiency). Omitting acceptance criteria creates inspection disputes."
                        ),
                        required_clarification=(
                            "Define clear factory acceptance criteria and specify applicable tolerance allowances per IS 12615 / IS/IEC 60034-1."
                        ),
                        affected_parameter="Acceptance Criteria & Tolerances",
                        expected_information="Tolerance allowance per IS/IEC 60034-1",
                        affected_standard_id=applicable_standard.id,
                        affected_clause="IS 12615 Table of Tolerances",
                        source="DEPENDENCY_GAP_ANALYZER",
                    )
                )

        # 2. SAFETY REQUIREMENT GAP
        has_earthing = (
            "earthing" in combined_text
            or "grounding" in combined_text
            or "earth terminal" in combined_text
            or "protective conductor" in combined_text
            or "3043" in combined_text
        )
        if not has_earthing:
            gaps.append(
                SpecificationGap(
                    specification_id=specification_id,
                    gap_type=GapType.MISSING_SAFETY_REQUIREMENT,
                    severity=GapSeverity.HIGH,
                    status="DETECTED",
                    title="Missing Safety Requirement: Protective Earthing & Grounding",
                    description=(
                        "The specification omits protective earthing requirements for equipment frame and terminal box."
                    ),
                    why_it_matters=(
                        "Electrical equipment requires dual distinct earthing terminals to ensure fault clearance and "
                        "prevent lethal touch voltages under fault conditions per IS 3043 (Code of Practice for Earthing)."
                    ),
                    required_clarification=(
                        "Specify dual earthing terminals on the main frame and terminal box in compliance with IS 3043 / IS/IEC 60034-1."
                    ),
                    affected_parameter="Earthing & Safety Grounding",
                    expected_information="Dual distinct earthing terminals conforming to IS 3043",
                    affected_standard_id=applicable_standard.id,
                    affected_clause="IS 3043 / IS/IEC 60034-1 Cl. 10",
                    source="DEPENDENCY_GAP_ANALYZER",
                )
            )

        # 3. INSTALLATION PRACTICE GAP
        has_installation_code = (
            "installation" in combined_text
            or "is 900" in combined_text
            or "is:900" in combined_text
            or "laying" in combined_text
            or "erection" in combined_text
            or "commissioning" in combined_text
        )
        if "12615" in std_num and not ("900" in combined_text or "code of practice" in combined_text):
            gaps.append(
                SpecificationGap(
                    specification_id=specification_id,
                    gap_type=GapType.MISSING_INSTALLATION_REQUIREMENT,
                    severity=GapSeverity.MEDIUM,
                    status="DETECTED",
                    title="Missing Installation Practice Standard: IS 900",
                    description=(
                        "The specification does not reference standard installation and maintenance practices (IS 900)."
                    ),
                    why_it_matters=(
                        "Proper installation, foundation vibration limits, and pre-commissioning alignment under IS 900 "
                        "are essential to prevent premature mechanical failure and maintain valid manufacturer warranties."
                    ),
                    required_clarification=(
                        "Include reference to IS 900 (Code of Practice for Installation and Maintenance of Induction Motors)."
                    ),
                    affected_parameter="Installation & Commissioning Standard",
                    expected_information="IS 900 Code of Practice",
                    affected_standard_id=applicable_standard.id,
                    affected_clause="IS 900",
                    source="DEPENDENCY_GAP_ANALYZER",
                )
            )

        # 4. ALLIED PRODUCT / INTERFACE GAP
        has_dimension_standard = (
            "1231" in combined_text
            or "2223" in combined_text
            or "frame size" in combined_text
            or "shaft dimension" in combined_text
            or "mounting dimension" in combined_text
        )
        if "12615" in std_num and not has_dimension_standard:
            gaps.append(
                SpecificationGap(
                    specification_id=specification_id,
                    gap_type=GapType.MISSING_INTERFACE_REQUIREMENT,
                    severity=GapSeverity.LOW,
                    status="DETECTED",
                    title="Missing Dimensional Interface Standard: IS 1231 / IS 2223",
                    description=(
                        "The specification omits standard dimensional interface references for motor frame sizes, shaft extensions, and keyways."
                    ),
                    why_it_matters=(
                        "Standard mechanical dimensions per IS 1231 (foot-mounted) or IS 2223 (flange-mounted) are necessary "
                        "to guarantee mechanical interchangeability with driven pumps, compressors, or gearboxes."
                    ),
                    required_clarification=(
                        "Specify frame size and shaft extension dimensional tolerances per IS 1231 (foot mounted) or IS 2223 (flange mounted)."
                    ),
                    affected_parameter="Mechanical Interface Dimensions",
                    expected_information="IS 1231 / IS 2223 Dimensional Standards",
                    affected_standard_id=applicable_standard.id,
                    affected_clause="IS 1231 / IS 2223",
                    source="DEPENDENCY_GAP_ANALYZER",
                )
            )

        # 5. STATUTORY CERTIFICATION & QCO REQUIREMENTS
        is_qco_mandatory = applicable_standard.is_mandatory_qco
        if not is_qco_mandatory and db:
            # Check CertificationRequirement table
            cert_req = (
                db.query(CertificationRequirement)
                .filter(CertificationRequirement.standard_id == applicable_standard.id)
                .first()
            )
            if cert_req and cert_req.is_mandatory_qco:
                is_qco_mandatory = True

        # Induction motors under IS 12615 are inherently under mandatory QCO
        if "12615" in std_num:
            is_qco_mandatory = True

        has_isi_certification = (
            "isi mark" in combined_text
            or "bis mark" in combined_text
            or "standard mark" in combined_text
            or "bis license" in combined_text
            or "bis certification" in combined_text
            or "cml" in combined_text
            or "scheme i" in combined_text
        )

        if is_qco_mandatory and not has_isi_certification:
            gaps.append(
                SpecificationGap(
                    specification_id=specification_id,
                    gap_type=GapType.MISSING_CERTIFICATION_REQUIREMENT,
                    severity=GapSeverity.CRITICAL,
                    status="DETECTED",
                    title="Mandatory Quality Control Order (QCO) Omitted: BIS Certification Required",
                    description=(
                        f"{applicable_standard.standard_number} is governed by a mandatory Quality Control Order (QCO) "
                        "notified under the Bureau of Indian Standards Act, 2016. The tender document omits mandatory BIS certification requirements."
                    ),
                    why_it_matters=(
                        "By statutory gazette order, no person shall manufacture, import, store, sell, or distribute goods "
                        "governed by this QCO without bearing the BIS Standard Mark (ISI mark) under a valid BIS license. "
                        "Procuring uncertified goods violates central procurement regulations and risks statutory seizure."
                    ),
                    required_clarification=(
                        "Incorporate mandatory statutory clause: 'Suppliers must hold a valid BIS License under Scheme-I "
                        "and equipment must bear the Standard Mark (ISI mark) in compliance with the applicable Quality Control Order.'"
                    ),
                    affected_parameter="Statutory BIS Certification (ISI Mark)",
                    expected_information="Valid BIS License with ISI Mark under Scheme-I",
                    affected_standard_id=applicable_standard.id,
                    affected_clause="BIS Act 2016 / Applicable Quality Control Order",
                    source="DEPENDENCY_GAP_ANALYZER",
                )
            )

        # 6. EDITION CURRENTNESS & AMENDMENT IMPACT
        if applicable_edition:
            if applicable_edition.status == EditionStatus.SUPERSEDED:
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        gap_type=GapType.EDITION_INCONSISTENCY,
                        severity=GapSeverity.HIGH,
                        status="DETECTED",
                        title=f"Superseded Edition Referenced: {applicable_standard.standard_number}:{applicable_edition.year}",
                        description=(
                            f"The specification references {applicable_standard.standard_number}:{applicable_edition.year}, "
                            "which is a SUPERSEDED edition replaced by a newer revision."
                        ),
                        why_it_matters=(
                            "Procuring against superseded editions introduces obsolete testing procedures and legal vulnerabilities. "
                            "Regulatory bodies and dispute arbitration require compliance with the currently active edition."
                        ),
                        required_clarification=(
                            f"Update the standard reference from {applicable_edition.year} to the current active edition."
                        ),
                        affected_parameter="Standard Edition Citation",
                        current_value=str(applicable_edition.year),
                        expected_information="Current active edition year",
                        affected_standard_id=applicable_standard.id,
                        affected_edition_id=applicable_edition.id,
                        source="DEPENDENCY_GAP_ANALYZER",
                    )
                )

        # Check for unindexed amendment notice
        if applicable_standard.amendments and len(applicable_standard.amendments) > 0:
            if not ("amendment" in combined_text or "latest amendment" in combined_text):
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        gap_type=GapType.AMENDMENT_IMPACT_GAP,
                        severity=GapSeverity.LOW,
                        status="DETECTED",
                        title=f"Amendment Notice: {len(applicable_standard.amendments)} Published Amendment(s)",
                        description=(
                            f"{applicable_standard.standard_number} has {len(applicable_standard.amendments)} published amendment(s). "
                            "Amendment identified; clause impact not indexed."
                        ),
                        why_it_matters=(
                            "Published amendments may modify efficiency thresholds, tolerance values, or test procedure clauses. "
                            "Tender documents should explicitly stipulate compliance with all current amendments."
                        ),
                        required_clarification=(
                            f"Append 'along with all amendments published to date' to the citation of {applicable_standard.standard_number}."
                        ),
                        affected_parameter="Standard Amendment Clause",
                        expected_information="Latest published amendments",
                        affected_standard_id=applicable_standard.id,
                        source="DEPENDENCY_GAP_ANALYZER",
                    )
                )

        return gaps
