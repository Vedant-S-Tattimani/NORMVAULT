"""
Multi-Bidder Comparative Evaluation Service.
Performs deterministic, side-by-side compliance benchmarking across competing vendor submissions.
Validates against governing Indian Standards, DPIIT QCO statutory mandates, and specified technical thresholds.
"""
from datetime import datetime, timezone
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.requirement import ProcurementSpecification, Requirement, TechnicalParameter
from app.models.standard import IndianStandard, StandardStatus
from app.schemas.comparative import (
    ComparativeEvaluationRequest,
    ComparativeEvaluationResponse,
    BidderSubmission,
    BidderEvaluationResult,
    ParameterComplianceDetail,
)


def _parse_numeric(val: str) -> Tuple[bool, float]:
    """Attempts to extract a leading or prominent float from a string."""
    match = re.search(r"[-+]?\d*\.?\d+", val.replace(",", ""))
    if match:
        try:
            return True, float(match.group())
        except ValueError:
            pass
    return False, 0.0


def _evaluate_efficiency_classes(target: str, offered: str) -> Tuple[bool, str]:
    """Evaluates efficiency hierarchy (e.g. IE4 > IE3 > IE2 > IE1)."""
    hierarchy = {"IE1": 1, "IE2": 2, "IE3": 3, "IE4": 4, "IE5": 5}
    target_rank = next((rank for code, rank in hierarchy.items() if code in target.upper()), None)
    offered_rank = next((rank for code, rank in hierarchy.items() if code in offered.upper()), None)
    if target_rank and offered_rank:
        if offered_rank >= target_rank:
            return True, "Meets or exceeds specified energy efficiency class."
        return False, f"Offered class ({offered}) is lower than specified mandatory minimum ({target})."
    return False, "Unrecognized efficiency class."


