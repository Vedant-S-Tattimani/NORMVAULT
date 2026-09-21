"""
Amendment tracking and clause impact analysis service.
Maintains historical amendment chains and computes clause-level impact without fabricating text.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.standard import StandardEdition, Amendment
from app.models.clause import Clause
from app.schemas.edition import AmendmentChainItem


class AmendmentTracker:
    """
    Manages edition-specific amendment chains and clause modification tracking.
    """

    def get_amendment_chain(self, db: Session, edition_id: int) -> List[AmendmentChainItem]:
        """
        Retrieves the chronological chain of amendments associated with an edition.
        """
        amendments = (
            db.query(Amendment)
            .filter(Amendment.edition_id == edition_id)
            .order_by(Amendment.amendment_number.asc())
            .all()
        )

        chain: List[AmendmentChainItem] = []
        for amd in amendments:
            chain.append(
                AmendmentChainItem(
                    id=amd.id,
                    amendment_number=amd.amendment_number,
                    title=amd.title,
                    issue_date=amd.issue_date.isoformat() if amd.issue_date else None,
                    effective_date=amd.effective_date.isoformat() if amd.effective_date else None,
                    summary=amd.summary,
                    affected_clauses=amd.affected_clauses,
                    old_clause_text=amd.old_clause_text,
                    new_clause_text=amd.new_clause_text,
                    clause_impact_summary=amd.clause_impact_summary,
                    is_effective=amd.is_effective,
                    provenance_id=amd.provenance_id,
                )
            )

        return chain

    def evaluate_clause_impact(
        self, db: Session, edition_id: int, target_clause_number: str
    ) -> List[Dict[str, Any]]:
        """
        Determines whether any amendment modifies a given clause.
        If clause text is unindexed, explicitly states: 'Amendment identified; clause impact not indexed.'
        """
        amendments = (
            db.query(Amendment)
            .filter(Amendment.edition_id == edition_id)
            .order_by(Amendment.amendment_number.asc())
            .all()
        )

        impacts: List[Dict[str, Any]] = []
        target_norm = target_clause_number.strip().lower().replace("clause", "").strip()

        for amd in amendments:
            affected = (amd.affected_clauses or "").lower()
            if target_norm in affected or not amd.affected_clauses:
                # Check whether verified old/new text is indexed
                has_indexed_diff = bool(amd.old_clause_text or amd.new_clause_text)

                if has_indexed_diff:
                    status_text = "Verified clause text diff indexed."
                else:
                    status_text = "Amendment identified; clause impact not indexed."

                impacts.append({
                    "amendment_number": amd.amendment_number,
                    "title": amd.title,
                    "issue_date": amd.issue_date.isoformat() if amd.issue_date else None,
                    "summary": amd.summary,
                    "affected_clauses": amd.affected_clauses,
                    "old_clause_text": amd.old_clause_text,
                    "new_clause_text": amd.new_clause_text,
                    "clause_impact_summary": amd.clause_impact_summary or status_text,
                    "status_note": status_text,
                    "has_indexed_diff": has_indexed_diff,
                    "is_effective": amd.is_effective,
                })

        return impacts
