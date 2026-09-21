"""
Decision Framework for Standards Applicability.
Transparent evidence-first adjudication logic.
Enforces that negative evidence (hard conflicts) overrides high retrieval similarity scores,
and implements principled abstention.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.models.applicability import ApplicabilityOutcome, AbstentionReason
from app.services.applicability.scope_analyzer import ScopeAnalysisResult
from app.services.applicability.product_matcher import ProductMatchResult
from app.services.applicability.application_matcher import ApplicationMatchResult
from app.services.applicability.parameter_comparator import ParameterComparisonResult
from app.services.applicability.citation_handler import CitationAnalysisResult


@dataclass
class AdjudicationResult:
    outcome: ApplicabilityOutcome
    abstention_reason: AbstentionReason
    applicability_score: float
    summary_rationale: str
    is_primary_candidate: bool
    primary_reason: Optional[str]
    reasons: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    component_evidence: Dict[str, Any]


class DecisionFramework:
    """
    Combines independent evidence channels into an auditable applicability determination.
    """

    @classmethod
    def evaluate_candidate(
        cls,
        standard_number: str,
        standard_title: str,
        standard_status: str,
        is_mandatory_qco: bool,
        scope_res: ScopeAnalysisResult,
        prod_res: ProductMatchResult,
        app_res: ApplicationMatchResult,
        param_res: ParameterComparisonResult,
        citation_res: CitationAnalysisResult,
        missing_info: List[Dict[str, Any]],
        retrieval_signals: Dict[str, float],
    ) -> AdjudicationResult:
        all_reasons = []
        all_conflicts = []

        # Aggregate reasons
        all_reasons.extend(scope_res.reasons)
        all_reasons.extend(prod_res.reasons)
        all_reasons.extend(app_res.reasons)
        all_reasons.extend(param_res.reasons)
        if citation_res.has_explicit_citation and citation_res.reason:
            all_reasons.insert(0, citation_res.reason)

        # Aggregate conflicts
        all_conflicts.extend(scope_res.conflicts)
        all_conflicts.extend(prod_res.conflicts)
        all_conflicts.extend(app_res.conflicts)
        all_conflicts.extend(param_res.conflicts)

        # Check standard lifecycle status
        if standard_status.upper() in {"WITHDRAWN", "SUPERSEDED"}:
            all_conflicts.insert(0, {
                "conflict_type": "OBSOLETE_STANDARD",
                "description": f"Standard {standard_number} is officially {standard_status.upper()} in BIS registry.",
                "severity": "FATAL",
                "tender_claim": "Active requirement specification",
                "standard_fact": f"BIS status: {standard_status.upper()}",
            })

        fatal_conflicts = [c for c in all_conflicts if c.get("severity") == "FATAL"]

        # Base component evidence dictionary
        comp_evidence = {
            "scope_match": scope_res.match_level,
            "product_match": prod_res.match_level,
            "application_match": app_res.match_level,
            "parameter_match": param_res.match_level,
            "explicit_reference": citation_res.has_explicit_citation,
            "exclusion_match": scope_res.has_exclusion,
            "specific_feature_match": scope_res.has_specific_feature,
            "is_mandatory_qco": is_mandatory_qco,
            "negative_evidence_count": len(all_conflicts),
            "retrieval_signals": retrieval_signals,
            "evidence_quality": "HIGH" if (scope_res.match_level == "EXACT" and prod_res.match_level == "EXACT") else "MEDIUM",
        }


        # -------------------------------------------------------------
        # RULE 1: HARD CONFLICTS OVERRIDE RETRIEVAL (Negative Evidence)
        # -------------------------------------------------------------
        if fatal_conflicts:
            conflict_descriptions = "; ".join(c["description"] for c in fatal_conflicts)
            return AdjudicationResult(
                outcome=ApplicabilityOutcome.NOT_APPLICABLE,
                abstention_reason=AbstentionReason.NONE,
                applicability_score=0.0,
                summary_rationale=(
                    f"Candidate standard {standard_number} is NOT APPLICABLE despite retrieval similarity. "
                    f"Fatal conflict(s) detected: {conflict_descriptions}."
                ),
                is_primary_candidate=False,
                primary_reason=None,
                reasons=all_reasons,
                conflicts=all_conflicts,
                component_evidence=comp_evidence,
            )

        # -------------------------------------------------------------
        # RULE 2: MISSING INFORMATION & ABSTENTION
        # -------------------------------------------------------------
        blocking_missing = [m for m in missing_info if m.get("impact") == "BLOCKING"]
        if blocking_missing and (prod_res.match_level in {"AMBIGUOUS", "CATEGORY"} or scope_res.match_level in {"UNCERTAIN", "PARTIAL"}):
            missing_fields = ", ".join(m["field_name"] for m in blocking_missing)
            return AdjudicationResult(
                outcome=ApplicabilityOutcome.INSUFFICIENT_EVIDENCE,
                abstention_reason=AbstentionReason.MISSING_REQUIREMENT_INFORMATION,
                applicability_score=0.25,
                summary_rationale=(
                    f"Engine abstained from definitive determination on {standard_number} due to missing procurement details. "
                    f"Required parameter(s) missing from tender: {missing_fields}."
                ),
                is_primary_candidate=False,
                primary_reason=None,
                reasons=all_reasons,
                conflicts=all_conflicts,
                component_evidence=comp_evidence,
            )

        # -------------------------------------------------------------
        # RULE 3: TRANSPARENT EVIDENCE SCORING
        # -------------------------------------------------------------
        # Multi-factor alignment index (0.0 to 1.0)
        scope_weights = {"EXACT": 1.0, "PARTIAL": 0.6, "UNCERTAIN": 0.3, "MISMATCH": 0.0}
        prod_weights = {"EXACT": 1.0, "CATEGORY": 0.7, "AMBIGUOUS": 0.3, "MISMATCH": 0.0}
        param_weights = {"COMPATIBLE": 1.0, "NOT_SPECIFIED": 0.6, "UNCHECKED": 0.5, "CONFLICT": 0.0}
        app_weights = {"COMPATIBLE": 1.0, "UNCERTAIN": 0.5, "MISMATCH": 0.0}

        w_scope = scope_weights.get(scope_res.match_level, 0.3)
        w_prod = prod_weights.get(prod_res.match_level, 0.3)
        w_param = param_weights.get(param_res.match_level, 0.5)
        w_app = app_weights.get(app_res.match_level, 0.5)
        w_cite = 1.0 if citation_res.has_explicit_citation else 0.0

        # Weighted composition: Scope (35%), Product (25%), Parameters (20%), Application (10%), Citation (10%)
        evidence_index = (
            0.35 * w_scope +
            0.25 * w_prod +
            0.20 * w_param +
            0.10 * w_app +
            0.10 * w_cite
        )
        evidence_index = round(min(1.0, max(0.0, evidence_index)), 3)

        # -------------------------------------------------------------
        # RULE 4: APPLICABLE / POSSIBLY_APPLICABLE ADJUDICATION
        # -------------------------------------------------------------
        if scope_res.match_level in {"EXACT", "PARTIAL"} and prod_res.match_level in {"EXACT", "CATEGORY"} and app_res.match_level != "MISMATCH":
            if (scope_res.match_level == "EXACT" and prod_res.match_level == "EXACT") or citation_res.has_explicit_citation:
                outcome = ApplicabilityOutcome.APPLICABLE
                rationale = (
                    f"Candidate standard {standard_number} is APPLICABLE. "
                    f"Verified scope and product identity directly align with procurement requirement without conflicting constraints."
                )
                if is_mandatory_qco:
                    rationale += " Note: This standard is subject to mandatory BIS Quality Control Orders (QCO)."
            else:
                outcome = ApplicabilityOutcome.POSSIBLY_APPLICABLE
                rationale = (
                    f"Candidate standard {standard_number} is POSSIBLY APPLICABLE. "
                    f"Scope overlaps on product category, but tender lacks specific detail to confirm exact sub-series applicability."
                )

            return AdjudicationResult(
                outcome=outcome,
                abstention_reason=AbstentionReason.NONE,
                applicability_score=evidence_index,
                summary_rationale=rationale,
                is_primary_candidate=False, # Designated during comparative resolution
                primary_reason=None,
                reasons=all_reasons,
                conflicts=all_conflicts,
                component_evidence=comp_evidence,
            )

        # Default fallback
        return AdjudicationResult(
            outcome=ApplicabilityOutcome.INSUFFICIENT_EVIDENCE,
            abstention_reason=AbstentionReason.INSUFFICIENT_EVIDENCE,
            applicability_score=evidence_index,
            summary_rationale=f"Insufficient verified evidence to confirm applicability of {standard_number}.",
            is_primary_candidate=False,
            primary_reason=None,
            reasons=all_reasons,
            conflicts=all_conflicts,
            component_evidence=comp_evidence,
        )

    @classmethod
    def resolve_candidate_roles(
        cls,
        candidates: List[AdjudicationResult],
    ) -> List[AdjudicationResult]:
        """
        Distinguishes Primary standard from Alternative candidates or flags Multiple Plausible Standards.
        Does NOT rely solely on retrieval score; uses evidence specificity and explicit citations.
        """
        if not candidates:
            return []

        applicable = [c for c in candidates if c.outcome == ApplicabilityOutcome.APPLICABLE]
        possibly_applicable = [c for c in candidates if c.outcome == ApplicabilityOutcome.POSSIBLY_APPLICABLE]

        if applicable:
            # Sort applicable by applicability_score descending, explicit reference priority, and specific feature match
            def primary_key(c: AdjudicationResult):
                has_cite = 1 if c.component_evidence.get("explicit_reference") else 0
                has_spec = 1 if c.component_evidence.get("specific_feature_match") else 0
                has_exact = 1 if c.component_evidence.get("scope_match") == "EXACT" and c.component_evidence.get("product_match") == "EXACT" else 0
                score = c.applicability_score
                return (has_cite, has_spec, has_exact, score)

            applicable.sort(key=primary_key, reverse=True)

            # Check if top two are indistinguishably tied
            if len(applicable) > 1:
                top_1 = applicable[0]
                top_2 = applicable[1]
                if (
                    primary_key(top_1) == primary_key(top_2)
                    and not top_1.component_evidence.get("explicit_reference")
                ):
                    # Multiple plausible standards! Do not arbitrarily crown one as primary.
                    for c in applicable:
                        c.outcome = ApplicabilityOutcome.POSSIBLY_APPLICABLE
                        c.abstention_reason = AbstentionReason.MULTIPLE_PLAUSIBLE_STANDARDS
                        c.is_primary_candidate = False
                        c.primary_reason = "Multiple standards exhibit identical applicability evidence without distinguishing tender specifics."
                    return candidates

            # Designate top applicable as primary
            primary = applicable[0]
            primary.is_primary_candidate = True
            primary.primary_reason = (
                "Designated primary standard based on superior evidence specificity, "
                "direct product scope match, and verified parameter compatibility."
            )
            if primary.component_evidence.get("explicit_reference"):
                primary.primary_reason += " Further reinforced by explicit tender citation."

        elif possibly_applicable:
            if len(possibly_applicable) > 1:
                for c in possibly_applicable:
                    c.abstention_reason = AbstentionReason.MULTIPLE_PLAUSIBLE_STANDARDS

        return candidates
