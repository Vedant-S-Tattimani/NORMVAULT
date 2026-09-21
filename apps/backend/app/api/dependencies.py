"""
FastAPI dependency injectors.
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

# Re-export get_db for cleaner route imports
DatabaseSession = Depends(get_db)
