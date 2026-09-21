"""
Traceability and Standard Coverage Matrix Builder.
Constructs end-to-end traceability paths from tender requirements to standard clauses,
normative dependencies, and identified gaps, and compiles the Standard Coverage Matrix.
"""

from typing import List, Dict, Any, Optional
from app.models.gap import (
    GapType,
    GapSeverity,
    CoverageStatus,
    SpecificationGap,
)
from app.models.requirement import Requirement, TechnicalParameter
from app.models.standard import IndianStandard, StandardEdition
from app.schemas.gap import CoverageMatrixItem, TraceabilityNode
from app.services.gaps.completeness_analyzer import STANDARD_EXPECTED_BASELINES, CompletenessAnalyzer
from app.services.gaps.conflict_detector import PARAMETER_CANONICAL_GROUPS


class TraceabilityBuilder:
    """
    Builds the Standard Coverage Matrix and requirement traceability graph.
    """

    def __init__(self):
        self.completeness_analyzer = CompletenessAnalyzer()

    def build_coverage_matrix(
        self,
        specification_id: int,
        requirements: List[Requirement],
        gaps: List[SpecificationGap],
        applicable_standard: Optional[IndianStandard] = None,
        applicable_edition: Optional[StandardEdition] = None,
    ) -> List[CoverageMatrixItem]:
        """
        Compiles the Standard Coverage Matrix comparing tender specifications against
        applicable standard requirements.
        """
        matrix: List[CoverageMatrixItem] = []
        std_num = applicable_standard.standard_number if applicable_standard else "IS 12615"
        baseline = self.completeness_analyzer._get_baseline_for_standard(std_num)

        # Index gaps by affected parameter or gap type
        gaps_by_param: Dict[str, SpecificationGap] = {}
        for g in gaps:
            if g.affected_parameter:
                gaps_by_param[g.affected_parameter.lower()] = g

        # Index extracted parameters from requirements
        extracted_by_canon: Dict[str, List[TechnicalParameter]] = {}
        for req in requirements:
            for p in req.parameters:
                canon = self.completeness_analyzer._canonicalize_param_name(p.name)
                extracted_by_canon.setdefault(canon, []).append(p)

        # Check raw text for quick fallback matches
        combined_text = " ".join(r.extracted_text.lower() for r in requirements)

        # 1. Baseline technical parameters
        for b in baseline:
            c_name = b["canonical_name"]
            display = b["display_name"]
            clause = b["clause"]

            # Find matching gap if any
            param_gap = None
            for p_key, g in gaps_by_param.items():
                if c_name in p_key or display.lower() in p_key:
                    param_gap = g
                    break

            # Determine tender value
            params = extracted_by_canon.get(c_name, [])
            tender_val: Optional[str] = None
            if params:
                tender_val = ", ".join(
                    f"{getattr(p, 'normalized_value', None) or getattr(p, 'original_value', None) or getattr(p, 'target_value', '')} {p.unit or ''}".strip()
                    for p in params
                )
            elif c_name == "voltage" and "415 v" in combined_text:
                tender_val = "415 V"
            elif c_name == "frequency" and "50 hz" in combined_text:
                tender_val = "50 Hz"
            elif c_name == "efficiency_class":
                for ie in ["ie4", "ie3", "ie2"]:
                    if ie in combined_text:
                        tender_val = ie.upper()
                        break
            elif c_name == "enclosure_ip":
                for ip in ["ip65", "ip56", "ip55"]:
                    if ip in combined_text:
                        tender_val = ip.upper()
                        break

            # Determine coverage status
            if param_gap:
                if param_gap.gap_type == GapType.CONFLICTING_REQUIREMENTS:
                    status = CoverageStatus.CONFLICTING
                elif param_gap.gap_type in (GapType.AMBIGUOUS_REQUIREMENT, GapType.NON_MEASURABLE_REQUIREMENT):
                    status = CoverageStatus.AMBIGUOUS
                elif param_gap.gap_type == GapType.MISSING_PARAMETER:
                    status = CoverageStatus.MISSING
                else:
                    status = CoverageStatus.REVIEW
            elif tender_val:
                status = CoverageStatus.COVERED
            else:
                status = CoverageStatus.MISSING

            matrix.append(
                CoverageMatrixItem(
                    parameter_or_topic=display,
                    tender_value=tender_val or "(Not Specified in Tender)",
                    standard_requirement=b["expected_format"],
                    coverage_status=status,
                    clause_reference=clause,
                    standard_number=std_num,
                    evidence_snippet=param_gap.evidence_snippet if param_gap else None,
                    why_it_matters=b["why_it_matters"],
                )
            )

        # 2. Add Normative Dependency rows (Test Method, Safety, QCO Certification)
        # Test Method row
        test_gap = next((g for g in gaps if g.gap_type == GapType.MISSING_TEST_METHOD), None)
        matrix.append(
            CoverageMatrixItem(
                parameter_or_topic="Factory Acceptance Test (FAT) Method",
                tender_value="(Omitted)" if test_gap else "Specified in Tender",
                standard_requirement="IS 15999 (Methods for Determining Losses and Efficiency)",
                coverage_status=CoverageStatus.MISSING if test_gap else CoverageStatus.COVERED,
                clause_reference="IS 12615 Cl. 8 / IS 15999",
                standard_number="IS 15999",
                evidence_snippet=test_gap.evidence_snippet if test_gap else None,
                why_it_matters="Ensures objective loss and efficiency measurement during FAT.",
            )
        )

        # Safety Earthing row
        safety_gap = next((g for g in gaps if g.gap_type == GapType.MISSING_SAFETY_REQUIREMENT), None)
        matrix.append(
            CoverageMatrixItem(
                parameter_or_topic="Protective Earthing Terminals",
                tender_value="(Omitted)" if safety_gap else "Specified in Tender",
                standard_requirement="Dual distinct earthing terminals on frame and terminal box (IS 3043)",
                coverage_status=CoverageStatus.MISSING if safety_gap else CoverageStatus.COVERED,
                clause_reference="IS 3043 / IS/IEC 60034-1 Cl. 10",
                standard_number="IS 3043",
                evidence_snippet=safety_gap.evidence_snippet if safety_gap else None,
                why_it_matters="Protects personnel against electric shock during ground fault conditions.",
            )
        )

        # QCO Certification row
        qco_gap = next((g for g in gaps if g.gap_type == GapType.MISSING_CERTIFICATION_REQUIREMENT), None)
        matrix.append(
            CoverageMatrixItem(
                parameter_or_topic="Statutory Quality Control Order (ISI Mark)",
                tender_value="(Omitted)" if qco_gap else "Mandatory BIS License Required",
                standard_requirement="Mandatory BIS Standard Mark (ISI mark) under valid BIS License",
                coverage_status=CoverageStatus.MISSING if qco_gap else CoverageStatus.COVERED,
                clause_reference="BIS Act 2016 / Gazette QCO Notification",
                standard_number=std_num,
                evidence_snippet=qco_gap.evidence_snippet if qco_gap else None,
                why_it_matters="Statutory requirement; uncertified equipment cannot be legally procured or distributed.",
            )
        )

        return matrix

    def build_traceability_graph(
        self,
        specification_id: int,
        requirements: List[Requirement],
        gaps: List[SpecificationGap],
        applicable_standard: Optional[IndianStandard] = None,
        applicable_edition: Optional[StandardEdition] = None,
    ) -> List[TraceabilityNode]:
        """
        Builds end-to-end traceability paths linking tender requirements to parameters,
        standards, clauses, dependencies, coverage status, and identified gaps.
        """
        nodes: List[TraceabilityNode] = []
        std_num = applicable_standard.standard_number if applicable_standard else None
        ed_year = applicable_edition.year if applicable_edition else None

        # Index gaps by requirement_id
        gaps_by_req: Dict[int, List[SpecificationGap]] = {}
        for g in gaps:
            if g.requirement_id:
                gaps_by_req.setdefault(g.requirement_id, []).append(g)

        for req in requirements:
            req_gaps = gaps_by_req.get(req.id, [])

            if not req.parameters:
                # Requirement without structured parameters
                status = CoverageStatus.COVERED
                gap_type = None
                gap_desc = None
                if req_gaps:
                    gap_type = req_gaps[0].gap_type
                    gap_desc = req_gaps[0].description
                    if gap_type in (GapType.AMBIGUOUS_REQUIREMENT, GapType.NON_MEASURABLE_REQUIREMENT):
                        status = CoverageStatus.AMBIGUOUS
                    elif gap_type == GapType.CONFLICTING_REQUIREMENTS:
                        status = CoverageStatus.CONFLICTING
                    else:
                        status = CoverageStatus.REVIEW

                nodes.append(
                    TraceabilityNode(
                        requirement_id=req.id,
                        requirement_text=req.extracted_text,
                        standard_number=std_num,
                        edition_year=ed_year,
                        coverage_status=status,
                        associated_gap_type=gap_type,
                        gap_description=gap_desc,
                    )
                )
            else:
                for p in req.parameters:
                    # Find any gap relating to this parameter or requirement
                    matched_gap = next(
                        (
                            g for g in req_gaps
                            if (g.affected_parameter and g.affected_parameter.lower() in p.name.lower())
                            or g.gap_type == GapType.CONFLICTING_REQUIREMENTS
                        ),
                        None,
                    )
                    if not matched_gap and req_gaps:
                        matched_gap = req_gaps[0]

                    if matched_gap:
                        if matched_gap.gap_type == GapType.CONFLICTING_REQUIREMENTS:
                            p_status = CoverageStatus.CONFLICTING
                        elif matched_gap.gap_type in (GapType.AMBIGUOUS_REQUIREMENT, GapType.NON_MEASURABLE_REQUIREMENT):
                            p_status = CoverageStatus.AMBIGUOUS
                        else:
                            p_status = CoverageStatus.REVIEW
                    else:
                        p_status = CoverageStatus.COVERED

                    nodes.append(
                        TraceabilityNode(
                            requirement_id=req.id,
                            requirement_text=req.extracted_text,
                            parameter_name=p.name,
                            parameter_value=f"{getattr(p, 'normalized_value', None) or getattr(p, 'original_value', None) or getattr(p, 'target_value', '')} {p.unit or ''}".strip(),
                            standard_number=std_num,
                            edition_year=ed_year,
                            clause_reference=matched_gap.affected_clause if matched_gap else None,
                            coverage_status=p_status,
                            associated_gap_type=matched_gap.gap_type if matched_gap else None,
                            gap_description=matched_gap.description if matched_gap else None,
                        )
                    )

        return nodes
