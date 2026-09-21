"""
Missing Information Detector for Standards Applicability.
Identifies unstated technical parameters or operating conditions required for a definitive standard determination.
"""

import re
from typing import List, Optional, Dict, Any
from app.models.requirement import TechnicalParameter


class MissingInformationDetector:
    """
    Evaluates whether a requirement or procurement tender lacks critical attributes
    necessary to adjudicate standards applicability without guesswork.
    """

    @classmethod
    def detect(
        cls,
        requirement_text: str,
        target_product_name: Optional[str] = None,
        parameters: Optional[List[TechnicalParameter]] = None,
    ) -> List[Dict[str, Any]]:
        combined = f"{target_product_name or ''} {requirement_text}".lower()
        param_names = {p.name.lower() for p in (parameters or [])}
        param_values = " ".join((p.target_value or "") for p in (parameters or [])).lower()

        missing_items: List[Dict[str, Any]] = []

        # --- Check Rotating Electrical Machines / Motors ---
        if "motor" in combined or "induction" in combined:
            # 1. Voltage
            has_voltage = "volt" in combined or "415" in combined or "v" in param_names or any("v" in (p.unit or "") for p in (parameters or []))
            if not has_voltage:
                missing_items.append({
                    "field_name": "rated_voltage",
                    "why_it_matters": "Rated voltage (e.g. 415 V vs 3.3 kV) is necessary to determine low-voltage vs medium-voltage standard classification.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "Specify nominal operating voltage (e.g. 415 V, 3-Phase).",
                })

            # 2. Supply Frequency
            has_freq = "hz" in combined or "frequency" in combined or "hertz" in combined
            if not has_freq:
                missing_items.append({
                    "field_name": "supply_frequency",
                    "why_it_matters": "Standard Indian grid frequency (50 Hz) is required to ensure motor performance complies with BIS rated speed limits.",
                    "impact": "NON_BLOCKING",
                    "suggested_clarification": "Confirm operating frequency is 50 Hz ± 5%.",
                })

            # 3. Duty Cycle
            has_duty = "duty" in combined or "s1" in combined or "continuous" in combined
            if not has_duty:
                missing_items.append({
                    "field_name": "duty_cycle",
                    "why_it_matters": "Duty type (continuous S1 vs intermittent S2–S8) dictates motor thermal rise and applicable efficiency testing standards.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "Clarify if motor is for continuous duty (S1) or cyclic operation.",
                })

            # 4. Motor Construction Type
            has_type = any(t in combined for t in ["squirrel cage", "induction", "synchronous", "slip ring", "permanent magnet"])
            if not has_type:
                missing_items.append({
                    "field_name": "motor_construction_type",
                    "why_it_matters": "Motor topology (e.g. squirrel cage induction vs slip-ring) is required to distinguish IS 12615 from other motor specifications.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "Specify whether squirrel cage induction or wound rotor.",
                })

        # --- Check Pipes / HDPE ---
        elif "pipe" in combined or "hdpe" in combined or "polyethylene" in combined:
            # 1. Pressure Class / PN
            has_pn = "pn" in combined or "pressure" in combined or "bar" in combined
            if not has_pn:
                missing_items.append({
                    "field_name": "pressure_rating_pn",
                    "why_it_matters": "Working pressure rating (e.g. PN 6, PN 10, PN 16) is necessary to verify wall thickness and standard SDR table.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "State the required working pressure (e.g. PN 10).",
                })

            # 2. Material Grade
            has_grade = any(g in combined for g in ["pe 100", "pe 80", "pe 63", "pe100", "pe80"])
            if not has_grade:
                missing_items.append({
                    "field_name": "polyethylene_grade",
                    "why_it_matters": "Polyethylene raw material designation (PE 80 vs PE 100) determines stress regression rating under IS 4984.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "Specify resin grade (e.g. PE 100).",
                })

        # --- Check Structural Steel ---
        elif "steel" in combined and any(w in combined for w in ["structural", "plate", "beam", "section"]):
            has_grade = any(g in combined for g in ["e250", "e350", "e410", "fe 410", "grade"])
            if not has_grade:
                missing_items.append({
                    "field_name": "steel_strength_grade",
                    "why_it_matters": "Yield strength grade (e.g. E250 quality A/BR/B0) dictates chemical composition and Charpy impact requirements under IS 2062.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "Indicate required steel grade (e.g. E250 Quality A).",
                })

        # --- Check Cement ---
        elif "cement" in combined:
            has_grade = any(g in combined for g in ["33 grade", "43 grade", "53 grade", "53-grade", "opc 53"])
            if not has_grade:
                missing_items.append({
                    "field_name": "cement_strength_grade",
                    "why_it_matters": "Compressive strength designation (33, 43, or 53 Grade) determines whether IS 269, IS 8112, or IS 12269 applies.",
                    "impact": "BLOCKING",
                    "suggested_clarification": "Specify OPC grade (e.g. 53 Grade).",
                })

        return missing_items
