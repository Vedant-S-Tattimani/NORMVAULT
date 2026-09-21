from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import DatabaseSession
from app.models.standard import StandardEdition, Amendment
from app.models.clause import Clause
from app.schemas.standard import StandardEditionRead, AmendmentRead

# We'll need a simple Clause schema since there wasn't one exported for API yet, or we can just return what we have.
# The user asked for GET /api/v1/editions/{id}/clauses but we might need a quick Pydantic model for it.
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ClauseRead(BaseModel):
    id: int
    clause_number: str
    content: str
    parent_clause_id: Optional[int] = None
    depth: int

    model_config = ConfigDict(from_attributes=True)

router = APIRouter()

@router.get("/{edition_id}", response_model=StandardEditionRead)
def get_edition(edition_id: int, db: Session = DatabaseSession):
    ed = db.query(StandardEdition).filter(StandardEdition.id == edition_id).first()
    if not ed:
        raise HTTPException(status_code=404, detail="Edition not found")
    return ed

@router.get("/{edition_id}/amendments", response_model=List[AmendmentRead])
def get_edition_amendments(edition_id: int, db: Session = DatabaseSession):
    ed = db.query(StandardEdition).filter(StandardEdition.id == edition_id).first()
    if not ed:
        raise HTTPException(status_code=404, detail="Edition not found")
    # Amendments are actually attached to the standard, but we can return ones for this edition or standard.
    # The domain model has edition_id on Amendment.
    amendments = db.query(Amendment).filter(Amendment.edition_id == edition_id).all()
    # Also include amendments directly on the standard if edition_id is null?
    if not amendments:
        amendments = db.query(Amendment).filter(Amendment.standard_id == ed.standard_id).all()
    return amendments

@router.get("/{edition_id}/clauses", response_model=List[ClauseRead])
def get_edition_clauses(edition_id: int, db: Session = DatabaseSession):
    ed = db.query(StandardEdition).filter(StandardEdition.id == edition_id).first()
    if not ed:
        raise HTTPException(status_code=404, detail="Edition not found")
    
    clauses = db.query(Clause).filter(Clause.edition_id == edition_id).all()
    return clauses
