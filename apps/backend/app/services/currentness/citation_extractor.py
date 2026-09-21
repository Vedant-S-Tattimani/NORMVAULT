"""
Tender citation extraction and classification service.
Parses procurement text to extract explicit standard numbers, edition years, and amendments,
detecting ambiguous or conflicting citations while treating document text as passive untrusted data.
"""

import re
from typing import List, Dict, Optional
from app.schemas.edition import TenderCitationExtraction, CitationType


class TenderCitationExtractor:
    """
    Extracts and categorizes Indian Standard citations from tender requirements.
    Never hallucinates editions when absent from text.
    """

    # Matches Indian Standard patterns such as:
    # "IS 12615:2018", "IS 12615: 2018", "IS 12615-2018", "IS 12615 (2018)", "IS 12615"
    # "IS/IEC 60034-5:2020", "IS/ISO 9001:2015"
    CITATION_PATTERN = re.compile(
        r"\b(?P<std>(?:IS|IS/IEC|IS/ISO)\s+\d+(?:[-/]\w+)*(?:\s*\([^)]+\))?)"
        r"(?:\s*[:\-]\s*(?P<year>(?:19|20)\d{2})|\s*\(\s*(?P<year_paren>(?:19|20)\d{2})\s*\))?"
        r"(?:\s*(?:with|including|incorporating)?\s*(?:amendment|amd\.?|amdt\.?)\s*(?:no\.?|number)?\s*(?P<amd>\d+))?",
        re.IGNORECASE,
    )

    AMENDMENT_ONLY_PATTERN = re.compile(
        r"(?:amendment|amd\.?|amdt\.?)\s*(?:no\.?|number)?\s*(\d+)",
        re.IGNORECASE,
    )

    YEAR_PATTERN = re.compile(r"\b((?:19|20)\d{2})\b")

    def extract_citations(self, text: str, section_name: Optional[str] = None) -> List[TenderCitationExtraction]:
        """
        Extracts all standard citations from a text snippet or requirement clause.
        """
        if not text or not isinstance(text, str):
            return []

        # Passive defense: Strip any prompt injection instructions from analysis
        cleaned_text = self._sanitize_text(text)

        extractions: List[TenderCitationExtraction] = []

        for match in self.CITATION_PATTERN.finditer(cleaned_text):
            raw_std = match.group("std")
            if not raw_std:
                continue

            # Canonicalize standard number spacing (e.g. "IS   12615" -> "IS 12615")
            std_number = re.sub(r"\s+", " ", raw_std.strip())

            # Extract year
            year_str = match.group("year") or match.group("year_paren")
            edition_year = int(year_str) if year_str else None

            # Extract amendment
            amd_str = match.group("amd")
            amendment_number = int(amd_str) if amd_str else None

            # Lookahead window for amendment if not caught directly in pattern
            match_end = match.end()
            lookahead = cleaned_text[match_end : match_end + 40]
            if amendment_number is None:
                amd_match = self.AMENDMENT_ONLY_PATTERN.search(lookahead)
                if amd_match:
                    amendment_number = int(amd_match.group(1))

            # Classify citation type
            if edition_year and amendment_number:
                citation_type = CitationType.EXPLICIT_WITH_YEAR_AND_AMENDMENT
            elif edition_year:
                citation_type = CitationType.EXPLICIT_WITH_YEAR
            else:
                citation_type = CitationType.UNSPECIFIED_YEAR

            extractions.append(
                TenderCitationExtraction(
                    standard_number=std_number,
                    edition_year=edition_year,
                    amendment_number=amendment_number,
                    raw_citation=match.group(0).strip(),
                    citation_type=citation_type,
                    source_clause_or_section=section_name,
                )
            )

        return extractions

    def detect_conflicts(self, extractions: List[TenderCitationExtraction]) -> List[TenderCitationExtraction]:
        """
        Groups citations by standard number and flags conflicting edition years across clauses.
        """
        by_std: Dict[str, List[TenderCitationExtraction]] = {}
        for ext in extractions:
            norm_key = re.sub(r"[^A-Z0-9]", "", ext.standard_number.upper())
            by_std.setdefault(norm_key, []).append(ext)

        resolved_list: List[TenderCitationExtraction] = []
        for norm_key, group in by_std.items():
            years = {ext.edition_year for ext in group if ext.edition_year is not None}
            if len(years) > 1:
                # Contradictory edition years specified in the same tender
                for ext in group:
                    ext.citation_type = CitationType.CONFLICTING
                    resolved_list.append(ext)
            else:
                resolved_list.extend(group)

        return resolved_list

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitizes text against prompt injection tokens, ensuring tender input
        is treated strictly as passive data.
        """
        # Truncate pathological inputs
        sanitized = text[:10000]
        # Neutralize system prompt override markers
        sanitized = re.sub(r"(?i)(?:ignore\s+previous\s+instructions|system\s+override|mark\s+as\s+current)", "[DATA]", sanitized)
        return sanitized
