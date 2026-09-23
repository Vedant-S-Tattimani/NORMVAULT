"""
Government e-Marketplace (GeM) BOQ & Technical Compliance Schedule Exporter.
Converts Decision Packages into GeM-compliant procurement schedules.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.intelligence import ProcurementIntelligenceRun
from app.models.requirement import ProcurementSpecification, Requirement
from app.models.applicability import ApplicabilityAssessment, ApplicabilityOutcome
from app.models.gap import SpecificationGap, ReadinessState


def build_gem_boq_schedule(db: Session, run: ProcurementIntelligenceRun) -> Dict[str, Any]:
    """
    Constructs a structured GeM BOQ Compliance Schedule from an intelligence run.
    """
    spec = db.query(ProcurementSpecification).filter_by(id=run.specification_id).first()
    spec_title = spec.title if spec else f"Tender Specification #{run.specification_id}"
    tender_ref = spec.tender_reference if spec else f"NIT-{run.specification_id}"
    product_name = spec.target_product_name if spec else "Engineering Equipment"

    # Get applicable standards for this spec
    from app.models.standard import IndianStandard
    from app.models.applicability import ApplicabilityRun

    standards = db.query(IndianStandard).all()
    primary_standards: List[IndianStandard] = []
    
    # 1. Check if explicit applicability assessments exist
    app_runs = db.query(ApplicabilityRun).filter_by(specification_id=run.specification_id).all()
    if app_runs:
        run_ids = [r.id for r in app_runs]
        assessments = db.query(ApplicabilityAssessment).filter(
            ApplicabilityAssessment.run_id.in_(run_ids),
            ApplicabilityAssessment.outcome == ApplicabilityOutcome.APPLICABLE
        ).all()
        for a in assessments:
            if a.standard and a.standard not in primary_standards:
                primary_standards.append(a.standard)

    # 2. Match based on specification text if none found
    if not primary_standards and spec:
        for std in standards:
            if std.standard_number in (spec.raw_content or "") or (spec.target_product_name and spec.target_product_name.lower() in std.title.lower()):
                primary_standards.append(std)

    if not primary_standards and standards:
        primary_standards = [standards[0]]

    # Map parameters and requirements
    requirements = db.query(Requirement).filter_by(specification_id=run.specification_id).all()
    gaps = db.query(SpecificationGap).filter_by(specification_id=run.specification_id).all()

    boq_items: List[Dict[str, Any]] = []
    item_idx = 1

    for req in requirements:
        for param in req.parameters:
            boq_items.append({
                "item_no": item_idx,
                "category_name": product_name,
                "parameter_name": param.name.title(),
                "specified_value": f"{param.operator or ''} {param.target_value or param.original_value or ''} {param.unit or ''}".strip(),
                "governing_standard": primary_standards[0].standard_number if primary_standards else "Relevant BIS Standard",
                "clause_reference": req.clause_reference or "General Specification",
                "test_method_standard": param.test_method_standard or "As per applicable IS",
                "is_mandatory": True,
                "bidder_compliance": "COMPLIANT / YES",
                "bidder_offered_value": "",
                "remarks": "Mandatory technical parameter. Non-compliance constitutes technical disqualification."
            })
            item_idx += 1

    # In case no parameters extracted, list top requirements
    if not boq_items:
        for idx, req in enumerate(requirements[:10], start=1):
            boq_items.append({
                "item_no": idx,
                "category_name": product_name,
                "parameter_name": req.clause_reference or f"Requirement #{idx}",
                "specified_value": req.extracted_text[:120],
                "governing_standard": primary_standards[0].standard_number if primary_standards else "IS Mandate",
                "clause_reference": req.clause_reference or "General",
                "test_method_standard": "Per BIS Specification",
                "is_mandatory": True,
                "bidder_compliance": "COMPLIANT / YES",
                "bidder_offered_value": "",
                "remarks": "Mandatory technical requirement."
            })

    # Build statutory declarations required by GeM portal
    statutory_undertakings = [
        "The bidder unconditionally confirms that the offered goods hold a valid Bureau of Indian Standards (BIS) ISI Mark license or Compulsory Registration Scheme (CRS) registration as on the date of bid submission.",
        "The bidder certifies compliance with DPIIT Quality Control Orders (QCO) issued under Section 16 of the BIS Act 2016.",
        "Self-declaration certificates or unverified laboratory test certificates shall not be accepted in lieu of a valid BIS license."
    ]

    return {
        "gem_format_version": "GeM-BOQ-v4.0",
        "tender_metadata": {
            "tender_title": spec_title,
            "tender_reference": tender_ref,
            "target_product": product_name,
            "procurement_department": spec.department if spec else "Central Procurement Entity",
            "decision_package_run_id": run.id,
            "overall_readiness": run.readiness_state,
        },
        "standards_schedule": [
            {
                "standard_number": s.standard_number,
                "title": s.title,
                "is_mandatory_qco": s.is_mandatory_qco,
                "qco_reference": s.qco_reference,
            }
            for s in primary_standards
        ],
        "boq_parameters": boq_items,
        "statutory_undertakings": statutory_undertakings,
        "total_parameters_count": len(boq_items),
        "critical_gaps_count": run.critical_gap_count,
    }


def generate_gem_boq_csv(boq_data: Dict[str, Any]) -> str:
    """Serializes GeM BOQ parameters into GeM-compliant CSV format."""
    lines = [
        f"# GeM Technical BOQ Compliance Schedule - {boq_data['tender_metadata']['tender_title']}",
        f"# Tender Reference: {boq_data['tender_metadata']['tender_reference']}",
        f"# Readiness State: {boq_data['tender_metadata']['overall_readiness']}",
        "Item No,Product Category,Parameter Name,Specified Target Value,Governing Indian Standard,Clause Ref,Test Standard,Mandatory,Bidder Offered Value,Bidder Compliance (YES/NO),Remarks",
    ]

    for item in boq_data.get("boq_parameters", []):
        row = [
            str(item["item_no"]),
            f'"{item["category_name"]}"',
            f'"{item["parameter_name"]}"',
            f'"{item["specified_value"]}"',
            f'"{item["governing_standard"]}"',
            f'"{item["clause_reference"]}"',
            f'"{item["test_method_standard"]}"',
            "YES" if item["is_mandatory"] else "NO",
            '""',
            '""',
            f'"{item["remarks"]}"',
        ]
        lines.append(",".join(row))

    return "\n".join(lines)
