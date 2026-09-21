import json
import argparse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from scripts.ingestion.validators import IngestStandard
from scripts.ingestion.resolvers import resolve_standard

def ingest_file(file_path: str, db_session: Session):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 1. Validate
    validated_data = IngestStandard.model_validate(data)
    
    # 2. Resolve & Persist
    std = resolve_standard(db_session, validated_data)
    print(f"Successfully ingested {std.standard_number}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a JSON standard into the knowledge graph")
    parser.add_argument("file", help="Path to the JSON file")
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        ingest_file(args.file, db)
    finally:
        db.close()
