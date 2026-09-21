"""
Tests verifying SQLAlchemy domain models, entities, and relationships.
Validates the core domain distinction between Standard, Edition, Amendment, and Reference.
"""

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.standard import IndianStandard, StandardEdition, Amendment, StandardStatus
from app.models.reference import NormativeReference, ReferenceType
from app.models.clause import Clause
from app.models.certification import CertificationRequirement, CertificationScheme


def test_standard_edition_amendment_separation(db_session: Session):
    """
    Validates that a Standard has multiple distinct Editions and Amendments,
    without collapsing them into a generic flat record.
    """
    # Create canonical Indian Standard
    standard = IndianStandard(
        standard_number="IS 4984",
        title="High Density Polyethylene Pipes for Water Supply - Specification",
        scope="Covers requirements for high density polyethylene pipes for water supply.",
        division_code="CED",
        status=StandardStatus.ACTIVE,
        is_mandatory_qco=True,
    )
    db_session.add(standard)
    db_session.commit()
    db_session.refresh(standard)

    assert standard.id is not None

    # Add 4th Edition (1995)
    edition_1995 = StandardEdition(
        standard_id=standard.id,
        edition_number=4,
        year=1995,
        is_current=False,
    )
    # Add 5th Edition (2016)
    edition_2016 = StandardEdition(
        standard_id=standard.id,
        edition_number=5,
        year=2016,
        is_current=True,
        reaffirmation_year=2021,
    )
    db_session.add_all([edition_1995, edition_2016])
    db_session.commit()

    # Add Amendment to Edition 2016
    amendment = Amendment(
        standard_id=standard.id,
        edition_id=edition_2016.id,
        amendment_number=1,
        issue_date=date(2018, 5, 1),
        summary="Amendment No. 1 modifying Clause 5.2 dimensions.",
        affected_clauses="5.2, 5.2.1",
        is_effective=True,
    )
    db_session.add(amendment)
    db_session.commit()

    # Add Normative Reference to Test Method (IS 2530)
    ref = NormativeReference(
        source_standard_id=standard.id,
        target_standard_number="IS 2530",
        relationship_type=ReferenceType.TEST_METHOD,
        referencing_clause="Clause 4.1",
        notes="Methods for test for polyethylene moulding materials and compounds",
    )
    db_session.add(ref)

    # Add Certification Requirement (ISI Mark Scheme I)
    cert = CertificationRequirement(
        standard_id=standard.id,
        scheme=CertificationScheme.ISI_MARK_SCHEME_I,
        is_mandatory_qco=True,
        qco_order_number="S.O. 1885(E)",
        notifying_ministry="Department for Promotion of Industry and Internal Trade",
    )
    db_session.add(cert)
    db_session.commit()

    # Query back and verify relations
    fetched = db_session.scalar(
        select(IndianStandard).where(IndianStandard.standard_number == "IS 4984")
    )
    assert fetched is not None
    assert len(fetched.editions) == 2
    assert len(fetched.amendments) == 1
    assert len(fetched.outgoing_references) == 1
    assert fetched.outgoing_references[0].relationship_type == ReferenceType.TEST_METHOD
    assert len(fetched.certifications) == 1
    assert fetched.certifications[0].is_mandatory_qco is True
