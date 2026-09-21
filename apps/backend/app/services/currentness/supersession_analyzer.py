"""
Supersession and withdrawal analysis service.
Validates supersession chains against verified database provenance without inferring status from publication year alone.
"""

from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard, StandardEdition, EditionStatus, StandardStatus


class SupersessionAnalyzer:
    """
    Analyzes supersession and withdrawal records for Indian Standard editions.
    Enforces clear separation between supersession and withdrawal.
    """

    def analyze_edition(
        self, db: Session, standard_id: int, edition_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyzes the edition status, verifying supersession or withdrawal provenance.
        """
        query = db.query(StandardEdition).filter(StandardEdition.standard_id == standard_id)
        if edition_year:
            edition = query.filter(StandardEdition.year == edition_year).first()
        else:
            # If year unspecified, get current or most recent
            edition = query.filter(StandardEdition.status == EditionStatus.CURRENT).first()
            if not edition:
                edition = query.order_by(StandardEdition.year.desc()).first()

        if not edition:
            return {
                "edition_found": False,
                "status": EditionStatus.UNKNOWN,
                "is_superseded": False,
                "is_withdrawn": False,
                "evidence": "Edition record not found in database.",
            }

        # Check explicit withdrawal
        if edition.status == EditionStatus.WITHDRAWN or edition.withdrawal_date is not None:
            return {
                "edition_found": True,
                "edition_id": edition.id,
                "year": edition.year,
                "status": EditionStatus.WITHDRAWN,
                "is_superseded": False,
                "is_withdrawn": True,
                "withdrawal_date": edition.withdrawal_date.isoformat() if edition.withdrawal_date else None,
                "withdrawal_reason": edition.withdrawal_reason or "Withdrawn by Bureau of Indian Standards.",
                "evidence": edition.withdrawal_evidence or f"Standard edition {edition.year} officially withdrawn.",
            }

        # Check explicit supersession
        if (
            edition.status == EditionStatus.SUPERSEDED
            or edition.superseded_by_edition_id is not None
            or edition.superseded_by_standard_number is not None
            or edition.superseded_date is not None
        ):
            replacing_info = edition.superseded_by_standard_number
            if not replacing_info and edition.superseded_by_edition_id:
                rep_ed = db.query(StandardEdition).filter_by(id=edition.superseded_by_edition_id).first()
                if rep_ed:
                    replacing_info = f"Edition {rep_ed.year}"

            return {
                "edition_found": True,
                "edition_id": edition.id,
                "year": edition.year,
                "status": EditionStatus.SUPERSEDED,
                "is_superseded": True,
                "superseded_by": replacing_info or "Newer verified edition",
                "superseded_date": edition.superseded_date.isoformat() if edition.superseded_date else None,
                "supersession_reason": edition.supersession_reason or "Superseded by revised standard edition.",
                "is_withdrawn": False,
                "evidence": edition.supersession_evidence or f"Verified supersession by {replacing_info}.",
            }

        # Active current edition
        if edition.status == EditionStatus.CURRENT or edition.is_current:
            return {
                "edition_found": True,
                "edition_id": edition.id,
                "year": edition.year,
                "status": EditionStatus.CURRENT,
                "is_superseded": False,
                "is_withdrawn": False,
                "evidence": f"Edition {edition.year} is verified current in BIS catalog.",
            }

        return {
            "edition_found": True,
            "edition_id": edition.id,
            "year": edition.year,
            "status": EditionStatus.UNKNOWN,
            "is_superseded": False,
            "is_withdrawn": False,
            "evidence": "Edition metadata incomplete or unverified.",
        }
