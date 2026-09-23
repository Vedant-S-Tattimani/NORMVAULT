"""
Unit tests for JWT Authentication, RBAC Role Guards, and Demo Role Switching.
"""
from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import pytest

from app.main import app
from app.api.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.core.security import create_access_token, decode_access_token, get_password_hash


# Sample test endpoint guarded by RBAC
@app.get("/api/v1/test/auditor-only")
def auditor_only_endpoint(current_user: User = Depends(require_roles([UserRole.STANDARDS_AUDITOR]))):
    return {"status": "ok", "officer": current_user.full_name, "role": current_user.role.value}


@app.get("/api/v1/test/admin-only")
def admin_only_endpoint(current_user: User = Depends(require_roles([UserRole.ADMIN]))):
    return {"status": "ok", "officer": current_user.full_name}


@pytest.fixture
def client():
    return TestClient(app)


def test_token_creation_and_decoding():
    token = create_access_token({
        "sub": "test_officer",
        "role": UserRole.STANDARDS_AUDITOR.value,
        "department": "Bureau of Indian Standards",
    })
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test_officer"
    assert payload["role"] == "standards_auditor"


def test_demo_role_switch(client):
    # Switch to Standards Auditor
    resp = client.post("/api/v1/auth/demo-switch", json={"role": "standards_auditor"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "standards_auditor"
    assert "Dr. S. K. Roy" in data["user"]["full_name"]
    token = data["access_token"]
    assert token is not None

    # Verify /auth/me returns this auditor with the bearer token
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "standards_auditor"


def test_rbac_guard_enforcement(client):
    # 1. Procurement Officer token
    po_token = create_access_token({
        "sub": "procurement_officer",
        "role": UserRole.PROCUREMENT_OFFICER.value,
        "full_name": "Er. Rajesh Kumar",
    })

    # Accessing auditor-only route with PO token must return 403
    forbidden_resp = client.get(
        "/api/v1/test/auditor-only",
        headers={"Authorization": f"Bearer {po_token}"}
    )
    assert forbidden_resp.status_code == 403

    # 2. Standards Auditor token
    auditor_token = create_access_token({
        "sub": "standards_auditor",
        "role": UserRole.STANDARDS_AUDITOR.value,
        "full_name": "Dr. S. K. Roy",
    })

    # Accessing auditor-only route with Auditor token must succeed
    allowed_resp = client.get(
        "/api/v1/test/auditor-only",
        headers={"Authorization": f"Bearer {auditor_token}"}
    )
    assert allowed_resp.status_code == 200
    assert allowed_resp.json()["officer"] == "Dr. S. K. Roy"

    # 3. Admin token has superuser access to all guarded routes
    admin_token = create_access_token({
        "sub": "vigilance_admin",
        "role": UserRole.ADMIN.value,
        "full_name": "Shri A. K. Verma",
    })
    admin_allowed = client.get(
        "/api/v1/test/auditor-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_allowed.status_code == 200
