from sqlalchemy.orm import Session
from app.models.provenance import ProvenanceRecord, SourceType
from app.models.standard import IndianStandard, StandardEdition, StandardStatus, Amendment
from app.models.clause import Clause
from app.models.reference import NormativeReference, ReferenceType
from scripts.ingestion.validators import IngestStandard, IngestClause

def resolve_standard(db_session: Session, data: IngestStandard) -> IndianStandard:
    """
    Ingest or update a standard from validated data.
    Identity strategy: Deduplicate by standard_number.
    """
    # 1. Create or retrieve Provenance
    # We create a new provenance record for the ingestion event
    prov = ProvenanceRecord(
        source_type=SourceType.BIS_PORTAL,
        source_url=data.source_url,
        source_hash=data.source_hash,
        confidence_score=1.0,
        extraction_metadata={"method": "fixture_import"}
    )
    db_session.add(prov)
    db_session.flush()

    # 2. Check for duplicate IndianStandard
    existing_std = db_session.query(IndianStandard).filter_by(standard_number=data.standard_number).first()
    
    if existing_std:
        std = existing_std
        # Update scalar fields
        std.title = data.title
        std.scope = data.scope
        std.division_code = data.division_code
        std.status = StandardStatus(data.status)
        std.is_mandatory_qco = data.is_mandatory_qco
        std.qco_reference = data.qco_reference
        std.provenance_id = prov.id
    else:
        std = IndianStandard(
            standard_number=data.standard_number,
            title=data.title,
            scope=data.scope,
            division_code=data.division_code,
            status=StandardStatus(data.status),
            is_mandatory_qco=data.is_mandatory_qco,
            qco_reference=data.qco_reference,
            provenance_id=prov.id
        )
        db_session.add(std)
    
    db_session.flush()

    # 3. Editions
    for ed_data in data.editions:
        existing_ed = db_session.query(StandardEdition).filter_by(
            standard_id=std.id,
            year=ed_data.year
        ).first()
        
        if existing_ed:
            ed = existing_ed
            ed.edition_number = ed_data.edition_number
            ed.is_current = ed_data.is_current
            ed.provenance_id = prov.id
        else:
            ed = StandardEdition(
                standard_id=std.id,
                edition_number=ed_data.edition_number,
                year=ed_data.year,
                is_current=ed_data.is_current,
                provenance_id=prov.id
            )
            db_session.add(ed)
        db_session.flush()

        # Clauses
        def process_clause(c_data: IngestClause, parent_id=None, depth=0):
            existing_c = db_session.query(Clause).filter_by(
                edition_id=ed.id,
                clause_number=c_data.clause_number
            ).first()
            if existing_c:
                c = existing_c
                c.content = c_data.content
                c.parent_clause_id = parent_id
                c.depth = depth
                c.provenance_id = prov.id
            else:
                c = Clause(
                    edition_id=ed.id,
                    clause_number=c_data.clause_number,
                    content=c_data.content,
                    parent_clause_id=parent_id,
                    depth=depth,
                    provenance_id=prov.id
                )
                db_session.add(c)
            db_session.flush()
            
            for child in c_data.children:
                process_clause(child, parent_id=c.id, depth=depth + 1)
        
        for c_data in ed_data.clauses:
            process_clause(c_data, parent_id=None, depth=0)

        # Amendments
        for am_data in ed_data.amendments:
            existing_am = db_session.query(Amendment).filter_by(
                standard_id=std.id,
                amendment_number=am_data.amendment_number
            ).first()
            if existing_am:
                am = existing_am
                am.summary = am_data.summary
                am.is_effective = am_data.is_effective
                am.provenance_id = prov.id
            else:
                am = Amendment(
                    standard_id=std.id,
                    amendment_number=am_data.amendment_number,
                    summary=am_data.summary,
                    is_effective=am_data.is_effective,
                    provenance_id=prov.id
                )
                db_session.add(am)
            db_session.flush()

    # 4. References
    # Remove old outgoing references for full replace
    db_session.query(NormativeReference).filter_by(source_standard_id=std.id).delete()
    db_session.flush()

    for ref_data in data.normative_references:
        # We don't try to auto-create the target standard; just set target_standard_number
        # If it happens to exist, we could link it, but we can rely on a second pass for linking.
        target_std = db_session.query(IndianStandard).filter_by(standard_number=ref_data.target_standard_number).first()
        target_id = target_std.id if target_std else None

        ref = NormativeReference(
            source_standard_id=std.id,
            target_standard_id=target_id,
            target_standard_number=ref_data.target_standard_number,
            relationship_type=ReferenceType(ref_data.relationship_type),
            referencing_clause=ref_data.referencing_clause,
            provenance_id=prov.id
        )
        db_session.add(ref)

    db_session.commit()
    db_session.refresh(std)
    return std
