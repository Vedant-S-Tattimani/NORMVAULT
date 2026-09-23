"""
User and Role models for Role-Based Access Control (RBAC) and Audit Provenance.
"""
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    PROCUREMENT_OFFICER = "procurement_officer"
    STANDARDS_AUDITOR = "standards_auditor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    full_name = Column(String(128), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PROCUREMENT_OFFICER)
    department = Column(String(128), default="Procurement & Contracts")
    designation = Column(String(128), default="Executive Engineer")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role.value}')>"
