from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    REDIS_URL: Optional[str] = None

    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: Optional[str] = "no-reply@ai-advisor.local"

    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "AI Career Advisor"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()