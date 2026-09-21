"""
Deterministic query construction layer for the Hybrid Standards Retrieval Engine.
Transforms structured procurement requirements, technical parameters, and product metadata
into normalized retrieval queries without arbitrary prompt hallucinations.
"""

from dataclasses import dataclass, field
import re
from typing import List, Optional
from app.models.requirement import Requirement, TechnicalParameter


# Regular expression to extract explicit Indian Standard citations (e.g., 'IS 4984', 'IS:12615', 'IS 2062:2011')
IS_CITATION_PATTERN = re.compile(r"\bIS\s*[:\-]?\s*(\d{2,6})(?:\s*:\s*\d{4})?\b", re.IGNORECASE)


@dataclass
class ConstructedQuery:
    """Structured representation of a constructed retrieval query."""
    search_text: str
    target_product: Optional[str] = None
    extracted_terms: List[str] = field(default_factory=list)
    explicit_standard_numbers: List[str] = field(default_factory=list)
    parameters_summary: List[str] = field(default_factory=list)


class DeterministicQueryBuilder:
    """
    Constructs deterministic, structured retrieval queries from Requirement models.
    """

    @staticmethod
    def extract_explicit_citations(text: str) -> List[str]:
        """Extract any explicitly mentioned Indian Standard numbers from text."""
        matches = IS_CITATION_PATTERN.findall(text)
        # Format as canonical 'IS XXXX'
        return [f"IS {m}" for m in matches]

    @classmethod
    def build_query(
        cls,
        requirement: Requirement,
        target_product_name: Optional[str] = None,
    ) -> ConstructedQuery:
        """
        Build a deterministic query string and metadata from a requirement and its parameters.
        """
        parts: List[str] = []
        parameters_summary: List[str] = []
        all_text_for_citations = requirement.extracted_text or ""

        # 1. Product Identity context
        product_clean = ""
        if target_product_name and target_product_name.strip():
            product_clean = target_product_name.strip()
            parts.append(product_clean)

        # 2. Requirement Text
        req_text = (requirement.extracted_text or "").strip()
        if req_text:
            parts.append(req_text)

        # 3. Structured Technical Parameters
        if requirement.parameters:
            param_tokens = []
            for p in requirement.parameters:
                p_repr_parts = []
                if p.name:
                    p_repr_parts.append(p.name)
                val = p.normalized_value or p.target_value or p.original_value
                if val:
                    p_repr_parts.append(val)
                if p.unit:
                    p_repr_parts.append(p.unit)
                
                param_str = " ".join(p_repr_parts)
                if param_str:
                    param_tokens.append(param_str)
                    parameters_summary.append(param_str)

                # Check if parameter has an explicitly cited test method standard
                if p.test_method_standard:
                    parts.append(p.test_method_standard)
                    all_text_for_citations += " " + p.test_method_standard

            if param_tokens:
                parts.append(" ".join(param_tokens))

        # 4. Explicit IS citations
        citations = cls.extract_explicit_citations(all_text_for_citations)

        # Deduplicate and clean query string
        full_query_text = " ".join(parts).strip()
        # Collapse multiple spaces
        clean_search_text = re.sub(r"\s+", " ", full_query_text)

        return ConstructedQuery(
            search_text=clean_search_text,
            target_product=product_clean or None,
            extracted_terms=list(set(clean_search_text.lower().split())),
            explicit_standard_numbers=citations,
            parameters_summary=parameters_summary,
        )
