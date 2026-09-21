"""
Grounded Verification Guard and Prompt Injection Defense (Phase 8).
Validates that all citations exist in the database and protects against prompt injection.
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session

from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause
from app.models.requirement import Requirement
from app.models.gap import SpecificationGap
from app.models.certification import CertificationRequirement


# Adversarial prompt injection tokens and patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt",
    r"you\s+are\s+now",
    r"override\s+(gap|readiness|applicability|severity)",
    r"mark\s+(as\s+)?(fully\s+)?compliant",
    r"disregard\s+(standards|gaps|qco|conflicts)",
    r"bypass\s+(verification|guard|audit)",
    r"drop\s+table",
    r"<script",
    r"javascript:",
    r"\{\{.*\}\}",  # template injection
]


class GroundedVerificationGuard:
    """
    Guarantees zero hallucination by verifying all citations against indexed database records.
    Provides prompt injection sanitization for untrusted procurement text.
    """

    @staticmethod
    def sanitize_untrusted_text(text: Optional[str]) -> Tuple[str, bool]:
        """
        Scans and sanitizes untrusted tender text for adversarial prompt injection tokens.
        Returns: (sanitized_text, has_injection_attempt)
        """
        if not text:
            return "", False

        has_injection = False
        sanitized = text

        for pattern in PROMPT_INJECTION_PATTERNS:
            matches = list(re.finditer(pattern, sanitized, re.IGNORECASE))
            if matches:
                has_injection = True
                for m in reversed(matches):
                    # Neutralize by replacing matched span with [DEFENSE: REMOVED ADVERSARIAL TOKEN]
                    sanitized = (
                        sanitized[: m.start()]
                        + f"[DEFENSE: NEUTRALIZED SUSPICIOUS DIRECTIVE: '{m.group(0)}']"
                        + sanitized[m.end() :]
                    )

        return sanitized, has_injection

    @classmethod
    def verify_grounding(
        cls,
        db: Session,
        standard_codes: List[str],
        standard_ids: Optional[List[int]] = None,
        edition_ids: Optional[List[int]] = None,
        clause_ids: Optional[List[int]] = None,
        requirement_ids: Optional[List[int]] = None,
        gap_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Cross-verifies all entity IDs and standard codes against the database.
        Returns verification report with valid and invalid entities.
        """
        results = {
            "all_grounded": True,
            "valid_standards": [],
            "unsupported_standards": [],
            "valid_editions": [],
            "unsupported_editions": [],
            "valid_clauses": [],
            "unsupported_clauses": [],
            "valid_requirements": [],
            "unsupported_requirements": [],
            "valid_gaps": [],
            "unsupported_gaps": [],
        }

        # 1. Verify Standard Codes
        if standard_codes:
            existing_stds = (
                db.query(IndianStandard.standard_number)
                .filter(IndianStandard.standard_number.in_(standard_codes))
                .all()
            )
            existing_set = {s[0] for s in existing_stds}
            for code in standard_codes:
                if code in existing_set:
                    results["valid_standards"].append(code)
                else:
                    results["unsupported_standards"].append(code)
                    results["all_grounded"] = False

        # 2. Verify Standard IDs
        if standard_ids:
            existing_std_ids = (
                db.query(IndianStandard.id)
                .filter(IndianStandard.id.in_(standard_ids))
                .all()
            )
            existing_id_set = {s[0] for s in existing_std_ids}
            for sid in standard_ids:
                if sid in existing_id_set:
                    results["valid_standards"].append(sid)
                else:
                    results["unsupported_standards"].append(sid)
                    results["all_grounded"] = False

        # 3. Verify Edition IDs
        if edition_ids:
            existing_ed_ids = (
                db.query(StandardEdition.id)
                .filter(StandardEdition.id.in_(edition_ids))
                .all()
            )
            existing_ed_set = {e[0] for e in existing_ed_ids}
            for eid in edition_ids:
                if eid in existing_ed_set:
                    results["valid_editions"].append(eid)
                else:
                    results["unsupported_editions"].append(eid)
                    results["all_grounded"] = False

        # 4. Verify Clause IDs
        if clause_ids:
            existing_cl_ids = (
                db.query(Clause.id)
                .filter(Clause.id.in_(clause_ids))
                .all()
            )
            existing_cl_set = {c[0] for c in existing_cl_ids}
            for cid in clause_ids:
                if cid in existing_cl_set:
                    results["valid_clauses"].append(cid)
                else:
                    results["unsupported_clauses"].append(cid)
                    results["all_grounded"] = False

        # 5. Verify Requirement IDs
        if requirement_ids:
            existing_req_ids = (
                db.query(Requirement.id)
                .filter(Requirement.id.in_(requirement_ids))
                .all()
            )
            existing_req_set = {r[0] for r in existing_req_ids}
            for rid in requirement_ids:
                if rid in existing_req_set:
                    results["valid_requirements"].append(rid)
                else:
                    results["unsupported_requirements"].append(rid)
                    results["all_grounded"] = False

        # 6. Verify Gap IDs
        if gap_ids:
            existing_gap_ids = (
                db.query(SpecificationGap.id)
                .filter(SpecificationGap.id.in_(gap_ids))
                .all()
            )
            existing_gap_set = {g[0] for g in existing_gap_ids}
            for gid in gap_ids:
                if gid in existing_gap_set:
                    results["valid_gaps"].append(gid)
                else:
                    results["unsupported_gaps"].append(gid)
                    results["all_grounded"] = False

        return results
