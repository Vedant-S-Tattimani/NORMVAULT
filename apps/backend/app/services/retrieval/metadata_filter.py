"""
Structured metadata filtering and scoring for candidate Indian Standards.
Applies verified domain rules without prematurely excluding plausible historical standards.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from app.models.standard import StandardStatus


@dataclass
class FilterCriteria:
    """Configurable structured filtering criteria for candidate retrieval."""
    division_code: Optional[str] = None
    include_withdrawn: bool = False
    is_mandatory_qco_only: bool = False


class StandardsMetadataFilter:
    """
    Applies deterministic filters and metadata-based feature scoring to candidate standards.
    """

    @staticmethod
    def evaluate(
        metadata: Dict[str, Any],
        criteria: FilterCriteria,
    ) -> Tuple[bool, float, List[str]]:
        """
        Evaluate a candidate standard against metadata criteria.
        
        Returns:
            passes: Whether candidate should be retained in the pool
            metadata_score: Normalized metadata relevance score [0.0 to 1.0]
            reasons: List of explanatory metadata match reasons
        """
        status_str = metadata.get("status", "ACTIVE")
        division = metadata.get("division_code")
        is_qco = bool(metadata.get("is_mandatory_qco", False))

        reasons: List[str] = []

        # 1. Hard Filter: Withdrawn standards (only excluded if explicitly not included)
        if not criteria.include_withdrawn and status_str in (StandardStatus.WITHDRAWN.value, "WITHDRAWN"):
            return False, 0.0, ["Withdrawn standard excluded by filter"]

        # 2. Hard Filter: Mandatory QCO constraint
        if criteria.is_mandatory_qco_only and not is_qco:
            return False, 0.0, ["Non-QCO standard excluded by mandatory QCO filter"]

        # 3. Hard Filter: Division filter if explicitly specified
        if criteria.division_code and criteria.division_code.strip():
            target_div = criteria.division_code.strip().upper()
            cand_div = (division or "").strip().upper()
            if cand_div and cand_div != target_div:
                return False, 0.0, [f"Excluded: Division {cand_div} does not match {target_div}"]

        # 4. Metadata Scoring Feature calculation [0.0 to 1.0]
        # Base score based on lifecycle status
        if status_str in (StandardStatus.ACTIVE.value, "ACTIVE"):
            base_score = 0.70
            reasons.append("Active canonical Indian Standard")
        elif status_str in (StandardStatus.AMENDED.value, "AMENDED"):
            base_score = 0.75
            reasons.append("Active standard with gazetted amendments")
        elif status_str in (StandardStatus.REVISED.value, "REVISED"):
            base_score = 0.60
            reasons.append("Prior revision of standard")
        else:
            base_score = 0.40
            reasons.append(f"Standard status: {status_str}")

        # QCO Boost
        if is_qco:
            base_score += 0.20
            qco_ref = metadata.get("qco_reference")
            ref_str = f" ({qco_ref})" if qco_ref else ""
            reasons.append(f"Statutory mandatory Quality Control Order{ref_str}")

        # Division alignment boost
        if criteria.division_code and division and division.upper() == criteria.division_code.upper():
            base_score += 0.10
            reasons.append(f"Exact match on BIS division {division}")

        final_metadata_score = round(min(base_score, 1.0), 4)
        return True, final_metadata_score, reasons
