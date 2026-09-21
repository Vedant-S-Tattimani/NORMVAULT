"""
Ambiguity and Non-Measurable Requirement Detector.
Detects vague, subjective, or non-verifiable language in procurement specifications
and generates structured clarification suggestions without fabricating technical values.
"""

import re
from typing import List, Dict, Any, Optional
from app.models.gap import GapType, GapSeverity, SpecificationGap


AMBIGUOUS_PATTERNS: List[Dict[str, Any]] = [
    {
        "pattern": r"\b(?:harsh|severe|rugged|aggressive)\s+(?:environments?|conditions?|atmospheres?)\b",
        "phrase": "harsh environments",
        "why_it_matters": (
            "Subjective environmental terms provide no objective criteria for enclosure ingress protection (IP code), "
            "cooling method, or corrosion protection. Tender evaluation cannot verify compliance without measurable parameters."
        ),
        "clarification_suggestion": (
            "Specify measurable environmental ratings, including Ingress Protection rating (IP code per IS/IEC 60034-5, "
            "e.g., IP55), ambient temperature limits (e.g., -10°C to +50°C), and relative humidity."
        ),
        "affected_parameter": "Ingress Protection / Ambient Envelope",
        "gap_type": GapType.AMBIGUOUS_REQUIREMENT,
        "severity": GapSeverity.MEDIUM,
    },
    {
        "pattern": r"\b(?:high|superior|premium|top|best[- ]in[- ]class|uncompromised)\s+quality\b",
        "phrase": "high quality",
        "why_it_matters": (
            "'High quality' is a marketing expression devoid of verifiable engineering tolerances or material standards. "
            "Quality must be defined via reference to normative standards or material test certificates."
        ),
        "clarification_suggestion": (
            "Replace subjective quality claims with specific material grades, inspection levels, or normative Indian Standard references."
        ),
        "affected_parameter": "Quality & Workmanship Standard",
        "gap_type": GapType.NON_MEASURABLE_REQUIREMENT,
        "severity": GapSeverity.MEDIUM,
    },
    {
        "pattern": r"\b(?:heavy[- ]duty|industrial[- ]grade|commercial[- ]grade)\b",
        "phrase": "heavy duty",
        "why_it_matters": (
            "'Heavy duty' does not map to a standard duty cycle classification under Indian Standards (e.g., S1 continuous, "
            "S2 short-time, S3 intermittent duty under IS 12615 / IS/IEC 60034-1)."
        ),
        "clarification_suggestion": (
            "Specify exact duty cycle classification according to applicable standard duty types (e.g., Duty Type S1 Continuous Duty per IS 12615)."
        ),
        "affected_parameter": "Duty Type / Operating Cycle",
        "gap_type": GapType.AMBIGUOUS_REQUIREMENT,
        "severity": GapSeverity.MEDIUM,
    },
    {
        "pattern": r"\b(?:high|ultra[- ]high|maximum|optimum)\s+efficiency\b",
        "phrase": "high efficiency",
        "why_it_matters": (
            "'High efficiency' lacks an efficiency class threshold or percentage benchmark. Energy-efficient equipment must "
            "specify an objective rating (e.g., IE2, IE3, or IE4 per IS 12615)."
        ),
        "clarification_suggestion": (
            "Specify the normative efficiency class (e.g., IE3 Premium Efficiency per IS 12615:2018) and designated test method (IS 15999)."
        ),
        "affected_parameter": "Efficiency Class",
        "gap_type": GapType.NON_MEASURABLE_REQUIREMENT,
        "severity": GapSeverity.HIGH,
    },
    {
        "pattern": r"\b(?:robust|rugged|sturdy|durable)\s+(?:construction|design|build|frame)\b",
        "phrase": "robust construction",
        "why_it_matters": (
            "Descriptive terms like 'robust' or 'durable' cannot be measured or inspected during Factory Acceptance Testing. "
            "Structural criteria must cite enclosure material (e.g., cast iron / fabricated steel) and mechanical vibration limits."
        ),
        "clarification_suggestion": (
            "Specify enclosure construction material (e.g., minimum Grade FG 200 Cast Iron frame) and mechanical vibration severity limits (IS 12075)."
        ),
        "affected_parameter": "Enclosure Material & Vibration Severity",
        "gap_type": GapType.NON_MEASURABLE_REQUIREMENT,
        "severity": GapSeverity.MEDIUM,
    },
    {
        "pattern": r"\b(?:good|satisfactory|acceptable|optimum)\s+performance\b",
        "phrase": "good performance",
        "why_it_matters": (
            "'Good performance' is non-verifiable without quantitative operating parameters, temperature rise limits, and power factor bounds."
        ),
        "clarification_suggestion": (
            "Specify operating parameter tolerances, full load power factor, and maximum permissible temperature rise (Class B/F limits per IS 12615)."
        ),
        "affected_parameter": "Performance Envelope & Temperature Rise",
        "gap_type": GapType.NON_MEASURABLE_REQUIREMENT,
        "severity": GapSeverity.MEDIUM,
    },
    {
        "pattern": r"\b(?:long|extended|maximum)\s+(?:service\s+)?life\b",
        "phrase": "long service life",
        "why_it_matters": (
            "Service life claims without operating hours, bearing L10h life ratings, or thermal endurance criteria cannot be audited or enforced."
        ),
        "clarification_suggestion": (
            "Specify bearing L10h life rating (e.g., minimum 40,000 hours for direct-coupled duty) and insulation thermal endurance class."
        ),
        "affected_parameter": "Bearing Life & Thermal Endurance",
        "gap_type": GapType.NON_MEASURABLE_REQUIREMENT,
        "severity": GapSeverity.LOW,
    },
    {
        "pattern": r"\b(?:state[- ]of[- ]the[- ]art|latest\s+technology|modern\s+design)\b",
        "phrase": "state of the art",
        "why_it_matters": (
            "Subjective technological buzzwords create ambiguity in procurement tenders and provide grounds for vendor bid protests."
        ),
        "clarification_suggestion": (
            "Remove subjective technological buzzwords and cite specific normative standard specifications or technical parameters."
        ),
        "affected_parameter": "Technical Baseline",
        "gap_type": GapType.AMBIGUOUS_REQUIREMENT,
        "severity": GapSeverity.LOW,
    },
]


