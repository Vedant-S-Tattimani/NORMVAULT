"""
Currentness Analyzer and Precedence Resolution Engine.
Resolves edition currentness, supersession, withdrawal, and procurement warnings
following a strict multi-tiered evidence-first decision priority rule.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard, StandardEdition, EditionStatus, Amendment
from app.models.certification import CertificationRequirement, CertificationCurrentness
from app.schemas.edition import (
    CurrentnessResolutionStatus,
    CurrentnessEvaluation,
    TenderCitationExtraction,
    CitationType,
)
from app.services.currentness.citation_extractor import TenderCitationExtractor
from app.services.currentness.amendment_tracker import AmendmentTracker
from app.services.currentness.supersession_analyzer import SupersessionAnalyzer


class CurrentnessAnalyzer:
    """
    Evaluates currentness of an Indian Standard in the context of a procurement requirement.
    Never equates newest edition with applicable edition.
    """

    def __init__(self):
        self.citation_extractor = TenderCitationExtractor()
        self.amendment_tracker = AmendmentTracker()
        self.supersession_analyzer = SupersessionAnalyzer()

    def evaluate_requirement_currentness(
        self,
        db: Session,
        standard: IndianStandard,
        requirement_text: Optional[str] = None,
        technical_applicability: Optional[str] = "APPLICABLE",
    ) -> CurrentnessEvaluation:
        """
        Evaluates currentness for a standard given optional tender requirement text.
        Follows the strict decision priority hierarchy:
        1. Verified explicit tender citations
        2. Detection of conflicting citations
        3. Handling of unspecified citations
        4. Verified statutory QCO edition mandates
        5. Verified database edition status (Current / Superseded / Withdrawn)
        6. Principled abstention (CURRENTNESS_UNCERTAIN)
        """
        # Step 1: Parse tender text for citations if provided
        extractions: List[TenderCitationExtraction] = []
        if requirement_text:
            raw_ext = self.citation_extractor.extract_citations(requirement_text)
            extractions = self.citation_extractor.detect_conflicts(raw_ext)

        # Find extraction matching this standard family
        matching_ext = self._find_matching_citation(standard.standard_number, extractions)

        # Check for conflicting citations
        if matching_ext and matching_ext.citation_type == CitationType.CONFLICTING:
            return CurrentnessEvaluation(
                status=CurrentnessResolutionStatus.CONFLICTING_EDITION_REFERENCES,
                standard_number=standard.standard_number,
                cited_edition_year=matching_ext.edition_year,
                technical_applicability=technical_applicability,
                edition_applicability="CONFLICTING_REFERENCES",
                evidence_summary="Multiple contradictory edition citations detected in tender specification.",
                procurement_warning="Conflicting edition citations detected in tender clauses. Manual clarification required before tender finalization.",
                provenance_id=standard.provenance_id,
            )

        # Query all indexed editions for this standard
        editions = (
            db.query(StandardEdition)
            .filter(StandardEdition.standard_id == standard.id)
            .order_by(StandardEdition.year.asc())
            .all()
        )

        current_ed = next((e for e in editions if e.status == EditionStatus.CURRENT or e.is_current), None)
        current_year = current_ed.year if current_ed else None

        # Check QCO edition mandate if present
        qco_req = (
            db.query(CertificationRequirement)
            .filter(CertificationRequirement.standard_id == standard.id)
            .first()
        )
        qco_edition_year = qco_req.edition_year if qco_req else None
        qco_is_mandatory = qco_req.is_mandatory_qco if qco_req else standard.is_mandatory_qco

        # If no editions exist in DB or metadata is completely incomplete -> Principled Abstention
        if not editions:
            return CurrentnessEvaluation(
                status=CurrentnessResolutionStatus.CURRENTNESS_UNCERTAIN,
                standard_number=standard.standard_number,
                technical_applicability=technical_applicability,
                edition_applicability="METADATA_UNAVAILABLE",
                evidence_summary="No edition records indexed for standard in knowledge database.",
                procurement_warning="Edition records unavailable in knowledge database. Currentness uncertain.",
                provenance_id=standard.provenance_id,
            )

        # Check if edition was unspecified in tender
        is_unspecified = False
        cited_year = None
        cited_amd = None
        if matching_ext:
            cited_year = matching_ext.edition_year
            cited_amd = matching_ext.amendment_number
            if matching_ext.citation_type == CitationType.UNSPECIFIED_YEAR or not cited_year:
                is_unspecified = True

        # Case A: Edition Unspecified in Tender
        if is_unspecified:
            # Do NOT silently substitute latest edition! Flag as EDITION_UNSPECIFIED
            active_amds = len(current_ed.amendments) if current_ed else 0
            warning_msg = (
                f"Edition not specified in procurement document. Current active edition in BIS registry is {standard.standard_number}:{current_year}."
                if current_year
                else "Edition not specified in procurement document. Active edition could not be verified."
            )
            return CurrentnessEvaluation(
                status=CurrentnessResolutionStatus.EDITION_UNSPECIFIED,
                standard_number=standard.standard_number,
                resolved_edition_year=current_year,
                cited_edition_year=None,
                has_amendments=active_amds > 0,
                active_amendments_count=active_amds,
                qco_edition_match=None,
                qco_edition_mandate=qco_edition_year,
                technical_applicability=technical_applicability,
                edition_applicability="UNSPECIFIED_IN_TENDER",
                evidence_summary="Procurement document cites standard family without edition year.",
                procurement_warning=warning_msg,
                provenance_id=standard.provenance_id,
            )

        # Target year for resolution: either cited year or current year
        target_year = cited_year or current_year

        # Analyze target edition status using SupersessionAnalyzer
        analysis = self.supersession_analyzer.analyze_edition(db, standard.id, target_year)
        target_ed = (
            db.query(StandardEdition)
            .filter(StandardEdition.standard_id == standard.id, StandardEdition.year == target_year)
            .first()
        )

        amendments_count = len(target_ed.amendments) if target_ed else 0
        has_amendments = amendments_count > 0

        # Check QCO edition match
        qco_match = None
        qco_warning = None
        if qco_is_mandatory and qco_edition_year:
            if target_year == qco_edition_year:
                qco_match = True
            else:
                qco_match = False
                qco_warning = f"Statutory QCO specifically mandates Edition {qco_edition_year}. Cited edition {target_year} may not satisfy statutory audit requirements."

        # Case B: Withdrawn
        if analysis["is_withdrawn"]:
            reason = analysis.get("withdrawal_reason") or "Withdrawn by BIS."
            warning_msg = f"Standard edition {target_year} is officially WITHDRAWN. Procurement specifications should not mandate withdrawn standards."
            if qco_warning:
                warning_msg += f" {qco_warning}"

            return CurrentnessEvaluation(
                status=CurrentnessResolutionStatus.WITHDRAWN,
                standard_number=standard.standard_number,
                resolved_edition_year=target_year,
                cited_edition_year=cited_year,
                has_amendments=has_amendments,
                active_amendments_count=amendments_count,
                is_withdrawn=True,
                withdrawal_reason=reason,
                qco_edition_match=qco_match,
                qco_edition_mandate=qco_edition_year,
                technical_applicability=technical_applicability,
                edition_applicability="WITHDRAWN_EDITION",
                evidence_summary=analysis["evidence"],
                procurement_warning=warning_msg,
                provenance_id=standard.provenance_id,
            )

        # Case C: Superseded
        if analysis["is_superseded"]:
            replacing = analysis.get("superseded_by") or "newer edition"
            citation_label = f"{standard.standard_number}:{target_year}" if target_year else standard.standard_number
            warning_msg = f"Procurement document explicitly cites {citation_label}. A newer edition exists ({replacing}). Review required."
            if qco_warning:
                warning_msg += f" {qco_warning}"

            return CurrentnessEvaluation(
                status=CurrentnessResolutionStatus.SUPERSEDED,
                standard_number=standard.standard_number,
                resolved_edition_year=target_year,
                cited_edition_year=cited_year,
                has_amendments=has_amendments,
                active_amendments_count=amendments_count,
                is_superseded=True,
                superseded_by=replacing,
                supersession_reason=analysis.get("supersession_reason"),
                qco_edition_match=qco_match,
                qco_edition_mandate=qco_edition_year,
                technical_applicability=technical_applicability,
                edition_applicability="EXPLICITLY_CITED_SUPERSEDED",
                evidence_summary=analysis["evidence"],
                procurement_warning=warning_msg,
                provenance_id=standard.provenance_id,
            )

        # Case D: Current / Active
        if analysis["status"] == EditionStatus.CURRENT:
            evidence = analysis["evidence"]
            warning_msg = qco_warning

            # Check if specific amendment was cited
            if cited_amd is not None:
                evidence += f" Cited with Amendment {cited_amd}."

            return CurrentnessEvaluation(
                status=CurrentnessResolutionStatus.CURRENT,
                standard_number=standard.standard_number,
                resolved_edition_year=target_year,
                cited_edition_year=cited_year,
                cited_amendment_number=cited_amd,
                has_amendments=has_amendments,
                active_amendments_count=amendments_count,
                qco_edition_match=qco_match,
                qco_edition_mandate=qco_edition_year,
                technical_applicability=technical_applicability,
                edition_applicability="EXPLICITLY_CITED_CURRENT" if cited_year else "RESOLVED_CURRENT",
                evidence_summary=evidence,
                procurement_warning=warning_msg,
                provenance_id=standard.provenance_id,
            )

        # Case E: Unknown / Uncertain
        return CurrentnessEvaluation(
            status=CurrentnessResolutionStatus.CURRENTNESS_UNCERTAIN,
            standard_number=standard.standard_number,
            resolved_edition_year=target_year,
            cited_edition_year=cited_year,
            has_amendments=has_amendments,
            active_amendments_count=amendments_count,
            qco_edition_match=qco_match,
            qco_edition_mandate=qco_edition_year,
            technical_applicability=technical_applicability,
            edition_applicability="CURRENTNESS_UNCERTAIN",
            evidence_summary="Currentness status cannot be verified from active BIS knowledge records.",
            procurement_warning="Official currentness status unverified. Verify with BIS catalog before tender issuance.",
            provenance_id=standard.provenance_id,
        )

    def _find_matching_citation(
        self, standard_number: str, extractions: List[TenderCitationExtraction]
    ) -> Optional[TenderCitationExtraction]:
        """
        Finds the tender citation matching the standard number (ignoring case/whitespace).
        """
        norm_std = standard_number.strip().upper().replace(" ", "")
        for ext in extractions:
            norm_ext = ext.standard_number.strip().upper().replace(" ", "")
            if norm_std == norm_ext or norm_std in norm_ext or norm_ext in norm_std:
                return ext
        return None
