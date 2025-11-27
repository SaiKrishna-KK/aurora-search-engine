"""
Configuration Management
Centralized configuration using environment variables with sensible defaults.
"""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    # API Configuration
    EXTERNAL_API_BASE_URL: str = os.getenv(
        "EXTERNAL_API_BASE_URL",
        "https://november7-730026606190.europe-west1.run.app"
    )

    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "Aurora Search Engine")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # API Limits
    MAX_QUERY_LENGTH: int = int(os.getenv("MAX_QUERY_LENGTH", "100"))
    MAX_RESULTS_PER_PAGE: int = int(os.getenv("MAX_RESULTS_PER_PAGE", "100"))
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # CORS Settings
    CORS_ENABLED: bool = os.getenv("CORS_ENABLED", "True").lower() == "true"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Timeout Settings
    HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "30"))


# Global settings instance
settings = Settings()