class AmbiguityDetector:
    """
    Scans requirement texts for non-measurable and ambiguous expressions.
    Treats tender text strictly as passive data and resists prompt injection.
    """

    def detect_ambiguities(
        self,
        text: str,
        specification_id: Optional[int] = None,
        requirement_id: Optional[int] = None,
        parameters_count: int = 0,
    ) -> List[SpecificationGap]:
        """Convenience alias for detecting ambiguities in text."""
        return self.analyze_requirement(
            specification_id=specification_id or 0,
            requirement_id=requirement_id,
            text=text,
            parameters_count=parameters_count,
        )

    def analyze_requirement(
        self,
        specification_id: int,
        requirement_id: Optional[int],
        text: str,
        parameters_count: int = 0,
    ) -> List[SpecificationGap]:
        """
        Analyzes a single requirement clause for ambiguous language and non-measurable statements.
        """
        gaps: List[SpecificationGap] = []
        if not text or not text.strip():
            return gaps

        # Clean prompt injection tokens from analysis context
        clean_text = re.sub(r"(?i)(?:system\s+instruction|ignore\s+previous|override)", "[REDACTED]", text)

        # 1. Pattern-based ambiguity detection
        for pat_info in AMBIGUOUS_PATTERNS:
            match = re.search(pat_info["pattern"], clean_text, re.IGNORECASE)
            if match:
                matched_phrase = match.group(0)
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        requirement_id=requirement_id,
                        gap_type=pat_info["gap_type"],
                        severity=pat_info["severity"],
                        status="DETECTED",
                        title=f"Ambiguous Expression: '{matched_phrase}'",
                        description=(
                            f"Requirement contains non-measurable or subjective phrasing '{matched_phrase}'. "
                            f"{pat_info['why_it_matters']}"
                        ),
                        why_it_matters=pat_info["why_it_matters"],
                        required_clarification=pat_info["clarification_suggestion"],
                        affected_parameter=pat_info["affected_parameter"],
                        current_value=matched_phrase,
                        expected_information="Quantifiable engineering limit or normative standard citation",
                        source="AMBIGUITY_DETECTOR",
                        evidence_snippet=text[max(0, match.start() - 30):min(len(text), match.end() + 30)],
                    )
                )

        # 2. General non-measurable requirement check
        # If text makes broad claims ("shall be supplied in proper manner", "satisfactory operation")
        # and has zero quantitative parameters extracted:
        if parameters_count == 0 and len(clean_text.split()) > 6:
            vague_indicators = [
                "satisfactory", "proper", "suitable", "appropriate", "adequate",
                "reliable", "standard quality", "good condition"
            ]
            found_vague = [v for v in vague_indicators if re.search(rf"\b{v}\b", clean_text, re.IGNORECASE)]
            if found_vague and not any(g.gap_type in (GapType.AMBIGUOUS_REQUIREMENT, GapType.NON_MEASURABLE_REQUIREMENT) for g in gaps):
                v_str = ", ".join(found_vague)
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        requirement_id=requirement_id,
                        gap_type=GapType.NON_MEASURABLE_REQUIREMENT,
                        severity=GapSeverity.MEDIUM,
                        status="DETECTED",
                        title=f"Non-Measurable Requirement Clause ({v_str})",
                        description=(
                            f"Requirement clause relies on subjective terms ({v_str}) without specifying measurable "
                            "technical parameters, tolerances, or acceptance criteria."
                        ),
                        why_it_matters=(
                            "Without quantifiable criteria, bid evaluation and inspection cannot objectively determine compliance."
                        ),
                        required_clarification="Define quantifiable numerical ranges, units, and acceptable testing methods.",
                        current_value=v_str,
                        expected_information="Numerical values with units and tolerances",
                        source="AMBIGUITY_DETECTOR",
                        evidence_snippet=clean_text[:120],
                    )
                )

        return gaps
