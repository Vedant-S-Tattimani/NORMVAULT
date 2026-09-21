"""
Compliance and Reference Semantics Classifier.
Adheres strictly to the core principle:
'Referenced by standard' does NOT equal 'Mandatory for procurement'.
"""

import re
from typing import Optional, Tuple
from app.models.reference import ReferenceType, ReferenceSemantics, ProcurementImpact


class ComplianceClassifier:
    """
    Evaluates source clause wording, relationship types, and conditions to determine
    the precise reference semantics and procurement impact without over-claiming obligation.
    """

    MANDATORY_PHRASES = [
        r"\bshall\s+conform\s+to\b",
        r"\bshall\s+be\s+in\s+accordance\s+with\b",
        r"\bshall\s+comply\s+with\b",
        r"\bshall\s+meet\s+the\s+requirements\s+of\b",
        r"\bmandatory\b",
        r"\bmust\s+conform\b",
    ]

    INFORMATIVE_PHRASES = [
        r"\bmay\s+refer\s+to\b",
        r"\bis\s+recommended\b",
        r"\bfor\s+guidance\b",
        r"\bfor\s+information\b",
        r"\bsee\s+also\b",
        r"\binformative\b",
    ]

    CONDITIONAL_PHRASES = [
        r"\bif\s+(?:the\s+)?(?:equipment|motor|pipe|material|cable|installation)\b",
        r"\bwhere\s+specified\b",
        r"\bwhen\s+required\b",
        r"\bif\s+installed\b",
        r"\bunless\s+otherwise\s+agreed\b",
        r"\bsubject\s+to\b",
    ]

    @classmethod
    def classify_semantics(
        cls,
        clause_content: Optional[str] = None,
        condition_text: Optional[str] = None,
        declared_semantics: Optional[ReferenceSemantics] = None,
    ) -> ReferenceSemantics:
        """Determines whether a reference is NORMATIVE, INFORMATIVE, CONDITIONAL, or UNKNOWN."""
        # 1. If explicit condition text exists, it is conditional
        if condition_text and condition_text.strip():
            return ReferenceSemantics.CONDITIONAL

        # 2. If already declared with high-confidence non-unknown value, preserve it
        if declared_semantics and declared_semantics != ReferenceSemantics.UNKNOWN:
            return declared_semantics

        if not clause_content:
            return ReferenceSemantics.UNKNOWN

        text_lower = clause_content.lower()

        # Check conditional phrases in text
        for pattern in cls.CONDITIONAL_PHRASES:
            if re.search(pattern, text_lower):
                return ReferenceSemantics.CONDITIONAL

        # Check informative phrases in text
        for pattern in cls.INFORMATIVE_PHRASES:
            if re.search(pattern, text_lower):
                return ReferenceSemantics.INFORMATIVE

        # Check mandatory/normative phrases in text
        for pattern in cls.MANDATORY_PHRASES:
            if re.search(pattern, text_lower):
                return ReferenceSemantics.NORMATIVE

        return ReferenceSemantics.UNKNOWN

    @classmethod
    def classify_procurement_impact(
        cls,
        relationship_type: ReferenceType,
        semantics: ReferenceSemantics,
        condition_text: Optional[str] = None,
        declared_impact: Optional[ProcurementImpact] = None,
    ) -> ProcurementImpact:
        """Maps relationship type and semantics to actionable procurement impact."""
        if declared_impact and declared_impact != ProcurementImpact.UNKNOWN:
            return declared_impact

        if semantics == ReferenceSemantics.CONDITIONAL or (condition_text and condition_text.strip()):
            return ProcurementImpact.CONDITIONAL

        if semantics == ReferenceSemantics.INFORMATIVE:
            return ProcurementImpact.INFORMATIONAL

        if semantics == ReferenceSemantics.NORMATIVE:
            if relationship_type == ReferenceType.TEST_METHOD:
                return ProcurementImpact.REQUIRED_TEST
            if relationship_type == ReferenceType.SAFETY_REQUIREMENT:
                return ProcurementImpact.REQUIRED_SAFETY_CONDITION
            if relationship_type == ReferenceType.INSTALLATION_PRACTICE:
                return ProcurementImpact.REQUIRED_INSTALLATION_CONDITION
            if relationship_type in (ReferenceType.NORMATIVE_REFERENCE, ReferenceType.ALLIED_PRODUCT):
                return ProcurementImpact.REQUIRED_SPECIFICATION

        # If semantics is UNKNOWN, default conservatively to UNKNOWN or INFORMATIONAL
        if relationship_type == ReferenceType.TERMINOLOGY:
            return ProcurementImpact.INFORMATIONAL

        return ProcurementImpact.UNKNOWN