class ComparativeEvaluator:
    """Evaluates multiple vendor bids against a procurement specification."""

    def evaluate(self, db: Session, request: ComparativeEvaluationRequest) -> ComparativeEvaluationResponse:
        spec = db.query(ProcurementSpecification).filter_by(id=request.specification_id).first()
        if not spec:
            raise ValueError(f"Specification ID {request.specification_id} not found.")

        # Gather tender parameters
        tender_params: List[TechnicalParameter] = []
        requirements = db.query(Requirement).filter_by(specification_id=spec.id).all()
        for r in requirements:
            tender_params.extend(r.parameters)

        # Query only obsolete/superseded standards for checking disqualifying bidder citations
        obsolete_standards = db.query(IndianStandard).filter(
            IndianStandard.status.in_([StandardStatus.SUPERSEDED, StandardStatus.WITHDRAWN])
        ).all()
        standards_by_num = {s.standard_number.replace(" ", "").upper(): s for s in obsolete_standards}

        # Check if tender has mandatory QCO by querying active QCO standard numbers only
        qco_standards = db.query(IndianStandard.standard_number).filter(IndianStandard.is_mandatory_qco == True).all()
        raw_text = spec.raw_content or ""
        has_mandatory_qco = any(q[0] in raw_text for q in qco_standards)

        results: List[BidderEvaluationResult] = []

        for bidder in request.bidders:
            eval_result = self._evaluate_bidder(
                bidder=bidder,
                tender_params=tender_params,
                standards_by_num=standards_by_num,
                has_mandatory_qco=has_mandatory_qco,
            )
            results.append(eval_result)

        # Sort: Qualified first (descending score), then disqualified
        results.sort(key=lambda r: (1 if r.is_technically_qualified else 0, r.compliance_score_percent), reverse=True)

        qualified_count = sum(1 for r in results if r.is_technically_qualified)
        disqualified_count = len(results) - qualified_count

        return ComparativeEvaluationResponse(
            specification_id=spec.id,
            tender_reference=spec.tender_reference or f"NIT-{spec.id}",
            tender_title=spec.title or f"Tender Specification #{spec.id}",
            evaluated_at=datetime.now(timezone.utc).isoformat(),
            total_bidders=len(results),
            qualified_bidders_count=qualified_count,
            disqualified_bidders_count=disqualified_count,
            results=results,
        )

    def _evaluate_bidder(
        self,
        bidder: BidderSubmission,
        tender_params: List[TechnicalParameter],
        standards_by_num: Dict[str, IndianStandard],
        has_mandatory_qco: bool,
    ) -> BidderEvaluationResult:
        disqualifications: List[str] = []
        superseded_standards: List[str] = []

        # 1. Statutory BIS License Verification
        if not bidder.bis_license_valid and has_mandatory_qco:
            disqualifications.append(
                "DISQUALIFICATION: Bidder does not hold a valid BIS ISI Mark / CRS License, violating DPIIT Quality Control Order (QCO)."
            )

        # 2. Check standards cited by bidder
        offered_map: Dict[str, Any] = {}
        for p in bidder.parameters:
            offered_map[p.parameter_name.strip().lower()] = p
            if p.offered_standard:
                norm_key = p.offered_standard.replace(" ", "").upper()
                # Check if standard is known and superseded
                matched_std = next((s for k, s in standards_by_num.items() if k in norm_key or norm_key in k), None)
                if matched_std and matched_std.status in (StandardStatus.SUPERSEDED, StandardStatus.WITHDRAWN):
                    superseded_standards.append(p.offered_standard)
                    disqualifications.append(
                        f"DISQUALIFICATION: Bidder offered obsolete/superseded standard ({p.offered_standard}). DPIIT orders mandate current revisions."
                    )

        # 3. Parameter-by-Parameter Evaluation
        param_evals: List[ParameterComplianceDetail] = []
        compliant_count = 0
        total_evaluable = max(len(tender_params), 1)

        for param in tender_params:
            p_name = param.name.strip()
            p_key = p_name.lower()
            tender_val = f"{param.operator or ''} {param.target_value or param.original_value or ''} {param.unit or ''}".strip()
            offered_param = offered_map.get(p_key)

            if not offered_param:
                param_evals.append(
                    ParameterComplianceDetail(
                        parameter_name=p_name,
                        tender_specified_value=tender_val,
                        offered_value="NOT SUBMITTED",
                        status="NOT_OFFERED",
                        deviation_reason="Parameter omitted from technical schedule.",
                    )
                )
                continue

            offered_val = offered_param.offered_value.strip()

            # Check if this is an efficiency parameter (IE class)
            if "IE" in tender_val.upper() and "IE" in offered_val.upper():
                is_comp, reason = _evaluate_efficiency_classes(tender_val, offered_val)
                if is_comp:
                    compliant_count += 1
                    status = "COMPLIANT"
                else:
                    status = "NON_COMPLIANT"
                param_evals.append(
                    ParameterComplianceDetail(
                        parameter_name=p_name,
                        tender_specified_value=tender_val,
                        offered_value=offered_val,
                        status=status,
                        deviation_reason=reason if not is_comp else None,
                    )
                )
                continue

            # Numeric comparison
            is_num_target, num_target = _parse_numeric(param.target_value or param.original_value or "")
            is_num_offered, num_offered = _parse_numeric(offered_val)

            if is_num_target and is_num_offered:
                op = param.operator or ">="
                is_comp = True
                dev_reason = None
                if op == ">=" and num_offered < num_target:
                    is_comp = False
                    dev_reason = f"Offered {num_offered} is below mandatory minimum {num_target}."
                elif op == "<=" and num_offered > num_target:
                    is_comp = False
                    dev_reason = f"Offered {num_offered} exceeds mandatory maximum {num_target}."
                elif op == "==" and abs(num_offered - num_target) > 0.01:
                    is_comp = False
                    dev_reason = f"Offered {num_offered} does not match required value {num_target}."

                if is_comp:
                    compliant_count += 1
                    status = "COMPLIANT"
                else:
                    status = "NON_COMPLIANT"

                param_evals.append(
                    ParameterComplianceDetail(
                        parameter_name=p_name,
                        tender_specified_value=tender_val,
                        offered_value=offered_val,
                        status=status,
                        deviation_reason=dev_reason,
                    )
                )
            else:
                # String / Categorical comparison
                clean_target = (param.target_value or param.original_value or "").strip().lower()
                clean_offered = offered_val.lower()
                if clean_target in clean_offered or clean_offered in clean_target:
                    compliant_count += 1
                    status = "COMPLIANT"
                    dev_reason = None
                else:
                    status = "DEVIATION"
                    dev_reason = f"Offered '{offered_val}' differs from specified requirement '{tender_val}'."

                param_evals.append(
                    ParameterComplianceDetail(
                        parameter_name=p_name,
                        tender_specified_value=tender_val,
                        offered_value=offered_val,
                        status=status,
                        deviation_reason=dev_reason,
                    )
                )

        score = round((compliant_count / total_evaluable) * 100.0, 1)

        # Technical Qualification logic
        is_qualified = (len(disqualifications) == 0) and (score >= 75.0)
        if score < 75.0 and len(disqualifications) == 0:
            disqualifications.append(f"Technical score of {score}% is below the minimum qualifying threshold (75%).")

        return BidderEvaluationResult(
            bidder_name=bidder.bidder_name,
            bidder_id=bidder.bidder_id,
            offered_model=bidder.offered_model,
            compliance_score_percent=score,
            is_technically_qualified=is_qualified,
            disqualification_reasons=disqualifications,
            superseded_standards_used=list(set(superseded_standards)),
            parameter_evaluations=param_evals,
        )
