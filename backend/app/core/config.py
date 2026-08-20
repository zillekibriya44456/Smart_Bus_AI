"""
Application configuration loaded from environment variables.
All secrets and environment-specific values must be set via a .env file or
the shell environment — never hardcoded here.
"""
import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------ App
    PROJECT_NAME: str = "Smart Bus Stop AI"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | production
    LOG_LEVEL: str = "INFO"

    # ------------------------------------------------------------------ CORS
    # Comma-separated origins, e.g. "http://localhost:5173,https://app.example.com"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ------------------------------------------------------------------ Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smartbusstop"

    # ------------------------------------------------------------------ Rate Limiting
    # Format accepted by slowapi: e.g. "60/minute", "1000/hour"
    RATE_LIMIT: str = "60/minute"

    # ------------------------------------------------------------------ Paths
    # BASE_DIR points to the `app/` package directory
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "../../ml/models"))
    DATA_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "../../data/cleaned"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
