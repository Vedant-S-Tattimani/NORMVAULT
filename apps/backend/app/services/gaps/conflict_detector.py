"""
Conflict and Contradiction Detector.
Identifies contradictory parameter values, opposing requirements, and conflicting standard citations
across clauses within a procurement specification.
"""

import re
from typing import List, Dict, Any, Optional
from app.models.gap import GapType, GapSeverity, SpecificationGap
from app.models.requirement import Requirement, TechnicalParameter
from app.services.currentness.citation_extractor import TenderCitationExtractor, CitationType


PARAMETER_CANONICAL_GROUPS = {
    "voltage": ["voltage", "rated voltage", "operating voltage", "supply voltage"],
    "frequency": ["frequency", "rated frequency", "supply frequency"],
    "phase": ["phase", "phases", "number of phases"],
    "rated_power": ["rated power", "rated output", "motor output", "power rating", "capacity", "power"],
    "efficiency_class": ["efficiency class", "efficiency", "energy efficiency class"],
    "speed": ["speed", "rated speed", "rpm", "synchronous speed"],
    "enclosure_ip": ["ip rating", "degree of protection", "ingress protection", "enclosure rating"],
    "insulation": ["insulation class", "insulation"],
    "duty": ["duty", "duty cycle", "duty type"],
}


class ConflictDetector:
    """
    Detects contradictions between extracted parameters and standard edition citations across requirements.
    """

    def __init__(self):
        self.citation_extractor = TenderCitationExtractor()

    def _canonicalize_param_name(self, name: str) -> str:
        clean = name.strip().lower().replace("_", " ")
        for canon, aliases in PARAMETER_CANONICAL_GROUPS.items():
            if clean == canon or clean in aliases:
                return canon
        return clean

    def _normalize_val(self, val: str, unit: Optional[str]) -> str:
        s = f"{val} {unit or ''}".strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    def detect_parameter_conflicts(
        self,
        specification_id: int,
        requirements: List[Requirement],
    ) -> List[SpecificationGap]:
        """
        Compares parameters across all requirements in the specification to detect numerical and categorical contradictions.
        """
        gaps: List[SpecificationGap] = []
        param_registry: Dict[str, List[Dict[str, Any]]] = {}

        for req in requirements:
            for p in req.parameters:
                canon_name = self._canonicalize_param_name(p.name)
                norm_val = self._normalize_val(p.normalized_value or p.original_value, p.unit)
                param_registry.setdefault(canon_name, []).append({
                    "requirement_id": req.id,
                    "requirement_text": req.extracted_text,
                    "param_name": p.name,
                    "original_value": p.original_value,
                    "normalized_value": norm_val,
                    "unit": p.unit,
                })

        # Check for contradictions within each canonical parameter group
        for canon_name, occurrences in param_registry.items():
            if len(occurrences) < 2:
                continue

            # Compare pairs of values
            seen_pairs = set()
            for i in range(len(occurrences)):
                for j in range(i + 1, len(occurrences)):
                    occ_a = occurrences[i]
                    occ_b = occurrences[j]

                    val_a = occ_a["normalized_value"]
                    val_b = occ_b["normalized_value"]

                    # If values are identical, no contradiction
                    if val_a == val_b:
                        continue

                    # Deduplicate pair
                    pair_key = tuple(sorted([f"{occ_a['requirement_id']}:{val_a}", f"{occ_b['requirement_id']}:{val_b}"]))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    gaps.append(
                        SpecificationGap(
                            specification_id=specification_id,
                            requirement_id=occ_a["requirement_id"],
                            gap_type=GapType.CONFLICTING_REQUIREMENTS,
                            severity=GapSeverity.CRITICAL,
                            status="DETECTED",
                            title=f"Contradictory Parameter Values for '{canon_name.title()}'",
                            description=(
                                f"Specification contains conflicting values for '{canon_name.title()}': "
                                f"Requirement #{occ_a['requirement_id']} specifies '{occ_a['original_value']}' "
                                f"whereas Requirement #{occ_b['requirement_id']} specifies '{occ_b['original_value']}'."
                            ),
                            why_it_matters=(
                                f"Tender bidders cannot reconcile conflicting {canon_name} specifications without a formal addendum. "
                                "This creates fatal ambiguity during commercial procurement and Factory Acceptance Testing."
                            ),
                            required_clarification=(
                                f"Clarify canonical {canon_name} requirement across all clauses. Issue a corrigendum stating "
                                f"whether '{occ_a['original_value']}' or '{occ_b['original_value']}' governs the procurement contract."
                            ),
                            affected_parameter=canon_name,
                            current_value=f"Req #{occ_a['requirement_id']}: {occ_a['original_value']} vs Req #{occ_b['requirement_id']}: {occ_b['original_value']}",
                            expected_information=f"Single unambiguous {canon_name} value",
                            source="CONFLICT_DETECTOR",
                            evidence_snippet=(
                                f"Clause A: \"{occ_a['requirement_text'][:80]}\" | "
                                f"Clause B: \"{occ_b['requirement_text'][:80]}\""
                            ),
                        )
                    )

        return gaps

    def detect_edition_inconsistencies(
        self,
        specification_id: int,
        requirements: List[Requirement],
    ) -> List[SpecificationGap]:
        """
        Detects conflicting standard edition citations across disparate clauses in the specification.
        """
        gaps: List[SpecificationGap] = []
        citations_by_standard: Dict[str, List[Dict[str, Any]]] = {}

        for req in requirements:
            citations = self.citation_extractor.extract_citations(req.extracted_text)
            for c in citations:
                if c.edition_year:
                    citations_by_standard.setdefault(c.standard_number, []).append({
                        "requirement_id": req.id,
                        "edition_year": c.edition_year,
                        "raw_citation": c.raw_citation,
                        "text_snippet": req.extracted_text[:100],
                    })

        for std_num, occurrences in citations_by_standard.items():
            years = set(o["edition_year"] for o in occurrences)
            if len(years) > 1:
                year_summary = ", ".join(f"Edition {y}" for y in sorted(years))
                citations_summary = "; ".join(f"Req #{o['requirement_id']}: '{o['raw_citation']}'" for o in occurrences)
                gaps.append(
                    SpecificationGap(
                        specification_id=specification_id,
                        gap_type=GapType.EDITION_INCONSISTENCY,
                        severity=GapSeverity.HIGH,
                        status="DETECTED",
                        title=f"Conflicting Edition Citations for {std_num}",
                        description=(
                            f"Procurement specification contains contradictory edition citations for {std_num} ({year_summary}). "
                            f"Details: {citations_summary}."
                        ),
                        why_it_matters=(
                            f"Multiple conflicting editions of {std_num} create legal and contractual uncertainty. "
                            "Testing tolerances and normative references vary between editions, leading to audit rejections."
                        ),
                        required_clarification=(
                            f"Harmonize all references to {std_num} across tender documents to cite a single valid edition."
                        ),
                        affected_parameter=f"{std_num} Edition",
                        current_value=year_summary,
                        expected_information=f"Unified edition citation for {std_num}",
                        source="CONFLICT_DETECTOR",
                        evidence_snippet=citations_summary,
                    )
                )

        return gaps
