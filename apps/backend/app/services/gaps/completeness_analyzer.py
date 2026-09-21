"""
Completeness Analyzer for Procurement Specifications.
Compares extracted procurement parameters against standard expected technical baselines
to identify missing operational, electrical, mechanical, and safety parameters.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from app.models.gap import (
    GapType,
    GapSeverity,
    CompletenessCategory,
    SpecificationGap,
)
from app.models.requirement import Requirement, TechnicalParameter
from app.models.standard import IndianStandard, StandardEdition
from app.services.gaps.conflict_detector import PARAMETER_CANONICAL_GROUPS


STANDARD_EXPECTED_BASELINES: Dict[str, List[Dict[str, Any]]] = {
    "IS 12615": [
        {
            "canonical_name": "rated_power",
            "display_name": "Rated Output (kW / HP)",
            "severity": GapSeverity.CRITICAL,
            "clause": "IS 12615:2018 Cl. 5.1 / Table 1-4",
            "why_it_matters": (
                "Rated output in kW directly defines frame size, full-load current, starting torque, "
                "and the applicable statutory minimum energy performance (MEPS) efficiency limits."
            ),
            "required_clarification": "Specify the rated continuous output in kilowatts (kW) or horsepower (HP).",
            "expected_format": "Numerical rating in kW (e.g., 15 kW)",
        },
        {
            "canonical_name": "voltage",
            "display_name": "Rated Voltage (V)",
            "severity": GapSeverity.CRITICAL,
            "clause": "IS 12615:2018 Cl. 5.2 / IS/IEC 60034-1 Cl. 6",
            "why_it_matters": (
                "Rated voltage defines stator winding design, turn insulation, terminal box sizing, "
                "and full-load operating current. Missing voltage prevents equipment manufacture and inspection."
            ),
            "required_clarification": "Specify rated supply voltage (e.g., 415 V ± 10%, 3-phase, 50 Hz).",
            "expected_format": "Voltage in Volts with tolerance (e.g., 415 V ± 10%)",
        },
        {
            "canonical_name": "frequency",
            "display_name": "Rated Frequency (Hz)",
            "severity": GapSeverity.HIGH,
            "clause": "IS 12615:2018 Cl. 5.3",
            "why_it_matters": (
                "Supply frequency directly determines magnetic core saturation and synchronous speed. "
                "Indian standard grid supply requires 50 Hz ± 5%."
            ),
            "required_clarification": "Confirm standard rated supply frequency of 50 Hz ± 5%.",
            "expected_format": "50 Hz ± 5%",
        },
        {
            "canonical_name": "speed",
            "display_name": "Synchronous Speed / Number of Poles",
            "severity": GapSeverity.HIGH,
            "clause": "IS 12615:2018 Cl. 5.4 / Table 1-4",
            "why_it_matters": (
                "Nominal efficiency values in IS 12615 vary substantially between 2-pole (3000 RPM), "
                "4-pole (1500 RPM), 6-pole (1000 RPM), and 8-pole (750 RPM) machines."
            ),
            "required_clarification": "Specify synchronous speed in RPM (e.g., 1500 RPM) or number of poles (e.g., 4 Poles).",
            "expected_format": "Number of poles (2, 4, 6, 8) or synchronous RPM",
        },
        {
            "canonical_name": "efficiency_class",
            "display_name": "Energy Efficiency Class (IE Class)",
            "severity": GapSeverity.CRITICAL,
            "clause": "IS 12615:2018 Cl. 4.2 / BEE & MoP Mandates",
            "why_it_matters": (
                "IS 12615 defines energy efficiency classes (IE2, IE3, IE4). Statutory Quality Control Orders "
                "mandate minimum efficiency class IE2/IE3 for industrial induction motors in India."
            ),
            "required_clarification": "Specify the energy efficiency classification (e.g., IE3 Premium Efficiency per IS 12615:2018).",
            "expected_format": "IE2, IE3, or IE4",
        },
        {
            "canonical_name": "duty",
            "display_name": "Duty Type / Operating Cycle",
            "severity": GapSeverity.HIGH,
            "clause": "IS 12615:2018 Cl. 4.1 / IS/IEC 60034-1 Cl. 4",
            "why_it_matters": (
                "IS 12615 covers motors rated for Duty Type S1 (continuous duty). Non-continuous duty cycles (S2-S9) "
                "have different thermal ratings and may fall outside standard energy labeling tables."
            ),
            "required_clarification": "Specify duty cycle classification (e.g., Duty Type S1 Continuous per IS/IEC 60034-1).",
            "expected_format": "Duty Type S1 (Continuous)",
        },
        {
            "canonical_name": "enclosure_ip",
            "display_name": "Degree of Protection (IP Rating)",
            "severity": GapSeverity.HIGH,
            "clause": "IS/IEC 60034-5 / IS 12615 Cl. 7.1",
            "why_it_matters": (
                "Ingress protection code defines environmental suitability against dust and moisture. "
                "Absence of an IP rating creates risk of premature insulation failure or electrical flashover."
            ),
            "required_clarification": "Specify minimum Degree of Protection (e.g., IP55 totally enclosed fan-cooled).",
            "expected_format": "IP55, IP56, or IP65 per IS/IEC 60034-5",
        },
        {
            "canonical_name": "insulation",
            "display_name": "Insulation Class & Temperature Rise",
            "severity": GapSeverity.HIGH,
            "clause": "IS 12615 Cl. 6 / IS/IEC 60034-1 Cl. 8",
            "why_it_matters": (
                "Insulation class governs maximum thermal endurance and operational lifespan. Standard industrial "
                "motors typically require Class F insulation with Class B temperature rise."
            ),
            "required_clarification": "Specify insulation class and temperature rise limits (e.g., Class F insulation with Class B temperature rise).",
            "expected_format": "Class F insulation with Class B temperature rise",
        },
        {
            "canonical_name": "mounting",
            "display_name": "Mounting Arrangement (IM Code)",
            "severity": GapSeverity.MEDIUM,
            "clause": "IS 1231 / IS/IEC 60034-7",
            "why_it_matters": (
                "Mechanical installation requires distinct shaft heights, feet, or flange dimensions. "
                "Foot mounting (B3/IM1001) vs. Flange mounting (B5/IM3001) must be defined for physical fitment."
            ),
            "required_clarification": "Specify mounting arrangement (e.g., Foot Mounted B3, Flange Mounted B5, or Foot-Flange B35).",
            "expected_format": "B3, B5, or B35 mounting per IS 1231",
        },
    ],
    "GENERIC_ELECTRICAL": [
        {
            "canonical_name": "rated_power",
            "display_name": "Rated Power / Capacity",
            "severity": GapSeverity.CRITICAL,
            "clause": "Technical Rating Clause",
            "why_it_matters": "Rated capacity defines primary operational sizing and electrical protection requirements.",
            "required_clarification": "Specify the rated electrical or mechanical capacity with standard engineering units.",
            "expected_format": "Numerical capacity with unit (kW, kVA, or HP)",
        },
        {
            "canonical_name": "voltage",
            "display_name": "Rated Operating Voltage",
            "severity": GapSeverity.CRITICAL,
            "clause": "Supply Rating Clause",
            "why_it_matters": "Operating voltage dictates insulation coordination and switchgear compatibility.",
            "required_clarification": "Specify nominal operating voltage and permissible tolerance.",
            "expected_format": "Voltage in Volts (e.g., 415 V / 230 V)",
        },
        {
            "canonical_name": "frequency",
            "display_name": "Operating Frequency",
            "severity": GapSeverity.HIGH,
            "clause": "Supply Frequency Clause",
            "why_it_matters": "Indian national grid requires standard 50 Hz operation.",
            "required_clarification": "Specify supply frequency (50 Hz ± 5%).",
            "expected_format": "50 Hz ± 5%",
        },
    ],
}


class CompletenessAnalyzer:
    """
    Evaluates whether a specification provides sufficient technical parameters to comply with
    applicable Indian Standards, identifying missing parameters with zero hallucination.
    """

    def _canonicalize_param_name(self, name: str) -> str:
        clean = name.strip().lower().replace("_", " ")
        for canon, aliases in PARAMETER_CANONICAL_GROUPS.items():
            if clean == canon or clean in aliases:
                return canon
        return clean

    def _get_baseline_for_standard(self, standard_number: Optional[str]) -> List[Dict[str, Any]]:
        if not standard_number:
            return STANDARD_EXPECTED_BASELINES["GENERIC_ELECTRICAL"]
        
        std_clean = standard_number.upper().replace(" ", "").replace("-", "")
        for key, baseline in STANDARD_EXPECTED_BASELINES.items():
            key_clean = key.upper().replace(" ", "").replace("-", "")
            if key_clean in std_clean or std_clean in key_clean:
                return baseline

        # Fallback to generic electrical baseline if unknown standard
        return STANDARD_EXPECTED_BASELINES["GENERIC_ELECTRICAL"]

    def analyze_completeness(
        self,
        specification_id: int,
        requirements: List[Requirement],
        applicable_standard: Optional[IndianStandard] = None,
        applicable_edition: Optional[StandardEdition] = None,
    ) -> Tuple[List[SpecificationGap], Dict[str, Any]]:
        """
        Analyzes the specification for missing standard parameters.
        Returns:
            - List of SpecificationGap records (type MISSING_PARAMETER)
            - Completeness metrics dictionary with expected, present, missing, and completeness_category.
        """
        gaps: List[SpecificationGap] = []
        std_number = applicable_standard.standard_number if applicable_standard else None
        baseline = self._get_baseline_for_standard(std_number)

        # Extract all canonical parameter names present in tender
        present_canonical_params: Set[str] = set()
        param_objects: List[TechnicalParameter] = []
        for req in requirements:
            for p in req.parameters:
                param_objects.append(p)
                canon = self._canonicalize_param_name(p.name)
                present_canonical_params.add(canon)
                # Also check common aliases in raw text if parameter extraction missed it
                for c_group, aliases in PARAMETER_CANONICAL_GROUPS.items():
                    if any(a in p.name.lower() for a in aliases):
                        present_canonical_params.add(c_group)

        # Secondary scan over raw requirement text for un-extracted standard keywords
        combined_text = " ".join(r.extracted_text.lower() for r in requirements)
        if "415 v" in combined_text or "415v" in combined_text or "voltage" in combined_text:
            present_canonical_params.add("voltage")
        if "50 hz" in combined_text or "50hz" in combined_text:
            present_canonical_params.add("frequency")
        if "rpm" in combined_text or "poles" in combined_text or "pole" in combined_text:
            present_canonical_params.add("speed")
        if "kw" in combined_text or "hp" in combined_text:
            present_canonical_params.add("rated_power")
        if "ie2" in combined_text or "ie3" in combined_text or "ie4" in combined_text:
            present_canonical_params.add("efficiency_class")
        if "ip55" in combined_text or "ip56" in combined_text or "ip65" in combined_text or "ip 55" in combined_text:
            present_canonical_params.add("enclosure_ip")
        if "class f" in combined_text or "class b" in combined_text or "insulation" in combined_text:
            present_canonical_params.add("insulation")
        if "duty" in combined_text or "s1" in combined_text:
            present_canonical_params.add("duty")
        if "b3" in combined_text or "b5" in combined_text or "foot mounted" in combined_text or "flange mounted" in combined_text:
            present_canonical_params.add("mounting")

        # Evaluate baseline parameters against present parameters
        total_expected = len(baseline)
        elements_present = 0
        elements_missing = 0

        for expected in baseline:
            c_name = expected["canonical_name"]
            if c_name in present_canonical_params:
                elements_present += 1
            else:
                elements_missing += 1
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        gap_type=GapType.MISSING_PARAMETER,
                        severity=expected["severity"],
                        status="DETECTED",
                        title=f"Missing Parameter: {expected['display_name']}",
                        description=(
                            f"The procurement specification omits required parameter '{expected['display_name']}'. "
                            f"{expected['why_it_matters']}"
                        ),
                        why_it_matters=expected["why_it_matters"],
                        required_clarification=expected["required_clarification"],
                        affected_parameter=expected["display_name"],
                        expected_information=expected["expected_format"],
                        affected_standard_id=applicable_standard.id if applicable_standard else None,
                        affected_edition_id=applicable_edition.id if applicable_edition else None,
                        affected_clause=expected["clause"],
                        source="COMPLETENESS_ANALYZER",
                    )
                )

        # Categorize completeness
        if not applicable_standard and elements_present == 0:
            category = CompletenessCategory.UNRESOLVED
        elif elements_missing == 0:
            category = CompletenessCategory.SUFFICIENT
        elif elements_present >= total_expected / 2:
            category = CompletenessCategory.PARTIALLY_COMPLETE
        else:
            category = CompletenessCategory.INCOMPLETE

        metrics = {
            "total_expected_elements": total_expected,
            "elements_present": elements_present,
            "elements_missing": elements_missing,
            "completeness_category": category,
        }

        return gaps, metrics
