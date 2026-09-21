"""
Product Matcher for Standards Applicability.
Compares procurement requirement product identity against standard title and product domain.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ProductMatchResult:
    match_level: str                       # EXACT, CATEGORY, AMBIGUOUS, MISMATCH
    reasons: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)


class ProductMatcher:
    """
    Evaluates product compatibility between procurement requirement and candidate standard.
    """

    # Domain vocabulary clusters for standard BIS divisions
    DOMAIN_CLUSTERS = {
        "MOTORS": {"motor", "motors", "induction", "a.c.", "rotor", "stator", "winding", "squirrel", "cage"},
        "PIPES": {"pipe", "pipes", "piping", "polyethylene", "hdpe", "pe", "conveyance", "potable"},
        "STEEL": {"steel", "plates", "beams", "sections", "bars", "tensile", "structural", "hot", "rolled"},
        "CEMENT": {"cement", "portland", "concrete", "clinker", "compressive", "setting", "curing"},
    }

    @classmethod
    def match(
        cls,
        standard_title: str,
        standard_scope: Optional[str],
        requirement_text: str,
        target_product_name: Optional[str] = None,
    ) -> ProductMatchResult:
        combined_tender = f"{target_product_name or ''} {requirement_text}".lower()
        std_text = f"{standard_title} {standard_scope or ''}".lower()

        tender_tokens = set(re.findall(r"\b[a-z]{3,}\b", combined_tender))
        std_tokens = set(re.findall(r"\b[a-z]{3,}\b", std_text))

        # Detect tender domain cluster
        tender_domains = set()
        for domain, kw_set in cls.DOMAIN_CLUSTERS.items():
            if len(tender_tokens & kw_set) >= 2 or (target_product_name and any(k in target_product_name.lower() for k in kw_set)):
                tender_domains.add(domain)

        # Detect standard domain cluster
        std_domains = set()
        for domain, kw_set in cls.DOMAIN_CLUSTERS.items():
            if len(std_tokens & kw_set) >= 2 or any(k in standard_title.lower() for k in kw_set):
                std_domains.add(domain)

        reasons: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []

        # Case 1: Cross-domain conflict
        if tender_domains and std_domains and not (tender_domains & std_domains):
            conflicts.append({
                "conflict_type": "PRODUCT_CATEGORY_MISMATCH",
                "description": f"Requirement targets product domain {list(tender_domains)}, but candidate standard covers {list(std_domains)}.",
                "severity": "FATAL",
                "tender_claim": target_product_name or requirement_text[:100],
                "standard_fact": standard_title,
            })
            reasons.append({
                "title": "Product Domain Mismatch",
                "description": f"Candidate standard belongs to a different technical domain ({', '.join(std_domains)}).",
                "is_positive": False,
                "category": "PRODUCT",
            })
            return ProductMatchResult(match_level="MISMATCH", reasons=reasons, conflicts=conflicts)

        # Case 2: Exact product name alignment
        # Check specific multi-word phrases
        exact_phrases = [
            ("induction motor", "a.c. motors"),
            ("induction motor", "induction motors"),
            ("hdpe pipe", "polyethylene pipes"),
            ("polyethylene pipe", "polyethylene pipes"),
            ("structural steel", "structural steel"),
            ("portland cement", "portland cement"),
        ]

        is_exact = False
        for tender_p, std_p in exact_phrases:
            if tender_p in combined_tender and (std_p in standard_title.lower() or (standard_scope and std_p in standard_scope.lower())):
                is_exact = True
                break

        generic_single_words = {"motor", "motors", "pipe", "pipes", "steel", "cement", "pump", "cable"}
        is_generic_word = bool(target_product_name and target_product_name.lower().strip() in generic_single_words)

        if is_exact or (target_product_name and not is_generic_word and target_product_name.lower() in standard_title.lower()):
            reasons.append({
                "title": "Exact Product Identification",
                "description": f"Standard title and scope directly match target product: '{standard_title}'",
                "is_positive": True,
                "category": "PRODUCT",
            })
            return ProductMatchResult(match_level="EXACT", reasons=reasons, conflicts=conflicts)

        # Case 3: Category match
        shared_tokens = tender_tokens & std_tokens
        meaningful_shared = {t for t in shared_tokens if t in {"motor", "motors", "pipe", "pipes", "steel", "cement", "pump", "cable"}}
        if meaningful_shared:
            reasons.append({
                "title": "Related Product Category",
                "description": f"Standard aligns with requirement on product category ({', '.join(meaningful_shared)}).",
                "is_positive": True,
                "category": "PRODUCT",
            })
            return ProductMatchResult(match_level="CATEGORY", reasons=reasons, conflicts=conflicts)

        # Case 4: Ambiguous
        reasons.append({
            "title": "Uncertain Product Identity",
            "description": "Requirement text does not specify a distinct target product matching this standard.",
            "is_positive": False,
            "category": "PRODUCT",
        })
        return ProductMatchResult(match_level="AMBIGUOUS", reasons=reasons, conflicts=conflicts)
