from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = ""  # Must be set via environment variable

    REDIS_URL: Optional[str] = None

    # Email
    # Email (Optional for startup)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = None

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_KEY_2: Optional[str] = None  # Alternative Gemini API key
    GEMINI_API_KEY_3: Optional[str] = None  # Another alternative
    PERPLEXITY_API_KEY: Optional[str] = None

    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "AI Career Advisor"

    JWT_SECRET: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Allow extra fields (like HF specific ones)
    }

settings = Settings()
