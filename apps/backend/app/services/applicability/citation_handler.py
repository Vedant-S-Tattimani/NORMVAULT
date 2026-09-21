"""
Citation Handler for Standards Applicability.
Detects and validates explicit standard references cited in tender documents.
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class CitationAnalysisResult:
    has_explicit_citation: bool
    cited_standard_number: Optional[str] = None
    citation_snippet: Optional[str] = None
    reason: Optional[dict] = None


class CitationHandler:
    """
    Evaluates whether a candidate standard was explicitly cited in the procurement document.
    Explicit references provide strong positive evidence, but are evaluated independently
    and cannot override hard negative conflicts (e.g. parameter violations).
    """

    CITATION_PATTERN = re.compile(
        r"(?:conform(?:ing)?\s+to|as\s+per|in\s+accordance\s+with|compliant\s+with|to\s+comply\s+with)\s+(IS\s*[:/]?\s*\d+(?:\s*(?:Part|Sec|Section)\s*\d+)?(?::\s*\d{4})?)",
        re.IGNORECASE,
    )

    @classmethod
    def check_citation(cls, requirement_text: str, standard_number: str) -> CitationAnalysisResult:
        std_num_clean = re.sub(r"[:\s]+", " ", standard_number.upper()).strip()
        req_upper = requirement_text.upper()

        # Check explicit citation pattern
        matches = cls.CITATION_PATTERN.finditer(requirement_text)
        for m in matches:
            cited_raw = m.group(1)
            cited_clean = re.sub(r"[:\s]+", " ", cited_raw.upper()).strip()
            if std_num_clean in cited_clean or cited_clean in std_num_clean:
                full_snippet = m.group(0)
                return CitationAnalysisResult(
                    has_explicit_citation=True,
                    cited_standard_number=standard_number,
                    citation_snippet=full_snippet,
                    reason={
                        "title": "Explicit Procurement Reference",
                        "description": f"Procurement specification explicitly stipulates compliance: '{full_snippet}'. Scope alignment independently confirmed.",
                        "is_positive": True,
                        "category": "CITATION",
                    },
                )

        # Fallback: check direct occurrence of standard number in text
        if std_num_clean in re.sub(r"[:\s]+", " ", req_upper):
            # Extract surrounding context
            idx = req_upper.find(std_num_clean.replace(" ", ""))
            if idx == -1:
                idx = req_upper.find(std_num_clean)
            start = max(0, idx - 40)
            end = min(len(requirement_text), idx + len(std_num_clean) + 40)
            snippet = requirement_text[start:end].strip()

            return CitationAnalysisResult(
                has_explicit_citation=True,
                cited_standard_number=standard_number,
                citation_snippet=snippet,
                reason={
                    "title": "Standard Reference Cited",
                    "description": f"Standard number '{standard_number}' is directly cited in requirement text: '...{snippet}...'.",
                    "is_positive": True,
                    "category": "CITATION",
                },
            )

        return CitationAnalysisResult(has_explicit_citation=False)
