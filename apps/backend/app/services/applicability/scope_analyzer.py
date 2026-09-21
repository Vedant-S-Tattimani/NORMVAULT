"""
Scope Analyzer for Standards Applicability.
Evaluates positive scope coverage and detects explicit negative scope exclusions.
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ScopeAnalysisResult:
    match_level: str                       # EXACT, PARTIAL, MISMATCH, UNCERTAIN
    has_exclusion: bool = False
    exclusion_snippet: Optional[str] = None
    has_specific_feature: bool = False
    specific_feature_name: Optional[str] = None
    positive_snippets: List[str] = field(default_factory=list)
    reasons: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)


class ScopeAnalyzer:
    """
    Analyzes standard scope against tender requirement text and target product.
    Identifies positive evidence and explicit exclusions/limitations.
    """

    # Patterns indicating negative scope exclusions or limitations
    EXCLUSION_PATTERNS = [
        re.compile(r"(?:excludes?|excluding|does not cover|not applicable to)\s+([^.;]+)", re.IGNORECASE),
        re.compile(r"(?:intended exclusively for|intended solely for|only for|exclusively for)\s+([^.;]+)", re.IGNORECASE),
        re.compile(r"(?:not intended for|not for)\s+([^.;]+)", re.IGNORECASE),
        re.compile(r"(?:specifically excludes?)\s+([^.;]+)", re.IGNORECASE),
    ]

    @classmethod
    def analyze(
        cls,
        scope_text: Optional[str],
        requirement_text: str,
        target_product_name: Optional[str] = None,
    ) -> ScopeAnalysisResult:
        if not scope_text or not scope_text.strip():
            return ScopeAnalysisResult(
                match_level="UNCERTAIN",
                reasons=[{
                    "title": "Scope Text Unavailable",
                    "description": "The candidate standard has no indexed scope text in the knowledge base.",
                    "is_positive": False,
                    "category": "SCOPE",
                }],
            )

        clean_scope = scope_text.strip()
        scope_lower = clean_scope.lower()
        req_lower = requirement_text.lower()
        prod_lower = (target_product_name or "").lower()

        conflicts: List[Dict[str, Any]] = []
        positive_snippets: List[str] = []
        reasons: List[Dict[str, Any]] = []
        has_exclusion = False
        exclusion_snippet = None

        # 1. Check for negative scope exclusions
        for pattern in cls.EXCLUSION_PATTERNS:
            matches = pattern.finditer(clean_scope)
            for m in matches:
                excluded_phrase = m.group(1).lower().strip()
                full_snippet = m.group(0).strip()
                
                # Check if requirement matches the excluded concept
                # E.g. tender mentions "hazardous" or "explosive", and scope says "excludes hazardous location motors"
                # Or tender mentions "industrial", and scope says "intended exclusively for domestic appliances"
                excluded_tokens = [w for w in re.findall(r"\b[a-z]{3,}\b", excluded_phrase) if w not in {"the", "and", "for", "with"}]
                req_tokens = set(re.findall(r"\b[a-z]{3,}\b", req_lower))

                # Check if exclusion directly conflicts with requirement
                is_direct_conflict = False
                if any(tok in req_tokens for tok in excluded_tokens if tok in {"domestic", "hazardous", "traction", "submerged", "marine", "automotive", "high-pressure", "steam"}):
                    is_direct_conflict = True
                
                # Check "exclusively for X" when requirement is Y
                if "exclusively for domestic" in full_snippet.lower() and ("industrial" in req_lower or "industrial" in prod_lower):
                    is_direct_conflict = True
                elif "exclusively for industrial" in full_snippet.lower() and ("domestic" in req_lower or "household" in req_lower):
                    is_direct_conflict = True

                if is_direct_conflict:
                    has_exclusion = True
                    exclusion_snippet = full_snippet
                    conflicts.append({
                        "conflict_type": "SCOPE_EXCLUSION",
                        "description": f"Standard scope explicitly excludes or restricts: '{full_snippet}'",
                        "severity": "FATAL",
                        "tender_claim": requirement_text[:120],
                        "standard_fact": full_snippet,
                    })

        if has_exclusion:
            return ScopeAnalysisResult(
                match_level="MISMATCH",
                has_exclusion=True,
                exclusion_snippet=exclusion_snippet,
                conflicts=conflicts,
                reasons=[{
                    "title": "Scope Exclusion Detected",
                    "description": f"Standard scope conflicts with procurement requirement: {exclusion_snippet}",
                    "is_positive": False,
                    "category": "SCOPE",
                }],
            )

        # 2. Evaluate positive scope coverage
        # Extract product keywords
        query_text = f"{target_product_name or ''} {requirement_text}".lower()
        key_tokens = set(re.findall(r"\b[a-z]{3,}\b", query_text))
        stopwords = {"the", "and", "for", "with", "this", "shall", "standard", "specification", "requirements", "covers"}
        content_tokens = key_tokens - stopwords

        matched_tokens = [tok for tok in content_tokens if tok in scope_lower]
        match_ratio = len(matched_tokens) / max(1, len(content_tokens))

        # Check key concept phrases
        phrases_to_check = [
            "induction motor", "polyethylene pipes", "structural steel", "portland cement",
            "three-phase", "squirrel cage", "energy efficient", "water supply", "potable water",
        ]
        matched_phrases = [p for p in phrases_to_check if p in query_text and p in scope_lower]

        # Specific sub-series / grade / efficiency features:
        specific_features = [
            "ie3", "ie4", "ie2", "ie1", "energy efficient", "pe 100", "pe 80", "e250", "53 grade", "43 grade", "33 grade"
        ]
        matched_specific = [f for f in specific_features if f in query_text and f in scope_lower]
        has_specific_feature = len(matched_specific) > 0
        specific_feature_name = ", ".join(matched_specific).upper() if matched_specific else None

        if has_specific_feature:
            reasons.append({
                "title": f"Specific Feature Alignment ({specific_feature_name})",
                "description": f"Standard scope specifically governs {specific_feature_name} required by procurement tender.",
                "is_positive": True,
                "category": "SCOPE",
            })

        if matched_phrases or match_ratio >= 0.35:
            match_level = "EXACT" if (matched_phrases and match_ratio >= 0.25) else "PARTIAL"
            snippet = clean_scope[:240] + ("..." if len(clean_scope) > 240 else "")
            positive_snippets.append(snippet)
            reasons.append({
                "title": "Product Scope Alignment",
                "description": f"Verified scope directly covers requirement domain: '{snippet}'",
                "is_positive": True,
                "category": "SCOPE",
            })
        elif match_ratio >= 0.15:
            match_level = "PARTIAL"
            reasons.append({
                "title": "Partial Scope Overlap",
                "description": f"Scope overlaps on domain terms ({', '.join(matched_tokens[:4])}) but lacks definitive product category confirmation.",
                "is_positive": True,
                "category": "SCOPE",
            })
        else:
            match_level = "MISMATCH"
            conflicts.append({
                "conflict_type": "SCOPE_MISMATCH",
                "description": "Standard scope describes a different technical domain with negligible semantic overlap.",
                "severity": "FATAL",
                "tender_claim": requirement_text[:120],
                "standard_fact": clean_scope[:120],
            })
            reasons.append({
                "title": "Scope Domain Divergence",
                "description": "Standard scope does not address the required product domain.",
                "is_positive": False,
                "category": "SCOPE",
            })

        return ScopeAnalysisResult(
            match_level=match_level,
            has_exclusion=False,
            has_specific_feature=has_specific_feature,
            specific_feature_name=specific_feature_name,
            positive_snippets=positive_snippets,
            reasons=reasons,
            conflicts=conflicts,
        )

