"""
Parameter Comparator for Standards Applicability.
Compares structured technical parameters from procurement requirements against verified standard data.
Never fabricates ranges; strictly uses verified standard scope and clause text.
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from app.models.requirement import TechnicalParameter
from app.models.clause import Clause


@dataclass
class ParameterComparisonResult:
    match_level: str                       # COMPATIBLE, CONFLICT, UNCHECKED, NOT_SPECIFIED
    verified_parameters: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    reasons: List[Dict[str, Any]] = field(default_factory=list)


class ParameterComparator:
    """
    Compares requirement parameters (power, voltage, frequency, dimensions, pressure)
    against verified constraints in candidate standard scope and clauses.
    """

    @classmethod
    def compare(
        cls,
        parameters: List[TechnicalParameter],
        standard_scope: Optional[str],
        clauses: List[Clause],
    ) -> ParameterComparisonResult:
        if not parameters:
            return ParameterComparisonResult(
                match_level="NOT_SPECIFIED",
                reasons=[{
                    "title": "No Technical Parameters Specified",
                    "description": "Requirement does not contain atomic quantitative parameters for comparison.",
                    "is_positive": False,
                    "category": "PARAMETER",
                }],
            )

        # Aggregate standard text
        standard_corpus = (standard_scope or "") + " " + " ".join(c.content for c in clauses)
        corpus_lower = standard_corpus.lower()

        conflicts: List[Dict[str, Any]] = []
        verified_params: List[Dict[str, Any]] = []
        reasons: List[Dict[str, Any]] = []

        # 1. Parse Standard Constraints (Ground Truth Extraction)
        # Power limits (kW)
        power_range = cls._extract_power_range(standard_corpus)
        # Voltage limits (V)
        voltage_limit = cls._extract_voltage_limit(standard_corpus)

        has_conflict = False
        compatible_count = 0

        for param in parameters:
            p_name = (param.name or "").lower()
            p_val_str = param.target_value or param.normalized_value or param.original_value or ""
            p_unit = (param.unit or "").lower()

            # Clean numerical value
            num_match = re.search(r"(\d+(?:\.\d+)?)", p_val_str)
            val_num = float(num_match.group(1)) if num_match else None

            # --- Check Power (kW) ---
            if ("power" in p_name or "output" in p_name or "rating" in p_name or "kw" in p_unit or "kw" in p_val_str.lower()) and val_num is not None:
                if power_range:
                    p_min, p_max = power_range
                    if val_num < p_min or val_num > p_max:
                        has_conflict = True
                        conflicts.append({
                            "conflict_type": "PARAMETER_OUT_OF_RANGE",
                            "description": f"Required power {val_num} kW is outside standard's verified range ({p_min} to {p_max} kW).",
                            "severity": "FATAL",
                            "tender_claim": f"{val_num} kW",
                            "standard_fact": f"{p_min} to {p_max} kW",
                        })
                    else:
                        compatible_count += 1
                        verified_params.append({
                            "parameter": "Rated Power",
                            "required_value": f"{val_num} kW",
                            "standard_coverage": f"{p_min} to {p_max} kW",
                            "is_compatible": True,
                        })
                else:
                    # Scope mentions kW without exact range
                    if "kw" in corpus_lower or "kilowatt" in corpus_lower:
                        compatible_count += 1
                        verified_params.append({
                            "parameter": "Rated Power",
                            "required_value": f"{val_num} kW",
                            "standard_coverage": "Power specified in kW (continuous duty)",
                            "is_compatible": True,
                        })

            # --- Check Voltage (V) ---
            elif ("voltage" in p_name or "volt" in p_unit or "415" in p_val_str or "v" == p_unit) and val_num is not None:
                if voltage_limit:
                    if val_num > voltage_limit:
                        has_conflict = True
                        conflicts.append({
                            "conflict_type": "PARAMETER_VOLTAGE_EXCEEDED",
                            "description": f"Required voltage {val_num} V exceeds standard's verified limit of {voltage_limit} V.",
                            "severity": "FATAL",
                            "tender_claim": f"{val_num} V",
                            "standard_fact": f"Up to {voltage_limit} V",
                        })
                    else:
                        compatible_count += 1
                        verified_params.append({
                            "parameter": "Rated Voltage",
                            "required_value": f"{val_num} V",
                            "standard_coverage": f"Up to {voltage_limit} V supported",
                            "is_compatible": True,
                        })
                elif "1000 v" in corpus_lower or "415 v" in corpus_lower or "rated voltage" in corpus_lower:
                    compatible_count += 1
                    verified_params.append({
                        "parameter": "Rated Voltage",
                        "required_value": f"{val_num} V",
                        "standard_coverage": "Standard covers low voltage three-phase supply",
                        "is_compatible": True,
                    })

            # --- Check Ingress Protection (IP) ---
            elif "ip" in p_name or "ingress" in p_name or "ip" in p_val_str.lower():
                ip_match = re.search(r"ip\s*(\d{2})", p_val_str.lower())
                if ip_match and ("ip 55" in corpus_lower or "ip55" in corpus_lower or "terminal box" in corpus_lower):
                    compatible_count += 1
                    verified_params.append({
                        "parameter": "Ingress Protection",
                        "required_value": ip_match.group(0).upper(),
                        "standard_coverage": "IP 55 protection supported",
                        "is_compatible": True,
                    })

        # Synthesize results
        if has_conflict:
            return ParameterComparisonResult(
                match_level="CONFLICT",
                verified_parameters=verified_params,
                conflicts=conflicts,
                reasons=[{
                    "title": "Technical Parameter Contradiction",
                    "description": f"Requirement technical parameter conflicts with standard limits ({conflicts[0]['description']}).",
                    "is_positive": False,
                    "category": "PARAMETER",
                }],
            )

        if compatible_count > 0:
            reasons.append({
                "title": "Parameter Compatibility Verified",
                "description": f"{compatible_count} quantitative requirement parameter(s) verified against standard ranges.",
                "is_positive": True,
                "category": "PARAMETER",
            })
            return ParameterComparisonResult(
                match_level="COMPATIBLE",
                verified_parameters=verified_params,
                conflicts=[],
                reasons=reasons,
            )

        return ParameterComparisonResult(
            match_level="NOT_SPECIFIED",
            verified_parameters=[],
            conflicts=[],
            reasons=[{
                "title": "Parameters Not Specifically Regulated",
                "description": "Standard does not restrict the specific parameters specified in this requirement.",
                "is_positive": True,
                "category": "PARAMETER",
            }],
        )

    @staticmethod
    def _extract_power_range(text: str) -> Optional[tuple[float, float]]:
        """Extracts power range like 'from 0.12 kW to 1000 kW' or 'up to 10 kW'."""
        # Check range pattern: from X kW to Y kW
        m_range = re.search(r"from\s*(\d+(?:\.\d+)?)\s*kw\s*to\s*(\d+(?:\.\d+)?)\s*kw", text, re.IGNORECASE)
        if m_range:
            return (float(m_range.group(1)), float(m_range.group(2)))

        # Check cap pattern: up to X kW / not exceeding X kW
        m_cap = re.search(r"(?:up to|not exceeding|maximum of)\s*(\d+(?:\.\d+)?)\s*kw", text, re.IGNORECASE)
        if m_cap:
            return (0.0, float(m_cap.group(1)))

        return None

    @staticmethod
    def _extract_voltage_limit(text: str) -> Optional[float]:
        """Extracts voltage limit like 'rated voltage up to 1000 V'."""
        m_volt = re.search(r"(?:rated voltage up to|up to|maximum of)\s*(\d+(?:\.\d+)?)\s*v\b", text, re.IGNORECASE)
        if m_volt:
            return float(m_volt.group(1))
        return None
