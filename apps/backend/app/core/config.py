"""
Core application configuration using Pydantic Settings.
Environment variables override default configuration values.
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "NORMVAULT Standards Intelligence Engine"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database: Default to PostgreSQL; falls back to local SQLite if DATABASE_URL starts with sqlite
    DATABASE_URL: str = "sqlite:///./normvault_dev.db"

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        import json
        try:
            return json.loads(v)
        except Exception:
            return [v]

    # AI & Embedding Providers (Phase 1+)
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # File upload constraints
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
