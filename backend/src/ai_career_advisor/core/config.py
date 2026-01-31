from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///D:/Cdac_project/project_02/dev.db"

    REDIS_URL: Optional[str] = None

    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_KEY_2: Optional[str] = None  # Alternative Gemini API key
    GEMINI_API_KEY_3: Optional[str] = None  # Another alternative
    PERPLEXITY_API_KEY: Optional[str] = None

    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "AI Career Advisor"

    JWT_SECRET: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        # Calculate absolute path to .env file
        # This file location: backend/src/ai_career_advisor/core/config.py
        # .env location: backend/.env
        # Need to go up 4 levels: core -> ai_career_advisor -> src -> backend
        
        _current_file = Path(__file__).resolve()
        _backend_dir = _current_file.parent.parent.parent.parent
        env_file = str(_backend_dir / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
