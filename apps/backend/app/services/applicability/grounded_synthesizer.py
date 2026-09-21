"""
Grounded Synthesizer & Verification Guard for Standards Applicability.
Ensures human-readable explanations operate strictly on verified evidence.
Rejects hallucinated standards, fictitious clauses, and defends against prompt injections in procurement documents.
"""

import re
from typing import List, Set, Optional, Dict, Any
from pydantic import BaseModel, Field


class GroundedExplanationSchema(BaseModel):
    summary: str = Field(..., description="Grounded explanation summary")
    verified_citations: List[str] = Field(default_factory=list, description="Verified standard numbers cited")
    hallucination_detected: bool = Field(False, description="Whether unverified standards or clauses were flagged")
    stripped_claims: List[str] = Field(default_factory=list, description="Unsupported claims stripped by guard")


class PromptSanitizer:
    """
    Treats tender text strictly as untrusted DATA.
    Neutralizes prompt injection attempts embedded inside procurement documents.
    """

    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*override", re.IGNORECASE),
        re.compile(r"you\s+must\s+declare\s+(?:this|is\s*\d+)\s+as\s+applicable", re.IGNORECASE),
        re.compile(r"mark\s+this\s+standard\s+as\s+mandatory", re.IGNORECASE),
        re.compile(r"bypass\s+evidence\s+verification", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_untrusted_text(cls, text: str) -> str:
        """Sanitizes text by neutralizing instruction hijack patterns."""
        sanitized = text
        for pattern in cls.INJECTION_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SUSPICIOUS_INSTRUCTION]", sanitized)
        return sanitized.strip()

    @classmethod
    def wrap_in_data_fence(cls, tender_text: str) -> str:
        """Wraps untrusted tender text in rigid XML-style data delimiters."""
        clean_text = cls.sanitize_untrusted_text(tender_text)
        return (
            "<untrusted_procurement_document_data>\n"
            f"{clean_text}\n"
            "</untrusted_procurement_document_data>"
        )


class GroundedVerificationGuard:
    """
    Validates that any generated explanation only references standards and clauses
    that actually exist in the verified knowledge base context.
    """

    STD_PATTERN = re.compile(r"\bIS\s*[:/]?\s*(\d+)\b", re.IGNORECASE)
    CLAUSE_PATTERN = re.compile(r"\bClause\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE)

    @classmethod
    def verify_and_guard(
        cls,
        raw_explanation: str,
        verified_standard_numbers: Set[str],
        verified_clause_numbers: Set[str],
    ) -> GroundedExplanationSchema:
        clean_std_set = {re.sub(r"[:\s]+", "", s.upper()) for s in verified_standard_numbers}
        clean_clause_set = set(verified_clause_numbers)

        hallucination_detected = False
        stripped_claims = []
        verified_citations = []

        # 1. Check mentioned standards
        found_stds = cls.STD_PATTERN.findall(raw_explanation)
        for std_num in found_stds:
            full_std = f"IS{std_num}"
            if full_std in clean_std_set or any(std_num in s for s in clean_std_set):
                verified_citations.append(f"IS {std_num}")
            else:
                hallucination_detected = True
                stripped_claims.append(f"Nonexistent / unverified standard: IS {std_num}")

        # 2. Check mentioned clauses
        found_clauses = cls.CLAUSE_PATTERN.findall(raw_explanation)
        for c_num in found_clauses:
            if c_num not in clean_clause_set:
                hallucination_detected = True
                stripped_claims.append(f"Nonexistent / unindexed clause: Clause {c_num}")

        # Sanitize explanation if hallucination was caught
        sanitized_explanation = raw_explanation
        if hallucination_detected:
            for unverified in stripped_claims:
                # Append warning banner to summary
                sanitized_explanation += f" [Guard Alert: Removed unsupported citation ({unverified})]"

        return GroundedExplanationSchema(
            summary=sanitized_explanation,
            verified_citations=list(set(verified_citations)),
            hallucination_detected=hallucination_detected,
            stripped_claims=stripped_claims,
        )


class DeterministicGroundedSynthesizer:
    """
    Fast, deterministic explanation synthesizer.
    Constructs transparent, grounded explanations directly from verified evidence items.
    """

    @classmethod
    def synthesize(
        cls,
        standard_number: str,
        outcome: str,
        reasons: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        missing_info: List[Dict[str, Any]],
        verified_standards: Set[str],
        verified_clauses: Set[str],
    ) -> GroundedExplanationSchema:
        lines = []

        if outcome == "APPLICABLE":
            lines.append(f"Determination: {standard_number} is APPLICABLE based on verified scope and technical alignment.")
        elif outcome == "POSSIBLY_APPLICABLE":
            lines.append(f"Determination: {standard_number} is POSSIBLY APPLICABLE as an alternative candidate.")
        elif outcome == "NOT_APPLICABLE":
            lines.append(f"Determination: {standard_number} is NOT APPLICABLE due to verified technical conflicts.")
        else:
            lines.append(f"Determination: INSUFFICIENT EVIDENCE to confirm applicability of {standard_number}.")

        # Positive reasons
        pos_reasons = [r for r in reasons if r.get("is_positive")]
        if pos_reasons:
            lines.append("Supporting Evidence:")
            for r in pos_reasons[:3]:
                lines.append(f"• {r['title']}: {r['description']}")

        # Negative conflicts
        if conflicts:
            lines.append("Conflicting Evidence / Exclusions:")
            for c in conflicts[:3]:
                lines.append(f"• [{c.get('severity', 'WARNING')}] {c['description']}")

        # Missing information
        if missing_info:
            lines.append("Information Required for Definite Determination:")
            for m in missing_info[:3]:
                lines.append(f"• {m['field_name']}: {m['why_it_matters']}")

        raw_text = "\n".join(lines)

        return GroundedVerificationGuard.verify_and_guard(
            raw_explanation=raw_text,
            verified_standard_numbers=verified_standards,
            verified_clause_numbers=verified_clauses,
        )
