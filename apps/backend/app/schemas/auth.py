"""
Pydantic schemas for Authentication, User Management, and RBAC.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole = UserRole.PROCUREMENT_OFFICER
    department: str = "Procurement & Contracts"
    designation: str = "Executive Engineer"


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class DemoRoleSwitchRequest(BaseModel):
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
