"""
Chronological Timeline Builder for Indian Standards lifecycle.
Aggregates publications, reaffirmations, amendments, supersessions, and QCO orders into an ordered event sequence.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard, StandardEdition, Amendment
from app.models.certification import CertificationRequirement
from app.schemas.edition import (
    StandardTimelineEvent,
    StandardHistoryRead,
    EditionRead,
    AmendmentChainItem,
)
from app.services.currentness.amendment_tracker import AmendmentTracker


class StandardTimelineBuilder:
    """
    Constructs chronological lifecycle histories and event streams for a standard family.
    """

    def __init__(self):
        self.amendment_tracker = AmendmentTracker()

    def build_history(self, db: Session, standard_id: int) -> Optional[StandardHistoryRead]:
        """
        Builds the complete historical record and timeline for a standard.
        """
        standard = db.query(IndianStandard).filter(IndianStandard.id == standard_id).first()
        if not standard:
            return None

        events: List[StandardTimelineEvent] = []
        editions_read: List[EditionRead] = []
        total_amendments = 0

        # 1. Process Editions and Amendments
        editions = (
            db.query(StandardEdition)
            .filter(StandardEdition.standard_id == standard.id)
            .order_by(StandardEdition.year.asc())
            .all()
        )

        for ed in editions:
            # Edition Publication Event
            events.append(
                StandardTimelineEvent(
                    year_or_date=str(ed.year),
                    event_type="PUBLICATION",
                    title=f"Publication of Edition {ed.edition_number} ({ed.year})",
                    description=f"Standard edition published for {standard.title}.",
                    evidence=f"Verified entry in BIS standards registry for {standard.standard_number}:{ed.year}.",
                )
            )

            # Reaffirmation Event
            if ed.reaffirmation_year:
                events.append(
                    StandardTimelineEvent(
                        year_or_date=str(ed.reaffirmation_year),
                        event_type="REAFFIRMATION",
                        title=f"Reaffirmation of Edition ({ed.reaffirmation_year})",
                        description=f"Standard reaffirmed by BIS Sectional Committee.",
                        evidence=f"Reaffirmed in {ed.reaffirmation_year}.",
                    )
                )

            # Superseded Event
            if ed.superseded_date or ed.superseded_by_edition_id or ed.superseded_by_standard_number:
                date_str = ed.superseded_date.isoformat() if ed.superseded_date else str(ed.year + 5)
                replacing = ed.superseded_by_standard_number or "revised edition"
                events.append(
                    StandardTimelineEvent(
                        year_or_date=date_str,
                        event_type="SUPERSEDED",
                        title=f"Edition {ed.year} Superseded",
                        description=f"Superseded by {replacing}. {ed.supersession_reason or ''}",
                        evidence=ed.supersession_evidence or f"Superseded by {replacing}.",
                    )
                )

            # Withdrawn Event
            if ed.withdrawal_date or ed.withdrawal_reason:
                date_str = ed.withdrawal_date.isoformat() if ed.withdrawal_date else str(ed.year + 5)
                events.append(
                    StandardTimelineEvent(
                        year_or_date=date_str,
                        event_type="WITHDRAWN",
                        title=f"Edition {ed.year} Officially Withdrawn",
                        description=ed.withdrawal_reason or "Withdrawn by BIS.",
                        evidence=ed.withdrawal_evidence or "Official withdrawal notice in BIS gazette.",
                    )
                )

            # Amendment Events
            amendment_chain = self.amendment_tracker.get_amendment_chain(db, ed.id)
            total_amendments += len(amendment_chain)

            for amd in amendment_chain:
                amd_date = amd.issue_date or amd.effective_date or str(ed.year + 1)
                events.append(
                    StandardTimelineEvent(
                        year_or_date=amd_date,
                        event_type="AMENDMENT",
                        title=f"Amendment No. {amd.amendment_number} ({amd_date})",
                        description=amd.summary,
                        evidence=f"Modifies {amd.affected_clauses or 'standard clauses'}.",
                    )
                )

            editions_read.append(
                EditionRead(
                    id=ed.id,
                    standard_id=ed.standard_id,
                    edition_number=ed.edition_number,
                    year=ed.year,
                    status=str(ed.status.value) if hasattr(ed.status, "value") else str(ed.status),
                    is_current=ed.is_current,
                    reaffirmation_year=ed.reaffirmation_year,
                    superseded_date=ed.superseded_date.isoformat() if ed.superseded_date else None,
                    superseded_by_edition_id=ed.superseded_by_edition_id,
                    superseded_by_standard_number=ed.superseded_by_standard_number,
                    supersession_reason=ed.supersession_reason,
                    supersession_evidence=ed.supersession_evidence,
                    withdrawal_date=ed.withdrawal_date.isoformat() if ed.withdrawal_date else None,
                    withdrawal_reason=ed.withdrawal_reason,
                    withdrawal_evidence=ed.withdrawal_evidence,
                    amendments=amendment_chain,
                    provenance_id=ed.provenance_id,
                )
            )

        # 2. Process QCO Notifications
        certifications = (
            db.query(CertificationRequirement)
            .filter(CertificationRequirement.standard_id == standard.id)
            .all()
        )
        for cert in certifications:
            if cert.is_mandatory_qco:
                qco_date = (
                    cert.notification_date.isoformat()
                    if cert.notification_date
                    else (cert.enforcement_date.isoformat() if cert.enforcement_date else "Gazette Notified")
                )
                events.append(
                    StandardTimelineEvent(
                        year_or_date=qco_date,
                        event_type="QCO_ENFORCED",
                        title=f"Statutory QCO Enforced ({cert.qco_order_number or 'Gazette Order'})",
                        description=f"Mandatory ISI Certification enforced by {cert.notifying_ministry or 'Government of India'}.",
                        evidence=f"Verification: {cert.verification_source or 'Gazette of India'}.",
                    )
                )

        # Sort timeline events chronologically
        events.sort(key=lambda ev: ev.year_or_date)

        return StandardHistoryRead(
            standard_number=standard.standard_number,
            title=standard.title,
            timeline=events,
            editions=editions_read,
            total_amendments=total_amendments,
        )
