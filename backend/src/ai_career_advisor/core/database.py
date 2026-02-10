from typing import AsyncGenerator

import os
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from sqlalchemy.orm import DeclarativeBase


import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use absolute path for dev.db relative to this file to avoid CWD confusion
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # Points to backend/
DB_PATH = BASE_DIR / "dev.db"
DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Log the database URL being used (masked for security)
if DATABASE_URL:
    masked_url = DATABASE_URL
    if "@" in masked_url:
        # Simple mask: keep protocol, mask credentials
        protocol = masked_url.split("://")[0]
        masked_url = f"{protocol}://****@..."
    logger.info(f"🔌 Connecting to Database: {masked_url}")
else:
    logger.warning("⚠️ No DATABASE_URL found, utilizing default")

# Handle Render's PostgreSQL URL which might start with postgres://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Ensure it uses asyncpg driver
    if "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

logger.info(f"🔧 Using Database URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else '...' }")

# Base class for all orm model
class Base(DeclarativeBase):
    pass

#Async Database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Test connections before using them
    # Render requires SSL for external connections, but internal ones might not.
    # We'll try to let standard libpq rules apply or be permissive if needed.
    # For asyncpg, passing ssl=True or ssl='require' is often needed.
)

#Session Factory 
AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    expire_on_commit = False,
    class_ = AsyncSession
)

#FastAPI Dependency 

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


