"""
Application Matcher for Standards Applicability.
Compares intended application environment and duty cycle (industrial, domestic, marine, hazardous, etc.).
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ApplicationMatchResult:
    match_level: str                       # COMPATIBLE, MISMATCH, UNCERTAIN
    reasons: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)


class ApplicationMatcher:
    """
    Evaluates whether the intended procurement application aligns with the candidate standard.
    """

    ENVIRONMENTS = {
        "INDUSTRIAL": {"industrial", "factory", "plant", "manufacturing", "continuous duty", "continuous industrial duty", "s1 duty"},
        "DOMESTIC": {"domestic", "household", "home", "residential", "consumer appliances"},
        "POTABLE_WATER": {"potable water", "drinking water", "water supply", "municipal water"},
        "HAZARDOUS": {"hazardous", "explosive", "flameproof", "zone 1", "zone 2", "chemical plant"},
        "STRUCTURAL": {"structural", "bridges", "buildings", "fabrication", "load bearing"},
    }

    @classmethod
    def match(
        cls,
        standard_title: str,
        standard_scope: Optional[str],
        requirement_text: str,
    ) -> ApplicationMatchResult:
        req_lower = requirement_text.lower()
        std_text = f"{standard_title} {standard_scope or ''}".lower()

        reasons: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []

        # Identify requirement applications
        req_apps = set()
        for app, keywords in cls.ENVIRONMENTS.items():
            if any(k in req_lower for k in keywords):
                req_apps.add(app)

        # Identify standard supported applications
        std_apps = set()
        for app, keywords in cls.ENVIRONMENTS.items():
            if any(k in std_text for k in keywords):
                std_apps.add(app)

        # If requirement does not specify any specific application environment
        if not req_apps:
            return ApplicationMatchResult(
                match_level="UNCERTAIN",
                reasons=[{
                    "title": "Application Environment Unstated",
                    "description": "Procurement requirement does not explicitly state operating environment or duty class.",
                    "is_positive": False,
                    "category": "APPLICATION",
                }],
            )

        # Check for direct conflicts (e.g. Industrial required, but standard is exclusively domestic)
        if "INDUSTRIAL" in req_apps and "DOMESTIC" in std_apps and "INDUSTRIAL" not in std_apps:
            conflicts.append({
                "conflict_type": "APPLICATION_MISMATCH",
                "description": "Requirement specifies continuous industrial application, whereas candidate standard covers domestic appliances.",
                "severity": "FATAL",
                "tender_claim": "Industrial duty",
                "standard_fact": "Domestic appliances specification",
            })
            reasons.append({
                "title": "Application Environment Conflict",
                "description": "Standard is designed for domestic/consumer applications, conflicting with industrial procurement duty.",
                "is_positive": False,
                "category": "APPLICATION",
            })
            return ApplicationMatchResult(match_level="MISMATCH", reasons=reasons, conflicts=conflicts)

        if "HAZARDOUS" in req_apps and "hazardous" not in std_text:
            conflicts.append({
                "conflict_type": "APPLICATION_MISMATCH",
                "description": "Requirement specifies hazardous or explosive atmosphere, not addressed by general standard.",
                "severity": "FATAL",
                "tender_claim": "Hazardous location duty",
                "standard_fact": "General environment standard",
            })
            return ApplicationMatchResult(match_level="MISMATCH", reasons=reasons, conflicts=conflicts)

        # Positive compatibility
        shared_apps = req_apps & std_apps
        if shared_apps:
            reasons.append({
                "title": "Application Compatibility Confirmed",
                "description": f"Standard explicitly supports intended operating conditions ({', '.join(shared_apps)}).",
                "is_positive": True,
                "category": "APPLICATION",
            })
            return ApplicationMatchResult(match_level="COMPATIBLE", reasons=reasons, conflicts=conflicts)

        # Default compatibility when standard is general purpose and does not exclude the application
        reasons.append({
            "title": "General Operating Compatibility",
            "description": "Candidate standard is compatible with requirement operating profile without explicit restrictions.",
            "is_positive": True,
            "category": "APPLICATION",
        })
        return ApplicationMatchResult(match_level="COMPATIBLE", reasons=reasons, conflicts=conflicts)
