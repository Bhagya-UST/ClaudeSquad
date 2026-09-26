"""
Configuration management for ReturnIQ
Uses Pydantic for environment validation
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "ReturnIQ"
    APP_ENV: str = "development"  # development, staging, production
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///returniq.db"  # Override in production

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Claude API
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Features
    ENABLE_PII_MASKING: bool = True
    ENABLE_HALLUCINATION_DETECTION: bool = True
    ENABLE_FAIRNESS_CHECKS: bool = True

    # Guardrails
    HALLUCINATION_THRESHOLD: float = 0.01  # 1%
    CONFIDENCE_THRESHOLD: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

def validate_settings() -> bool:
    """Validate critical settings on startup"""
    settings = get_settings()

    required_fields = {
        "DATABASE_URL": "Database connection",
        "JWT_SECRET_KEY": "JWT secret key (change from default in production)",
    }

    if settings.APP_ENV == "production":
        required_fields["ANTHROPIC_API_KEY"] = "Claude API key"

        if settings.JWT_SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError(
                "JWT_SECRET_KEY must be changed from default in production"
            )

    missing = []
    for field, description in required_fields.items():
        value = getattr(settings, field, None)
        if not value or (isinstance(value, str) and value.startswith("dev-")):
            if settings.APP_ENV == "production":
                missing.append(f"  - {description}: {field}")

    if missing:
        raise ValueError(
            f"Missing or invalid production settings:\n" + "\n".join(missing)
        )

    return True
