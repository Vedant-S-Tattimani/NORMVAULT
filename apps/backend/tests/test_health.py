"""
Tests for API root and health diagnostic endpoint.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["status"] == "online"
    assert "/api/v1/health" in data["health_url"]


def test_health_check_returns_200_and_database_ok(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True
    assert "dialect" in data["database"]
    assert "version" in data
    assert "timestamp" in data
