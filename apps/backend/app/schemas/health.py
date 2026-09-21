"""
Pydantic schemas for System Health and Diagnostics.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    connected: bool
    dialect: str
    pool_status: str


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Overall health state")
    service: str = Field(description="Name of the service")
    version: str = Field(description="Service release version")
    environment: str = Field(description="Deployment environment (development, staging, production)")
    database: DatabaseHealth = Field(description="Database connectivity metrics")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the health check invocation",
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostic metadata (e.g. pgvector readiness, feature flags)",
    )
